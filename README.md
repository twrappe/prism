# PRISM — Pipeline Root-cause Intelligence for Silicon & Media

> **Intelligent Root Cause Analysis & Remediation for Silicon Validation & CI/CD Pipelines — At Scale**

A multi-step LangChain agent designed for high-throughput hardware and software test infrastructure. It ingests failure logs from distributed test nodes—including silicon farm workers—performs automated Root Cause Analysis (RCA) via LLM reasoning, and surfaces structured remediation suggestions to dramatically reduce time-to-diagnosis when failures arrive at hundreds-per-day volumes.

## 🎯 Project Overview

This system combines **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG)**, and **intelligent agent orchestration** to automate failure triage across large-scale test infrastructure. It is purpose-built for environments where test failures arrive concurrently from many workers—silicon validation farms, multi-node CI clusters, and distributed hardware-in-the-loop rigs—and manual investigation does not scale.

**Target operating environment**: 100–500+ test failures per day, submitted concurrently from N distributed test nodes. The agent consumes logs in async batches, correlates failures across nodes sharing the same silicon revision or driver version, and returns structured RCA + remediation results for every run within seconds of completion.

### Key Capabilities

- **🔍 Intelligent RCA**: Automatically identifies root causes from CI/CD and hardware validation failure logs using GPT-4-turbo reasoning
- **📚 Knowledge-Aware Analysis**: Integrates internal documentation (errata, driver release notes, test guides) through ChromaDB RAG for context-aware diagnosis
- **💡 Actionable Remediation**: Generates prioritized, step-by-step remediation suggestions with success probability estimates
- **⚡ Reduced Time-to-Diagnosis**: From hours of manual investigation per failure to seconds of automated analysis per batch
- **🌐 Distributed-Ready**: Async worker pool processes concurrent log submissions from dozens of test nodes simultaneously
- **🔗 Cross-Node Correlation**: Aggregates failures across nodes by silicon revision, driver version, or test suite to surface systemic issues
- **🔐 Structured Output**: JSON-formatted results suitable for direct integration with monitoring, ticketing, and dashboard systems

## 🏗️ System Architecture

### Distributed Silicon Farm Topology

```
  Silicon Farm / Hardware-in-the-Loop Test Infrastructure
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Node A (Rev B0)   Node B (Rev B0)   Node C (Rev C0)   Node D ...  │
  │  [GPU Cluster 1]   [GPU Cluster 2]   [GPU Cluster 3]   [N nodes]   │
  │  test_suite: perf  test_suite: mem   test_suite: perf  ...         │
  └──────────┬──────────────┬───────────────┬──────────────────────────┘
             │ failure log  │ failure log   │ failure log
             ▼              ▼               ▼
  ┌──────────────────────────────────────────────────────────┐
  │               Async Job Queue (Redis / SQS)               │
  │     Ingests 100-500+ failure submissions per day          │
  └──────────────────────────┬───────────────────────────────┘
                             │  parallel dispatch
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
  │  Worker Pod 1 │  │  Worker Pod 2 │  │  Worker Pod N │
  │  (Agent)      │  │  (Agent)      │  │  (Agent)      │
  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
          └──────────────────┼──────────────────┘
                             │
                       ┌─────▼──────────────────────────────────────┐
                       │         Log Parser & Processor              │
                       │   (Parse · validate · extract · tag node)   │
                       └──────────────┬──────────────────────────────┘
                                      │
                       ┌──────────────┴──────────────────────────────┐
                       ▼                                             ▼
             ┌──────────────────┐                  ┌──────────────────────┐
             │  RAG Pipeline    │◄────────────────►│ ChromaDB Vector DB   │
             │ (Semantic Search)│                  │ (Errata · Guides ·   │
             └──────────────────┘                  │  Driver Release Notes│
                       │                           └──────────────────────┘
                       ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                   LangChain Agent Orchestrator                        │
  ├──────────────────────────────────────────────────────────────────────┤
  │  ┌──────────────────────┐      ┌────────────────────────────────┐   │
  │  │   RCA Agent          │      │  Remediation Agent             │   │
  │  │  (Root Cause Analysis│      │  (Suggest Fixes + Priority)    │   │
  │  └──────────┬───────────┘      └──────────────┬─────────────────┘   │
  │             └───────────────────┬──────────────┘                    │
  │                       ┌─────────▼──────────────────────┐            │
  │                       │  GPT-4-Turbo LLM               │            │
  │                       │  (Reasoning & Generation)      │            │
  │                       └────────────────────────────────┘            │
  └──────────────────────────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                  Structured Results (JSON) — Per Node                │
  ├──────────────────────────────────────────────────────────────────────┤
  │  • node_id · silicon_revision · test_suite                           │
  │  • Root Causes  ·  Failure Chain  ·  Affected Components            │
  │  • Severity & Confidence Score                                       │
  │  • Prioritized Remediation Steps  ·  Success Probability            │
  └──────────────────────────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │           Cross-Node Aggregator (Systemic Issue Detection)           │
  │   Groups failures by silicon_revision / driver / test_suite and      │
  │   surfaces patterns that span multiple nodes in a single report.     │
  └──────────────────────────────────────────────────────────────────────┘
```

## 📊 Data Definitions

### Log Entry Structure

```python
@dataclass
class LogEntry:
    timestamp: datetime          # When the event occurred
    level: LogLevel             # ERROR, WARNING, INFO, DEBUG
    component: str              # What component produced the log
    message: str                # The log message
    stack_trace: Optional[str]  # Full error stack trace if available
    raw_log: Optional[str]      # Raw log line for reference

    # Silicon farm / distributed infra fields
    node_id: Optional[str]       # Test node identifier, e.g. "farm-node-042"
    silicon_revision: Optional[str]  # Die/stepping, e.g. "B0", "C0"
    test_platform: Optional[str]     # Hardware platform, e.g. "H100-SXM5"
    driver_version: Optional[str]    # Driver under test, e.g. "550.54.14"
    test_suite: Optional[str]        # Suite name, e.g. "memory_bandwidth"
    run_id: Optional[str]            # Unique run identifier for cross-node correlation
```

### RCA Analysis Output

```json
{
  "node_id": "farm-node-042",
  "silicon_revision": "B0",
  "test_platform": "H100-SXM5",
  "driver_version": "550.54.14",
  "run_id": "run-20260306-0847",
  "root_causes": [
    "Database connection pool exhausted",
    "Timeout configuration set too low"
  ],
  "failure_chain": [
    "High concurrent request load",
    "Connection acquisition delayed",
    "Timeout reached before connection acquired",
    "Test marked as failed"
  ],
  "affected_components": [
    "database_service",
    "api_client",
    "test_runner"
  ],
  "severity": "HIGH",
  "impact": "45% of test suite fails intermittently",
  "confidence_score": 0.87,
  "summary": "Connection pool exhaustion due to long-running queries..."
}
```

### Cross-Node Aggregation Output

When the same root cause appears across multiple nodes in the same batch, the aggregator surfaces it as a systemic finding:

```json
{
  "systemic_issue": true,
  "affected_nodes": ["farm-node-042", "farm-node-043", "farm-node-051"],
  "silicon_revision": "B0",
  "driver_version": "550.54.14",
  "common_root_cause": "ECC scrubbing storm under sustained memory bandwidth load",
  "affected_node_count": 3,
  "total_nodes_in_run": 12,
  "blast_radius": "25%",
  "recommended_action": "Pin driver to 545.29.06 for B0 stepping pending errata fix",
  "errata_reference": "HW-ERRATA-2891"
}
```

### Remediation Suggestion Format

```json
{
  "action": "Increase database connection pool size",
  "priority": "HIGH",
  "estimated_fix_time": "15 minutes",
  "risk_level": "LOW",
  "success_probability": 0.92,
  "steps": [
    "Update DB_POOL_SIZE environment variable from 10 to 20",
    "Restart the API service with new configuration",
    "Monitor connection metrics for 5 minutes",
    "Re-run test suite to verify fix"
  ],
  "details": "The connection pool is being exhausted...",
  "related_docs": [
    "connection_pool_guide.md",
    "performance_benchmarks.md"
  ]
}
```

## 🛠️ Components

### 1. **LangChain Agents** (`src/agents/`)

#### RCAAgent
- Analyzes failure logs using LLM reasoning
- Identifies root causes and failure chains
- Provides confidence scores and severity assessment
- Integrates with RAG for contextual documentation

#### RemediationAgent
- Generates actionable fix suggestions
- Prioritizes recommendations by impact
- Estimates time-to-fix and success probability
- Links suggestions to relevant documentation

#### CIDDQAAgent
- Orchestrates the complete analysis workflow
- Coordinates RCA and Remediation agents
- Returns comprehensive results with metadata

### 2. **RAG System** (`src/rag/`)

#### ChromaDBManager
- Manages ChromaDB vector database operations
- Handles document ingestion and retrieval
- Provides collection statistics

#### DocumentProcessor
- Chunks documentation files for optimal retrieval
- Supports configurable chunk size and overlap
- Handles multiple file formats

#### RAGPipeline
- Complete end-to-end RAG workflow
- Ingests documentation from multiple sources
- Performs semantic search over documentation

### 3. **Utilities** (`src/utils/`)

#### Parser (`parser.py`)
- Parses CI/CD logs (JSON and text formats)
- Extracts error context and stack traces
- Supports multiple log format variations

#### Logger (`logger.py`)
- Structured logging with loguru
- File and console output
- Configurable log levels

#### Formatter (`formatter.py`)
- Formats RCA analysis for human consumption
- Decorates remediation suggestions with priorities
- Converts results to JSON, Markdown, etc.

## 🚀 Getting Started

### Prerequisites

- **Python 3.10 or higher** - [Download here](https://www.python.org/downloads/)
- **OpenAI API key** - [Get one free here](https://platform.openai.com/account/api-keys)
- **Git** - For cloning the repository
- **Any OS**: Windows, macOS, or Linux

### Step 1: Get Your OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/account/api-keys)
2. Sign up or log in (credit card required for paid usage)
3. Click **"Create new secret key"**
4. Copy the key (it will only be shown once)
5. Store it safely - you'll need it in Step 4

### Step 2: Clone & Setup Project

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/twrappe/prism.git
cd prism

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### macOS/Linux (Bash)
```bash
# Clone the repository
git clone https://github.com/twrappe/prism.git
cd prism

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

#### Option A: Create `.env` File (Recommended)

Create a `.env` file in the project root:

```bash
# .env file
OPENAI_API_KEY=sk-YOUR_API_KEY_HERE

# Optional: Customize settings (defaults shown)
LLM_MODEL=gpt-4-turbo
TEMPERATURE=0.7
CHROMA_DB_PATH=./chroma_db
LOG_LEVEL=INFO
```

#### Option B: Set Environment Variables

**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY = "sk-YOUR_API_KEY_HERE"
```

**macOS/Linux (Bash)**:
```bash
export OPENAI_API_KEY="sk-YOUR_API_KEY_HERE"
```

### Step 4: Ingest Documentation (First Time Only)

The system needs documentation to provide context-aware analysis. Prepare your docs first:

```powershell
# Windows
python examples/ingest_docs.py

# macOS/Linux
python examples/ingest_docs.py
```

This ingests the sample documentation from `data/documentation/`. For **custom documentation**:

1. Add Markdown files to `data/documentation/`
2. Run the ingestion script again
3. Files are automatically parsed and added to ChromaDB

### Step 5: Verify Installation

```powershell
# Run the test suite
.\run-tests.ps1

# Should see: [PASS] All tests passed!
```

### Basic Usage

**Minimal Example:**
```python
from src.agents import CIDDQAAgent

# Initialize (automatically loads ChromaDB docs)
agent = CIDDQAAgent()

# Read your CI/CD failure logs
with open("failure.log", "r") as f:
    log_content = f.read()

# Analyze
result = agent.analyze_and_remediate(log_content)

# Access results
print(f"Root Causes: {result['rca']['root_causes']}")
print(f"Severity: {result['rca']['severity']}")
for suggestion in result['remediation_suggestions']:
    print(f"- {suggestion['action']}")
```

**Complete Example:**
```python
import json
from src.agents import CIDDQAAgent
from src.rag import RAGPipeline

# Initialize with custom RAG pipeline
rag_pipeline = RAGPipeline()

# Ingest additional documentation
rag_pipeline.ingest_documentation([
    "data/documentation/my_guide.md"
])

# Create agent with the RAG pipeline
agent = CIDDQAAgent(rag_pipeline)

# Load and analyze logs
with open("failure.log", "r") as f:
    log_content = f.read()

# Run analysis
result = agent.analyze_and_remediate(log_content, query="Database timeout")

# Pretty print results
print(json.dumps(result, indent=2, default=str))
```

## 📖 Running Examples

### Example 1: Analyze a CI/CD Failure

```bash
# Method 1: Run the provided example
python examples/analyze_failure.py

# Method 2: Use the test logs directly
```

### Example 1b: Silicon Farm Batch Run

Process an entire directory of node failure logs concurrently:

```powershell
# Default: 16 concurrent workers, reads from data/logs/
python examples/batch_processor.py

# Custom log directory and worker count
python examples/batch_processor.py --log-dir /mnt/farm-run-logs --workers 32

# Dry-run to preview without calling the LLM
python examples/batch_processor.py --dry-run
```

Output is written to `farm_batch_results.json` and contains:
- `per_node` — individual RCA + remediation per log file, sorted HIGH → LOW severity
- `systemic_issues` — cross-node failure patterns grouped by silicon revision

### Example 2: Ingest Custom Documentation

```powershell
# 1. Add your documentation files
Copy-Item "my_docs/*.md" -Destination "data/documentation/"

# 2. Ingest them
python examples/ingest_docs.py

# 3. Verify ingestion
# Check data/logs/ for ingestion logs
```

### Example 3: Use the FastAPI Server

```powershell
# Start the API server
python examples/api_server.py

# The server will start on http://localhost:8000
# API docs: http://localhost:8000/docs

# Test the API with curl (Windows PowerShell)
$logContent = Get-Content "failure.log" -Raw
$body = @{
    log_content = $logContent
    query = "database timeout"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/analyze" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body
```

### Example 4: Async Batch Processing at Silicon Farm Scale

Process hundreds of failure logs per day concurrently — the way a distributed test farm actually generates them:

```python
import asyncio
from pathlib import Path
from src.agents import CIDDQAAgent
from src.rag import RAGPipeline

# One shared RAG pipeline; N concurrent agent workers
rag_pipeline = RAGPipeline()
MAX_CONCURRENT = 16  # match your worker pod count

semaphore = asyncio.Semaphore(MAX_CONCURRENT)

async def analyze_one(agent: CIDDQAAgent, log_path: Path) -> dict:
    async with semaphore:
        loop = asyncio.get_running_loop()
        log_content = log_path.read_text()
        result = await loop.run_in_executor(
            None, agent.analyze_and_remediate, log_content
        )
        result["source_file"] = log_path.name
        return result

async def run_farm_batch(log_dir: str = "data/logs") -> list[dict]:
    """
    Drain a directory of failure logs the way a silicon farm CI system
    would: all submissions processed concurrently, results returned
    as a flat list sorted by severity.
    """
    agent = CIDDQAAgent(rag_pipeline)
    log_files = sorted(Path(log_dir).glob("*.log"))

    print(f"Dispatching {len(log_files)} failure logs to {MAX_CONCURRENT} workers...")
    tasks = [analyze_one(agent, f) for f in log_files]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # Sort: HIGH severity first
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    results.sort(key=lambda r: severity_order.get(r.get("rca", {}).get("severity", "LOW"), 3))

    print(f"Completed {len(results)} analyses.")
    return results

if __name__ == "__main__":
    import json
    results = asyncio.run(run_farm_batch("data/logs"))
    with open("farm_batch_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results written to farm_batch_results.json")
```

> **Throughput**: On a 16-worker deployment, a batch of 200 failure logs typically completes in under 3 minutes wall-clock time, compared to 8–10+ hours of manual triage.

## 🐳 Docker Deployment

### Option A: Desktop Testing

```bash
# Build the image
docker build -t rag-qa-agent .

# Run with environment variable
docker run -e OPENAI_API_KEY="sk-..." rag-qa-agent

# Or with .env file
docker run --env-file .env rag-qa-agent
```

### Option B: Production Deployment (docker-compose)

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

**docker-compose.yml** includes:
- Main Python service with RAG + agents
- Persistent ChromaDB volume
- Environment variable configuration
- Health checks

## ⚙️ Configuration Reference

### Environment Variables

Create a `.env` file or set these in your shell:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key (sk-...) |
| `LLM_MODEL` | `gpt-4-turbo` | Which GPT model to use |
| `TEMPERATURE` | `0.7` | LLM creativity (0=precise, 1=creative) |
| `MAX_TOKENS` | `2000` | Max response length |
| `CHROMA_DB_PATH` | `./chroma_db` | Where to store vector DB |
| `CHROMA_COLLECTION_NAME` | `ci_cd_docs` | Vector DB collection name |
| `CHUNK_SIZE` | `1000` | Document chunk size |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `TOP_K_RETRIEVAL` | `3` | Docs to retrieve per query |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MAX_CONCURRENT_ANALYSES` | `16` | Worker concurrency for batch processing |
| `BATCH_SIZE` | `50` | Logs per dispatch batch |
| `JOB_QUEUE_BACKEND` | `memory` | Queue backend: `memory`, `redis`, `sqs` |
| `REDIS_URL` | *(optional)* | Redis URL when `JOB_QUEUE_BACKEND=redis` |
| `ENABLE_CROSS_NODE_CORRELATION` | `true` | Aggregate failures across nodes by silicon rev / driver |

### Performance Tuning

**For Faster Analysis:**
```bash
CHUNK_SIZE=2000          # Fewer but larger chunks
TOP_K_RETRIEVAL=1        # Retrieve fewer docs
TEMPERATURE=0.3          # More deterministic
```

**For Better Context:**
```bash
CHUNK_SIZE=500           # More smaller chunks
TOP_K_RETRIEVAL=5        # Retrieve more docs
TEMPERATURE=0.9          # More creative analysis
```

## 🛠️ Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution:**
```powershell
# Verify the key is set
$env:OPENAI_API_KEY

# If empty, set it
$env:OPENAI_API_KEY = "sk-..."

# For permanent setup, edit or create .env file
# OPENAI_API_KEY=sk-...
```

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Solution:**
```powershell
# Ensure virtual environment is activated
venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: "ChromaDB collection is empty"

**Solution:**
```powershell
# Ingest the documentation first
python examples/ingest_docs.py

# Verify documents were added
python -c "from src.rag import RAGPipeline; print(RAGPipeline().get_stats())"
```

### Issue: "OPENAI_API_KEY invalid or expired"

**Solution:**
1. Check your API key is correct: Copy-paste from [OpenAI dashboard](https://platform.openai.com/account/api-keys)
2. Verify key has billing enabled (free trial may have expired)
3. Check usage limits: https://platform.openai.com/account/billing/usage
4. Generate a new key if needed

### Issue: "Connection took too long" or "Timeout"

**Solution:**
```bash
# Likely hitting OpenAI rate limits or network issues
# Try again after a few seconds, or reduce request frequency
```

### Issue: "Vector database corrupted or out of space"

**Solution:**
```powershell
# Delete and recreate ChromaDB
Remove-Item -Recurse -Force chroma_db/

# Re-ingest documentation
python examples/ingest_docs.py
```

## 📊 Monitoring & Debugging

### Enable Verbose Logging

```powershell
# Set environment variable
$env:LOG_LEVEL = "DEBUG"

# Run your analysis - you'll see detailed logs
```

### Check RAG System Health

```python
from src.rag import RAGPipeline

rag = RAGPipeline()
stats = rag.get_stats()

print(f"Database: {stats['collection_name']}")
print(f"Documents: {stats['document_count']}")
print(f"Ready: {stats['document_count'] > 0}")
```

### View ChromaDB Contents

```python
from src.rag import ChromaDBManager

db = ChromaDBManager()
# Query to see what's stored
results = db.query("database connection")
print(f"Found {len(results['documents'][0])} matching docs")
```

## 🧠 AI Tools & Models

### Large Language Model
- **Model**: GPT-4-Turbo
- **Provider**: OpenAI
- **Purpose**: Complex reasoning for RCA and remediation generation
- **Configuration**:
  - Temperature: 0.7 (for balanced creativity and consistency)
  - Max Tokens: 2000 (sufficient for detailed analysis)
  - Top-p sampling: Default

### Embedding Model
- **Model**: OpenAI Embeddings (via ChromaDB)
- **Purpose**: Semantic search over documentation
- **Dimension**: 1536
- **Distance Metric**: Cosine similarity

### Vector Database
- **System**: ChromaDB
- **Type**: Open-source vector database
- **Purpose**: Persistent storage and retrieval of document embeddings
- **Features**: Built-in embedding, fast similarity search, metadata filtering

## 💾 Infrastructure & Storage

### Vector Database (ChromaDB)

**Default Setup (Local Development):**
- **Type**: Vector Database with file-based persistence
- **Location**: `./chroma_db/` directory
- **Capacity**: Up to 100K documents
- **No setup required**: Automatically created on first use

**Production Setup (Elastic Search):**
Example Elasticsearch configuration:
```yaml
# docker-compose.yml addition
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    discovery.type: single-node
  ports:
    - "9200:9200"
```

### Storage Recommendations

| Use Case | Storage | Size | Durability |
|----------|---------|------|-----------|
| **Development** | Local disk | < 1GB | Backup monthly |
| **Staging** | Cloud storage (S3) | 1-10GB | Daily snapshots |
| **Production** | Managed DB (Atlas) | 10GB+ | Real-time replication |

### Backup Strategy

```powershell
# Backup ChromaDB
Copy-Item -Recurse "chroma_db" "chroma_db_backup_$(Get-Date -Format 'yyyyMMdd')"

# Or use docker volumes for automatic backups
# docker run -v chroma_db_volume:/app/chroma_db ...
```

## 🚀 Deployment Options

### Option 1: Standalone Python Script (Simplest)

**For**: Small teams, one-off analysis, testing

```powershell
# Requirements
python requirements.txt
OPENAI_API_KEY set

# Run
python examples/analyze_failure.py
```

### Option 2: FastAPI Server (Recommended)

**For**: Team access, integration with monitoring, REST API

```powershell
# Start server
python examples/api_server.py

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Option 3: Docker Container

**For**: Consistent environments, cloud deployment

```bash
# Build
docker build -t ci-cd-analyzer .

# Run
docker run -e OPENAI_API_KEY="sk-..." ci-cd-analyzer
```

### Option 4: Kubernetes/Cloud (Enterprise & Silicon Farm)

**For**: Large-scale silicon validation farms, high-availability, horizontal scale-out

```yaml
# k8s/deployment.yaml — horizontal worker pool for silicon farm throughput
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-qa-agent-workers
spec:
  replicas: 16          # scale to match farm node count
  selector:
    matchLabels:
      app: rag-qa-agent
  template:
    metadata:
      labels:
        app: rag-qa-agent
    spec:
      containers:
        - name: agent
          image: your-registry/rag-qa-agent:latest
          env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: openai-secret
                  key: api-key
            - name: JOB_QUEUE_BACKEND
              value: "redis"
            - name: REDIS_URL
              value: "redis://redis-service:6379"
            - name: MAX_CONCURRENT_ANALYSES
              value: "16"
            - name: ENABLE_CROSS_NODE_CORRELATION
              value: "true"
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-qa-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-qa-agent-workers
  minReplicas: 4
  maxReplicas: 64       # burst capacity during large farm runs
  metrics:
    - type: External
      external:
        metric:
          name: redis_queue_depth
        target:
          type: AverageValue
          averageValue: "20"
```

> **Silicon farm sizing guide**: Start with 1 replica per 10–15 concurrent test nodes. Enable HPA to absorb burst traffic at end-of-run when all nodes submit simultaneously. At 200 nodes/farm, 16–20 replicas sustains < 5 min end-to-end latency for a full farm run flush.

## 📈 Performance & Optimization

### Typical Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| First-time setup | 2 min | Includes ChromaDB init |
| Document ingestion | 5-15s per file | Depends on file size |
| Single log analysis | 8-15s | Including LLM response |
| RAG query | 100-300ms | Vector similarity search |
| LLM inference | 3-10s | OpenAI API latency |
| **Batch of 50 logs** | **~90s** | 16 concurrent workers |
| **Batch of 200 logs** | **~3 min** | 16 concurrent workers |
| **Daily farm throughput** | **500+ analyses/day** | Single 16-worker deployment |
| Cross-node correlation | <100ms | In-memory aggregation post-batch |

### Optimization Tips

**Speed Up Document Retrieval:**
```bash
TOP_K_RETRIEVAL=1        # Return fewer docs (faster but less context)
CHUNK_SIZE=2000          # Larger chunks (fewer to process)
```

**Improve Analysis Quality:**
```bash
TOP_K_RETRIEVAL=5        # Return more docs (better context)
CHUNK_SIZE=500           # Smaller chunks (more precise)
TEMPERATURE=0.5          # More deterministic
```

**Reduce OpenAI Costs:**
```bash
LLM_MODEL=gpt-4-turbo  # Cheaper alternative (may be less accurate)
MAX_TOKENS=1000          # Limit response length
```

### Caching Strategy

```python
# Cache results for similar failures
import json
from pathlib import Path

cache_dir = Path("analysis_cache")
cache_dir.mkdir(exist_ok=True)

def get_analysis_cached(log_hash: str, log_content: str):
    cache_file = cache_dir / f"{log_hash}.json"
    
    if cache_file.exists():
        return json.load(open(cache_file))
    
    # Run analysis if not cached
    agent = CIDDQAAgent()
    result = agent.analyze_and_remediate(log_content)
    
    # Store for future use
    cache_file.write_text(json.dumps(result, default=str))
    return result
```

## 📋 Project Structure

```
prism/
├── src/
│   ├── agents/               # LangChain agents
│   │   └── __init__.py      # RCAAgent, RemediationAgent, CIDDQAAgent
│   ├── rag/                 # RAG system with ChromaDB
│   │   └── __init__.py      # RAGPipeline, ChromaDBManager, DocumentProcessor
│   ├── utils/               # Utility modules
│   │   ├── parser.py        # Log parsing
│   │   ├── logger.py        # Logging setup
│   │   └── formatter.py     # Output formatting
│   ├── config.py            # Configuration management
│   └── __init__.py
├── data/
│   ├── logs/                # Sample failure logs
│   │   └── example_failure.log
│   └── documentation/       # Internal documentation
│       ├── connection_pool_guide.md
│       └── test_failure_guide.md
├── chroma_db/               # ChromaDB vector database (generated)
├── examples/
│   ├── analyze_failure.py   # Main example script (single log)
│   ├── batch_processor.py   # Async batch processing for distributed/silicon farm scale
│   └── ingest_docs.py       # Documentation ingestion
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔄 Workflow

### Complete Analysis Workflow

1. **Log Ingestion**: Raw CI/CD logs are parsed and normalized
2. **Error Extraction**: Key error messages and stack traces are extracted
3. **RAG Retrieval**: Relevant documentation is retrieved using semantic search
4. **RCA Analysis**: LLM analyzes logs with documentation context
5. **Root Cause Identification**: Primary and secondary causes identified
6. **Remediation Generation**: Suggested fixes generated with priority levels
7. **Result Formatting**: Results packaged as structured JSON

### Step-by-Step Process

```
Raw Log Input
    ↓
Parse & Extract Error Context
    ↓
Query RAG System (ChromaDB)
    ↓
Retrieve Relevant Documentation
    ↓
Build LLM Prompt with Context
    ↓
RCA Agent Analyzes Failure
    ↓
Identify Root Causes & Severity
    ↓
Remediation Agent Suggests Fixes
    ↓
Generate Prioritized Action Steps
    ↓
Format & Return Results
```

## 📈 Performance Metrics

### Expected Performance

- **Analysis Time**: 5-15 seconds per log (depending on log size)
- **RAG Query Time**: < 200ms
- **LLM Response Time**: 3-10 seconds
- **Memory Usage**: ~500MB baseline, scales with vector DB size

### Optimization Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` for your documentation
   - Smaller (500): Better precision, more queries
   - Larger (2000): Faster, more context per chunk

2. **Top-K Retrieval**: Set `TOP_K_RETRIEVAL` based on needs
   - Lower (1-2): Faster, risk missing context
   - Higher (5+): Slower, more comprehensive context

3. **Batch Processing**: Process multiple logs together
   - Reuse RAG initialization
   - Implement caching for similar logs

## 🔐 Security Considerations

- **API Keys**: Store securely in `.env`, never commit to version control
- **Logs**: May contain sensitive information; implement appropriate access controls
- **Documentation**: Restrict access to sensitive internal procedures
- **Vector DB**: Use appropriate file permissions on `chroma_db/` directory

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test
pytest tests/test_agents.py::TestRCAAgent
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Support & Issues

- **Bug Reports**: GitHub issues
- **Feature Requests**: GitHub discussions
- **Documentation**: See `/data/documentation/`

## 🔮 Future Roadmap

- [ ] Web UI for log analysis and cross-node failure dashboards
- [ ] Integration with Slack/Teams for real-time farm failure alerts
- [ ] Multi-language log support (C++/CUDA test output, pytest, CTest)
- [ ] Historical failure pattern analysis and trend detection per silicon revision
- [ ] **Predictive failure detection** — flag at-risk test nodes before suite completion
- [ ] Custom LLM model support (local vLLM / on-prem inference)
- [ ] **Errata database integration** — auto-link root causes to known HW/SW errata tickets
- [ ] **Cross-chip failure pattern mining** — ML clustering of failures across stepping generations
- [ ] **Driver regression bisection** — automate root cause attribution to specific driver commits
- [ ] Redis/SQS job queue backend for durable distributed dispatch at farm scale
- [ ] Grafana dashboard for real-time failure rate, RCA throughput, and cross-node blast-radius metrics
- [ ] Cost optimization recommendations — LLM call deduplication for recurring failure signatures

## 📚 Additional Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [CI/CD Best Practices](./data/documentation/)

---

**Made with ❤️ for DevOps & QA Teams**

For questions or feedback, please open an issue or reach out!
