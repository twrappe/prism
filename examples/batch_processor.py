#!/usr/bin/env python3
"""
Async batch processor for silicon farm / distributed test infrastructure.

Designed for environments that generate 100-500+ failure logs per day across
multiple test nodes (e.g., GPU silicon validation farms). All submissions are
processed concurrently via an asyncio worker pool, then aggregated to surface
systemic issues that span multiple nodes.

Usage
-----
    # Process all .log files in data/logs/ with default worker count
    python examples/batch_processor.py

    # Point at a specific directory and override worker count
    python examples/batch_processor.py --log-dir /mnt/farm-logs --workers 32

    # Dry-run to see what would be dispatched without calling the LLM
    python examples/batch_processor.py --dry-run
"""

import asyncio
import json
import sys
import argparse
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import CIDDQAAgent
from src.rag import RAGPipeline
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Per-log analysis
# ---------------------------------------------------------------------------

def _analyze_one_sync(rag_pipeline: RAGPipeline, log_content: str) -> dict:
    """
    Run analysis in a thread-pool worker.

    A fresh CIDDQAAgent is constructed per call so that concurrent threads
    never share mutable LangChain chain state.
    """
    agent = CIDDQAAgent(rag_pipeline)
    return agent.analyze_and_remediate(log_content)


async def analyze_one(
    rag_pipeline: RAGPipeline,
    log_path: Path,
    semaphore: asyncio.Semaphore,
) -> dict:
    """Run a single log through a fresh agent under the concurrency semaphore."""
    async with semaphore:
        loop = asyncio.get_running_loop()
        log_content = log_path.read_text(encoding="utf-8", errors="replace")

        # Extract optional node metadata embedded in the log filename.
        # Expected convention: <node_id>__<silicon_rev>__<suite>.log
        # e.g.  farm-node-042__B0__memory_bandwidth.log
        parts = log_path.stem.split("__")
        node_id = parts[0] if len(parts) > 0 else log_path.stem
        silicon_rev = parts[1] if len(parts) > 1 else "unknown"
        test_suite = parts[2] if len(parts) > 2 else "unknown"

        logger.info(f"Analyzing {log_path.name} | node={node_id} rev={silicon_rev}")

        # run_in_executor with return_exceptions-style wrapper so a single
        # OpenAI error does not abort the whole batch.
        try:
            result = await loop.run_in_executor(
                None, _analyze_one_sync, rag_pipeline, log_content
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Analysis failed for {log_path.name}: {exc}")
            result = {"error": str(exc), "rca": {}, "remediation_suggestions": []}

        result.update(
            {
                "source_file": log_path.name,
                "node_id": node_id,
                "silicon_revision": silicon_rev,
                "test_suite": test_suite,
            }
        )
        return result


# ---------------------------------------------------------------------------
# Cross-node aggregation
# ---------------------------------------------------------------------------

def correlate_across_nodes(results: list[dict]) -> list[dict]:
    """
    Group per-node results by (silicon_revision, common root-cause token) and
    surface systemic findings where ≥ 2 nodes share the same failure signature.

    Returns a list of systemic-issue dicts, sorted by affected_node_count desc.
    """
    # Map: (silicon_rev, first_root_cause) -> list of node results
    buckets: dict[tuple, list] = defaultdict(list)

    for r in results:
        rev = r.get("silicon_revision", "unknown")
        causes = r.get("rca", {}).get("root_causes", [])
        key = (rev, causes[0] if causes else "unknown")
        buckets[key].append(r)

    systemic: list[dict] = []
    for (rev, cause), group in buckets.items():
        if len(group) < 2:
            continue
        systemic.append(
            {
                "systemic_issue": True,
                "silicon_revision": rev,
                "common_root_cause": cause,
                "affected_nodes": [r["node_id"] for r in group],
                "affected_node_count": len(group),
                "test_suites": list({r.get("test_suite") for r in group}),
                "max_severity": max(
                    (r.get("rca", {}).get("severity", "LOW") for r in group),
                    key=lambda s: {"HIGH": 2, "MEDIUM": 1, "LOW": 0}.get(s, 0),
                ),
            }
        )

    systemic.sort(key=lambda x: x["affected_node_count"], reverse=True)
    return systemic


# ---------------------------------------------------------------------------
# Main batch runner
# ---------------------------------------------------------------------------

async def run_batch(log_dir: str, max_workers: int, dry_run: bool) -> dict:
    log_path = Path(log_dir)
    log_files = sorted(log_path.glob("*.log"))

    if not log_files:
        logger.warning(f"No .log files found in {log_dir}")
        return {"per_node": [], "systemic_issues": []}

    logger.info(
        f"Dispatching {len(log_files)} failure logs | "
        f"workers={max_workers} | dry_run={dry_run}"
    )

    if dry_run:
        for f in log_files:
            logger.info(f"  [dry-run] would process: {f.name}")
        logger.info(f"Dry-run: {len(log_files)} file(s) found in {log_dir}")
        return {"per_node": [], "systemic_issues": [], "dry_run": True, "listed_count": len(log_files)}

    rag_pipeline = RAGPipeline()

    # Ingest documentation once; all workers share this index
    docs_dir = Path(__file__).parent.parent / "data" / "documentation"
    doc_files = [str(f) for f in docs_dir.glob("*.md")]
    if doc_files:
        rag_pipeline.ingest_documentation(doc_files)

    semaphore = asyncio.Semaphore(max_workers)

    # Process in chunks of batch_size to cap peak memory from in-flight futures.
    chunk_size = settings.batch_size
    per_node_results: list[dict] = []
    for i in range(0, len(log_files), chunk_size):
        chunk = log_files[i : i + chunk_size]
        logger.info(
            f"Batch {i // chunk_size + 1}: dispatching {len(chunk)} logs "
            f"(files {i + 1}–{i + len(chunk)} of {len(log_files)})"
        )
        tasks = [analyze_one(rag_pipeline, f, semaphore) for f in chunk]
        chunk_results = await asyncio.gather(*tasks)
        per_node_results.extend(chunk_results)

    # Sort single-node results by severity
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    per_node_results.sort(
        key=lambda r: severity_rank.get(r.get("rca", {}).get("severity", "LOW"), 3)
    )

    systemic_issues = correlate_across_nodes(per_node_results)

    if systemic_issues:
        logger.warning(
            f"SYSTEMIC ISSUES DETECTED: {len(systemic_issues)} cross-node failure "
            f"pattern(s) found — review systemic_issues in output."
        )

    return {"per_node": per_node_results, "systemic_issues": systemic_issues}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Async batch processor for silicon farm failure logs"
    )
    parser.add_argument(
        "--log-dir",
        default=str(Path(__file__).parent.parent / "data" / "logs"),
        help="Directory containing .log files to process",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=settings.max_concurrent_analyses,
        help=f"Concurrent worker count (default: {settings.max_concurrent_analyses})",
    )
    parser.add_argument(
        "--output",
        default="farm_batch_results.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be processed without calling the LLM",
    )
    args = parser.parse_args()

    # Remove stale output file before starting so a failed run never leaves
    # results that look current.
    output_path = Path(args.output)
    if output_path.exists() and not args.dry_run:
        output_path.unlink()
        logger.info(f"Removed previous output: {output_path}")

    results = asyncio.run(run_batch(args.log_dir, args.workers, args.dry_run))

    if results.get("dry_run"):
        n_listed = results.get("listed_count", 0)
        logger.info(
            f"Dry-run complete: {n_listed} file(s) would be dispatched. "
            f"Remove --dry-run to execute analyses."
        )
        return

    n_per_node = len(results["per_node"])
    n_systemic = len(results["systemic_issues"])
    logger.info(f"Completed: {n_per_node} analyses, {n_systemic} systemic issue(s).")

    output_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    logger.info(f"Results written to {output_path}")


if __name__ == "__main__":
    main()
