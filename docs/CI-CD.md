# CI/CD Configuration & Deployment Guide

This document describes the complete CI/CD setup for PRISM.

## Overview

The project includes automated testing, code quality checks, containerization, and deployment pipelines.

### CI/CD Components

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions                           │
├─────────────────────────────────────────────────────────────┤
│ • Test Suite (Python 3.10-3.13 on 3 OS)                     │
│ • Code Linting (Black, isort, Flake8)                       │
│ • Type Checking (mypy)                                     │
│ • Security Scanning (Bandit)                                │
│ • Docker Image Build & Cache                                │
│ • Code Coverage Upload (Codecov)                            │
└─────────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                         │
├─────────────────────────────────────────────────────────────┤
│ • Pre-commit Hooks (Automatic code quality)                 │
│ • Makefile (Convenient commands)                            │
│ • Docker Compose (Local multi-container environment)       │
└─────────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Containerization                          │
├─────────────────────────────────────────────────────────────┤
│ • Dockerfile (Multi-stage build, non-root user)             │
│ • docker-compose.yml (Local dev environment)                │
│ • .dockerignore (Optimized build context)                   │
└─────────────────────────────────────────────────────────────┘
```

## GitHub Actions Workflows

### File: `.github/workflows/ci.yml`

Triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

#### Jobs

##### 1. **Test Job**
- **OS**: Ubuntu, Windows, macOS
- **Python**: 3.10, 3.11, 3.12, 3.13
- **Tasks**:
  - Install dependencies
  - Run pytest with coverage
  - Upload coverage to Codecov

**Key Details**:
```yaml
- Runs on all major OSs (9 combinations)
- Uses caching for faster builds
- Generates coverage reports
- Uploads to Codecov for tracking
```

##### 2. **Lint Job**
- **OS**: Ubuntu only
- **Python**: 3.13
- **Tasks**:
  - Black code formatting check
  - Flake8 linting
  - MyPy type checking

**Key Details**:
```yaml
- Continues on error (non-blocking)
- Max line length: 100 characters
- Ignores whitespace diffs in type hints
```

##### 3. **Security Job**
- **OS**: Ubuntu only
- **Tasks**:
  - Bandit security scanning
  - Generates JSON report

**Key Details**:
```yaml
- Checks for common security issues
- Scans source code only
- Non-blocking (continues on error)
```

##### 4. **Docker Build Job**
- **OS**: Ubuntu only
- **Depends on**: test + lint jobs
- **Tasks**:
  - Setup Docker Buildx
  - Build image with caching
  - Caches via GitHub Actions cache

**Key Details**:
```yaml
- Only builds after tests pass
- Uses layer caching for speed
- Ready for push to registry
```

## Local Development

### Pre-commit Hooks

Installed via: `make pre-commit-install`

**Hooks configured**:
- Trailing whitespace removal
- End of file fixing
- YAML validation
- JSON validation
- Merge conflict detection
- Private key detection
- Black formatting
- isort import sorting
- Flake8 linting
- mypy type checking
- Bandit security checks
- pydocstyle docstring checks

**Setup**:
```bash
pip install pre-commit
make pre-commit-install
```

Pre-commit hooks run automatically before each commit. To run manually:
```bash
make pre-commit-run
```

### Makefile Commands

Available commands via `make`:

```bash
# Help
make help                 # Show all available commands

# Setup
make install             # Install production dependencies
make install-dev         # Install dev dependencies
make pre-commit-install  # Install pre-commit hooks

# Code Quality
make format              # Format code (Black + isort)
make lint                # Run all linters
make pre-commit-run      # Run pre-commit hooks

# Testing
make test                # Run tests
make test-cov            # Run tests with coverage report
make test-fast           # Run tests in parallel
make test-watch          # Watch and re-run tests on changes

# Docker
make docker-build        # Build Docker image
make docker-run          # Run container
make docker-test         # Run tests in Docker
make docker-compose-up   # Start services
make docker-compose-down # Stop services

# Examples
make run-example         # Run analysis example
make run-api             # Start API server
make ingest-docs         # Ingest documents

# Cleanup
make clean               # Clean generated files
```

## Docker

### Dockerfile

**Multi-stage build** for optimized image size:

1. **Builder stage**: Compiles wheels for all dependencies
2. **Runtime stage**: Installs only runtime dependencies

**Features**:
- Python 3.13 slim base image
- Non-root user (appuser)
- Health check command
- Minimal layer size
- Environment variable configuration
- Exposed port 8000 for API

**Build**:
```bash
docker build -t prism:latest .
```

**Run tests**:
```bash
docker run --rm prism:latest pytest tests/ -v
```

**Run API**:
```bash
docker run -it -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  prism:latest python examples/api_server.py
```

### docker-compose.yml

**Services**:
1. `agent` - Main application (runs API server)
2. `chromadb` - Vector database
3. `tests` - Test runner

**Features**:
- Environment variable configuration
- Volume mounting for persistence
- Health checks
- Custom network
- Service dependencies

**Usage**:
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run tests
docker-compose run tests
```

## Code Quality Configuration

### Black (Code Formatter)
- Line length: 100 characters
- Configuration in: Makefile, CI, pre-commit

### isort (Import Sorting)
- Profile: Black compatible
- Line length: 100 characters

### Flake8 (Linter)
- Max line length: 100
- Ignores: E203 (whitespace before ':'), W503 (line break before operators)
- Excludes: tests/

### mypy (Type Checker)
- Ignores missing imports
- Checks source code (excludes tests)
- Configuration in: CI, pre-commit

### Bandit (Security)
- Scans for security issues
- Nonblocking in CI
- Configuration in: pre-commit

## Dependency Management

### Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Production dependencies (pinned versions) |
| `setup.cfg` | Setuptools configuration (matches requirements.txt) |
| `pyproject.toml` | Poetry configuration (reference) |

### Versions

All files are kept in sync:
- langchain: 0.1.9
- langchain-openai: 0.0.8
- langchain-community: 0.0.21
- pydantic: 2.10.3
- openai: 1.13.3
- Python: 3.10+

## Testing in CI/CD

### Test Matrix

```
Python Versions:  3.10, 3.11, 3.12, 3.13
Operating Systems: Ubuntu, Windows, macOS
Total Combinations: 12 test runs per push
```

### Coverage

- Target: ≥ 80% line coverage
- Uploaded to Codecov after each run
- Badge available for README

**Generate locally**:
```bash
make test-cov
# View report in: htmlcov/index.html
```

## Security

### GitHub Secrets

Set these in repository settings:

```
OPENAI_API_KEY        - For tests with API access (optional)
CODECOV_TOKEN         - For Codecov uploads (optional)
DOCKER_USERNAME       - For Docker Hub pushes (optional)
DOCKER_PASSWORD       - For Docker Hub pushes (optional)
```

### Security Checks

1. **Bandit** - Scans for common vulnerabilities
2. **Pre-commit hooks** - Prevent secrets from being committed
3. **Dependency auditing** - Using pip-audit (recommended addition)

## Deployment

### Local Deployment

```bash
# Install locally
make install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
python examples/api_server.py
```

### Docker Deployment

```bash
# Build image
make docker-build

# Run container
make docker-run

# Or use docker-compose
make docker-compose-up
```

### CI/CD Deployment (Recommended for Production)

1. **Push to develop** → CI tests run
2. **All tests pass** → Docker image builds
3. **Merge to main** → (Optional) Deploy to production

## Troubleshooting

### Pre-commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Docker Build Fails

```bash
# Clear build cache
docker system prune -a

# Rebuild
docker build --no-cache -t prism:latest .
```

### Tests Timeout in CI

- Reduce test scope
- Use parallel execution: `pytest -n auto`
- Check for blocking operations

### Codecov Upload Fails

- Optional in CI (continues on error)
- Requires proper token if public repo

## Best Practices

1. **Always run `make lint` before pushing**
   ```bash
   make lint
   ```

2. **Use pre-commit hooks**
   ```bash
   make pre-commit-install
   ```

3. **Test locally with Docker**
   ```bash
   make docker-test
   ```

4. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip-audit  # Find vulnerabilities
   ```

5. **Monitor coverage metrics**
   - Target: ≥ 80%
   - Check Codecov dashboard

6. **Document changes**
   - Update CHANGELOG
   - Reference issue numbers

## Future Enhancements

Recommended additions:

1. **Docker Hub automated builds**
   - Push images to Docker Hub
   - Tag releases

2. **Semantic versioning**
   - Automated version bumping
   - GitHub releases

3. **Integration tests**
   - End-to-end testing
   - API endpoint testing

4. **Performance benchmarks**
   - Track test execution time
   - Monitor memory usage

5. **Artifact uploads**
   - Coverage reports
   - Test results
   - Build artifacts

6. **Dependency scanning**
   - pip-audit for vulnerabilities
   - Dependabot integration

7. **Code quality gates**
   - Require coverage threshold
   - Require lint approval
