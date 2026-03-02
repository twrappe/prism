.PHONY: help install install-dev test lint format clean run docker-build docker-run pre-commit-install pre-commit-run

help:
	@echo "LLM RAG-Powered CI/CD Failure Analysis Agent - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install dependencies"
	@echo "  make install-dev          Install development dependencies"
	@echo "  make pre-commit-install   Install pre-commit hooks"
	@echo ""
	@echo "Development:"
	@echo "  make format               Format code with black and isort"
	@echo "  make lint                 Run linters (flake8, mypy)"
	@echo "  make test                 Run tests with pytest"
	@echo "  make test-cov             Run tests with coverage report"
	@echo "  make pre-commit-run       Run pre-commit hooks manually"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-run           Run Docker container"
	@echo "  make docker-test          Run tests in Docker"
	@echo "  make docker-compose-up    Start services with docker-compose"
	@echo "  make docker-compose-down  Stop docker-compose services"
	@echo ""
	@echo "Other:"
	@echo "  make clean                Clean up generated files"
	@echo "  make run-example          Run example analysis"

# Installation targets
install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-xdist
	pip install black isort flake8 mypy
	pip install bandit pydocstyle
	pip install pre-commit

pre-commit-install:
	pre-commit install

# Code quality targets
format:
	black src tests examples --line-length 100
	isort src tests examples --profile black --line-length 100

lint:
	@echo "Running Black check..."
	black --check src tests --line-length 100
	@echo "Running isort check..."
	isort --check-only src tests --profile black --line-length 100
	@echo "Running Flake8..."
	flake8 src tests --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running mypy..."
	mypy src --ignore-missing-imports

pre-commit-run:
	pre-commit run --all-files

# Testing targets
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

test-fast:
	pytest tests/ -v -n auto

test-watch:
	pytest-watch tests/ -v

# Docker targets
docker-build:
	docker build -t llm-rag-qa-agent:latest .

docker-run:
	docker run -it --rm \
		-e OPENAI_API_KEY=${OPENAI_API_KEY} \
		-v $(PWD)/chroma_db:/app/chroma_db \
		-v $(PWD)/data:/app/data \
		llm-rag-qa-agent:latest

docker-test:
	docker build -f Dockerfile -t llm-rag-qa-agent:test .
	docker run --rm llm-rag-qa-agent:test pytest tests/ -v

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

# Example targets
run-example:
	python examples/analyze_failure.py

run-api:
	python examples/api_server.py

ingest-docs:
	python examples/ingest_docs.py

# Cleanup targets
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov coverage.xml .coverage
	@echo "Cleanup complete"
