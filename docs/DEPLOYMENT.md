# Deployment Guide

## Prerequisites

- Python 3.10+
- Git
- Docker (optional)
- OpenAI API key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/twrappe/prism.git
cd prism
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n ci_cd_agent python=3.10
conda activate ci_cd_agent
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required Configuration**:
```env
OPENAI_API_KEY=sk-your-key-here
```

## Quick Start

### Option 1: Basic Usage

```bash
python examples/analyze_failure.py
```

### Option 2: Using as a Module

```python
from src.agents import CIDDQAAgent
from src.rag import RAGPipeline

# Initialize
rag = RAGPipeline()
agent = CIDDQAAgent(rag)

# Analyze
result = agent.analyze_and_remediate(log_content)
print(result)
```

### Option 3: FastAPI Server

```bash
python examples/api_server.py
```

Then access the API at `http://localhost:8000`

## Docker Deployment

### Build Image

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "examples/analyze_failure.py"]
```

Build and run:

```bash
docker build -t ci-cd-agent .
docker run --env-file .env ci-cd-agent
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ci-cd-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ci-cd-agent
  template:
    metadata:
      labels:
        app: ci-cd-agent
    spec:
      containers:
      - name: agent
        image: ci-cd-agent:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secrets
              key: api-key
        - name: CHROMA_DB_PATH
          value: /data/chroma_db
        volumeMounts:
        - name: chroma-volume
          mountPath: /data/chroma_db
      volumes:
      - name: chroma-volume
        persistentVolumeClaim:
          claimName: chroma-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: chroma-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## Custom Deployment

### 1. Prepare Documentation

Place your documentation in `data/documentation/`:
```
data/documentation/
├── api_guide.md
├── database_guide.md
└── test_framework.md
```

### 2. Ingest Documentation

```bash
python examples/ingest_docs.py
```

### 3. Run Analysis

```bash
python examples/analyze_failure.py
```

## Production Considerations

### Database Persistence
- Configure persistent storage for `chroma_db/`
- Implement backup strategy
- Monitor database size

### Logging
- Set `LOG_LEVEL=WARNING` for production
- Implement log aggregation
- Set up log rotation

### Performance
- Set `TOP_K_RETRIEVAL=3` for optimal performance
- Adjust `CHUNK_SIZE` based on documentation length
- Monitor OpenAI API usage

### Cost Management
- Set API key spending limits
- Monitor usage and costs
- Cache similar analyses

### Security
- Use environment variables for sensitive data
- Implement API authentication
- Validate input logs
- Sanitize outputs

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Statistics

```bash
curl http://localhost:8000/stats
```

### Logging

Check logs at `data/logs/app.log`

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Verify `.env` file exists and contains valid API key

### Issue: "ChromaDB connection failed"
**Solution**: Ensure `chroma_db/` directory exists and is writable

### Issue: "No documents found in RAG"
**Solution**: Run `python examples/ingest_docs.py` to ingest documentation

### Issue: Slow analysis
**Solutions**:
- Reduce `TOP_K_RETRIEVAL`
- Use smaller `CHUNK_SIZE`
- Check OpenAI API latency
- Increase system resources

## Maintenance

### Regular Tasks
- Monitor API costs
- Review log files for errors
- Update dependencies monthly
- Backup ChromaDB regularly

### Updates
```bash
# Get latest
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart service
systemctl restart ci-cd-agent
```

## Support
For issues or questions, please refer to the main README.md or open a GitHub issue.
