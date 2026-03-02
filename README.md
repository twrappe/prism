# LLM RAG-Powered CI/CD Failure Analysis Agent

> **Intelligent Root Cause Analysis & Remediation for CI/CD Pipeline Failures**

A sophisticated multi-step LangChain agent that ingests CI/CD failure logs, performs automated Root Cause Analysis (RCA) via LLM reasoning, and surfaces structured remediation suggestions to dramatically reduce time-to-diagnosis in test pipelines.

## 🎯 Project Overview

This system combines **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG)**, and **intelligent agent orchestration** to provide automated, context-aware analysis of CI/CD pipeline failures.

### Key Capabilities

- **🔍 Intelligent RCA**: Automatically identifies root causes from CI/CD failure logs using GPT-4-turbo reasoning
- **📚 Knowledge-Aware Analysis**: Integrates internal documentation through ChromaDB RAG for context-aware diagnosis
- **💡 Actionable Remediation**: Generates prioritized, step-by-step remediation suggestions with success probability estimates
- **⚡ Reduced Time-to-Diagnosis**: From hours of manual investigation to seconds of automated analysis
- **🔐 Structured Output**: JSON-formatted results suitable for integration with monitoring and ticketing systems

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Failure Logs                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   Log Parser & Processor     │
        │  (Parse, validate, extract)  │
        └──────────┬───────────────────┘
                   │
        ┌──────────┴──────────────────────────────┐
        ▼                                         ▼
┌──────────────────┐                  ┌──────────────────────┐
│  RAG Pipeline    │◄─────────────────►│ ChromaDB Vector DB   │
│ (Document Retriev)                  │ (Documentation Index)│
└──────────────────┘                  └──────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│               LangChain Agent Orchestrator                    │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐      ┌───────────────────────────┐ │
│  │   RCA Agent          │      │  Remediation Agent        │ │
│  │  (Root Cause Analysis)      │  (Suggest Fixes)          │ │
│  └──────────┬───────────┘      └────────────┬──────────────┘ │
│             │                               │                │
│             └───────────┬────────────────────┘                │
│                         │                                     │
│             ┌───────────▼──────────────────┐                 │
│             │  GPT-4-Turbo LLM             │                 │
│             │  (Reasoning & Generation)    │                 │
│             └──────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│              Structured Results (JSON)                        │
├──────────────────────────────────────────────────────────────┤
│ • Root Causes                                                │
│ • Failure Chain Analysis                                     │
│ • Affected Components                                        │
│ • Severity & Confidence Score                                │
│ • Prioritized Remediation Steps                              │
│ • Success Probability Estimates                              │
└──────────────────────────────────────────────────────────────┘
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
```

### RCA Analysis Output

```json
{
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

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- pip or poetry for package management

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/llm_rag_powered_qa_agent.git
cd llm_rag_powered_qa_agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key
```

### Basic Usage

```python
from src.agents import CIDDQAAgent
from src.rag import RAGPipeline

# Initialize the agent
rag_pipeline = RAGPipeline()

# Ingest your documentation
rag_pipeline.ingest_documentation([
    "docs/connection_pool_guide.md",
    "docs/test_failure_guide.md"
])

# Create agent and analyze
agent = CIDDQAAgent(rag_pipeline)

# Load failure logs
with open("failure.log", "r") as f:
    log_content = f.read()

# Run analysis
result = agent.analyze_and_remediate(log_content)

# Results contain:
# - result['rca']: Root Cause Analysis details
# - result['remediation_suggestions']: List of fixes
# - result['rag_stats']: RAG system statistics
```

## 📖 Usage Examples

### Example 1: Analyze a CI/CD Failure

```bash
# Run the example analysis script
python examples/analyze_failure.py
```

### Example 2: Ingest Custom Documentation

```bash
# Prepare your documentation files (Markdown format)
mkdir data/documentation
cp my_docs/*.md data/documentation/

# Run the ingestion script
python examples/ingest_docs.py
```

### Example 3: Programmatic Integration

```python
import json
from src.agents import CIDDQAAgent
from src.rag import RAGPipeline

def analyze_pipeline_failure(log_content: str):
    # Setup
    rag = RAGPipeline()
    agent = CIDDQAAgent(rag)
    
    # Analyze
    result = agent.analyze_and_remediate(log_content)
    
    # Export results
    return json.dumps(result, indent=2, default=str)

# Usage
with open("pipeline.log") as f:
    analysis = analyze_pipeline_failure(f.read())
    print(analysis)
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

## 💾 Infrastructure & Deployment

### Database

**ChromaDB Configuration**:
- **Type**: Vector Database
- **Storage**: Persistent (file-based by default)
- **Location**: `./chroma_db` directory
- **Collection**: `ci_cd_docs` (configurable)
- **Scaling**: Suitable for up to 100K documents

### Optional: Production Deployment

```yaml
# Using Docker
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "examples/analyze_failure.py"]

# Using FastAPI (optional API wrapper)
# See examples/api_server.py for REST API implementation
```

### Environment Configuration

Create `.env` file with:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4-turbo
TEMPERATURE=0.7

# RAG Configuration
CHROMA_DB_PATH=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=3

# Logging
LOG_LEVEL=INFO
```

## 📋 Project Structure

```
llm_rag_powered_qa_agent/
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
│   ├── analyze_failure.py   # Main example script
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

- [ ] Web UI for log analysis
- [ ] Integration with Slack/Teams
- [ ] Multi-language log support
- [ ] Historical failure pattern analysis
- [ ] Predictive failure detection
- [ ] Custom LLM model support
- [ ] Distributed processing for large logs
- [ ] Cost optimization recommendations

## 📚 Additional Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [CI/CD Best Practices](./data/documentation/)

---

**Made with ❤️ for DevOps & QA Teams**

For questions or feedback, please open an issue or reach out!
