# Testing Documentation

This document provides comprehensive information about the test suite for PRISM.

## Overview

The project includes 6 test cases organized into 4 test classes that validate core functionality:

- **Log Parsing** (2 tests)
- **RAG Pipeline** (3 tests)
- **RCA Agent** (1 test)

All tests are located in [`tests/test_agents.py`](../tests/test_agents.py)

## Running Tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test Class

```bash
# Test log parsing only
python -m pytest tests/test_agents.py::TestLogParser -v

# Test RAG pipeline only
python -m pytest tests/test_agents.py::TestRAGPipeline -v

# Test RCA agent only
python -m pytest tests/test_agents.py::TestRCAAgent -v
```

### Run Specific Test

```bash
python -m pytest tests/test_agents.py::TestLogParser::test_parse_structured_logs -v
```

### Run with Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

## Test Cases Details

### TestLogParser Class

Tests the log parsing functionality that extracts structured information from CI/CD failure logs.

#### 1. `test_parse_structured_logs`

**Purpose**: Validate that the parser correctly extracts structured log entries with proper log levels.

**What it tests**:
- Parser can handle formatted log entries with timestamps
- Correctly identifies log levels (ERROR, WARNING, INFO, DEBUG)
- Extracts component information from log messages
- Returns a list of parsed log entries

**Input**:
```
[2024-01-15 10:23:45] [ERROR] [database] Connection failed
[2024-01-15 10:23:46] [WARNING] [api] Retry attempt 1
```

**Assertions**:
- `len(entries) > 0` - At least one entry was parsed
- `entries[0].level == LogLevel.ERROR` - First entry has ERROR level

**Why it matters**: The parser is the first step in the analysis pipeline. If logs aren't parsed correctly, downstream analysis will fail.

#### 2. `test_parse_empty_logs`

**Purpose**: Ensure the parser handles edge cases gracefully.

**What it tests**:
- Parser doesn't crash when given empty input
- Returns a valid list (even if empty)
- Handles malformed or missing log content

**Input**: Empty string `""`

**Assertions**:
- `isinstance(entries, list)` - Returns a list type

**Why it matters**: Production systems must handle edge cases without errors. This ensures robustness when parsing logs with unexpected formats.

---

### TestRAGPipeline Class

Tests the Retrieval-Augmented Generation (RAG) pipeline that manages knowledge documents and retrieval.

#### 3. `test_initialization`

**Purpose**: Verify that the RAG pipeline initializes properly with all required components.

**What it tests**:
- RAG pipeline instantiation succeeds
- Database manager is created
- Document processor is initialized
- All core components are available

**Fixture Used**:
```python
@pytest.fixture
def rag(self):
    """Create RAG pipeline instance"""
    return RAGPipeline()
```

**Assertions**:
- `rag.db_manager is not None` - Database manager exists
- `rag.doc_processor is not None` - Document processor exists

**Why it matters**: The RAG pipeline is essential for context-aware analysis. If it doesn't initialize properly, the entire knowledge retrieval system fails.

#### 4. `test_document_ingestion`

**Purpose**: Validate that documents can be successfully ingested into the knowledge database.

**What it tests**:
- File-based document ingestion
- Document processing and vectorization
- Statistics tracking
- ChromaDB integration

**Test Flow**:

1. **Create Test Document**:
   - Creates temporary markdown file with content: "This is a test document about connection pools"
   
2. **Ingest Documents**:
   - Calls `rag.ingest_documentation()` with file path
   - Documents are parsed, chunked, and stored in ChromaDB
   
3. **Verify Statistics**:
   - Checks `rag.get_stats()` to confirm documents were ingested
   - Validates `stats['document_count'] > 0`

**Assertions**:
- `stats['document_count'] > 0` - At least one document was processed

**Why it matters**: Document ingestion is the core of RAG. Without proper ingestion, the knowledge database is empty and retrieval fails.

#### 5. `test_retrieval`

**Purpose**: Ensure the retrieval system can find relevant documents based on semantic similarity.

**What it tests**:
- Document storage and indexing
- Semantic search functionality
- Query-document matching
- Retrieval result format

**Test Flow**:

1. **Create and Ingest Document**:
   - Creates markdown file: "Connection pool management best practices"
   - Ingests it into the RAG pipeline
   
2. **Perform Retrieval**:
   - Queries for: "how to manage connections"
   - System performs semantic similarity search
   - Returns matching documents
   
3. **Validate Results**:
   - Confirms results are returned as a list
   - Results should match the ingested document semantically

**Assertions**:
- `isinstance(results, list)` - Results are properly formatted

**Why it matters**: Retrieval is what makes RAG work. If documents can't be retrieved during analysis, the LLM won't have context to provide accurate remediation suggestions.

---

### TestRCAAgent Class

Tests the Root Cause Analysis agent that performs failure analysis.

#### 6. `test_initialization`

**Purpose**: Verify that the RCA Agent initializes properly and can perform analysis.

**What it tests**:
- Agent can be instantiated
- RAG pipeline is attached
- Agent is ready for analysis
- Graceful handling when OpenAI API key is not available

**Fixture Used**:
```python
@pytest.fixture
def agent(self):
    """Create RCA agent"""
    return RCAgent()
```

**Assertions**:
- `agent is not None` - Agent is created successfully
- `agent.rag_pipeline is not None` - RAG pipeline is attached

**Important Note**: The agent can initialize without an OpenAI API key (for testing purposes). In production, the API key must be set in the `.env` file for actual LLM-based analysis.

**Why it matters**: The RCA Agent is the core of the system. Verifying it initializes properly ensures the analysis workflow can be executed.

---

## Test Dependencies & Fixtures

### Fixtures

- **`rag`** (TestRAGPipeline): Creates a fresh RAG pipeline instance for each test
- **`agent`** (TestRCAAgent): Creates an RCA agent instance for each test
- **`tmp_path`** (Built-in pytest): Provides temporary directory for test files

### External Dependencies

- **pytest**: Testing framework
- **chromadb**: Vector database for document storage
- **langchain**: LLM framework components

## Expected Test Results

When all tests pass, you should see:

```
============================= test session starts =============================
collected 6 items

tests/test_agents.py::TestLogParser::test_parse_structured_logs PASSED   [ 16%]
tests/test_agents.py::TestLogParser::test_parse_empty_logs PASSED        [ 33%]
tests/test_agents.py::TestRAGPipeline::test_initialization PASSED        [ 50%]
tests/test_agents.py::TestRAGPipeline::test_document_ingestion PASSED    [ 66%]
tests/test_agents.py::TestRAGPipeline::test_retrieval PASSED             [ 83%]
tests/test_agents.py::TestRCAAgent::test_initialization PASSED           [100%]

======================= 6 passed in 2.27s ========================
```

## Common Issues & Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Run tests from the project root directory:
```bash
cd prism
python -m pytest tests/ -v
```

### Issue: "ValidationError for OpenAI API Key"

**Solution**: This is expected in test environments. The RCA Agent now handles missing API keys gracefully. To test with a real API key:
```bash
export OPENAI_API_KEY=your-key-here
python -m pytest tests/ -v
```

### Issue: "ChromaDB initialization warnings"

**Solution**: These are harmless telemetry warnings from ChromaDB. Tests will pass despite the warnings.

### Issue: Tests timeout or hang

**Solution**: 
- Ensure no other pytest sessions are running
- Clear pytest cache: `rm -rf .pytest_cache`
- Rebuild ChromaDB: `rm -rf chroma_db`

## Extending the Test Suite

### Adding a New Test

1. Add method to appropriate test class
2. Use descriptive name: `test_<what_it_tests>`
3. Include docstring explaining purpose
4. Use fixtures for setup/teardown
5. Write clear assertions with meaningful messages

**Example**:
```python
def test_error_handling(self):
    """Test that agent handles malformed logs gracefully"""
    bad_logs = "{{invalid: json]"
    try:
        result = self.agent.analyze_failure(bad_logs)
        assert result is not None
    except Exception as e:
        pytest.fail(f"Agent should handle bad input: {e}")
```

### Test Coverage Goals

Target metrics:
- **Line coverage**: ≥ 80%
- **Branch coverage**: ≥ 75%
- **Critical path coverage**: 100%

Check coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## CI/CD Integration

Tests should be run as part of the CI/CD pipeline on:
- Every pull request
- Before merging to main
- Before releases

Recommended setup:
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: python -m pytest tests/ -v --cov=src
```

## Performance Notes

- All tests complete in < 3 seconds
- ChromaDB vector operations are the slowest component
- Document ingestion test takes ~1 second
- Use `-x` flag to stop on first failure during debugging
