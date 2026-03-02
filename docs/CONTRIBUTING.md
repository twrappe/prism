# Contributing Guide

Thank you for interest in contributing to the LLM RAG-Powered CI/CD Failure Analysis Agent!

## Getting Started

### 1. Fork the Repository

Click "Fork" on the GitHub repository to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/yourusername/llm_rag_powered_qa_agent.git
cd llm_rag_powered_qa_agent
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Setup

### Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### Code Style

We follow PEP 8 standards with Black formatting.

```bash
# Format code
black src/ examples/ tests/

# Check linting
flake8 src/ examples/ tests/

# Type checking
mypy src/
```

## Making Changes

### File Structure

- **src/agents/**: LangChain agents
- **src/rag/**: RAG system with ChromaDB
- **src/utils/**: Utility modules
- **examples/**: Example scripts
- **tests/**: Unit tests
- **data/**: Sample data and documentation
- **docs/**: Documentation files

### Adding Features

1. Create feature branch
2. Write tests first (TDD approach preferred)
3. Implement feature
4. Ensure all tests pass
5. Add documentation
6. Submit pull request

### Adding Documentation

1. Update relevant markdown files
2. Add docstrings to code
3. Include examples in docstrings
4. Update README.md if needed

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

### Writing Tests

```python
import pytest
from src.agents import RCAAgent

class TestRCAAgent:
    @pytest.fixture
    def agent(self):
        return RCAAgent()
    
    def test_initialization(self, agent):
        assert agent.llm is not None
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**: feat, fix, docs, style, refactor, test, chore
**Scope**: agents, rag, utils, config, etc.
**Subject**: Brief description (imperative, lowercase)

**Example**:
```
feat(agents): add confidence score validation

Added validation logic to ensure RCA confidence scores
are between 0 and 1. Includes comprehensive tests.

Closes #123
```

### Commit Best Practices

- Make small, focused commits
- One feature/fix per commit
- Include tests with code changes
- Write clear commit messages
- Reference issues when applicable

## Pull Request Process

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**:
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in PR template

3. **PR Description** should include:
   - What changes were made
   - Why they were made
   - How to test the changes
   - Any breaking changes
   - Related issues

4. **Wait for Review**:
   - Maintainers will review
   - Address feedback
   - Ensure CI checks pass

## Code Review Guidelines

### For Contributors

- Be open to feedback
- Respond promptly to comments
- Make requested changes
- Thank reviewers

### For Reviewers

- Be respectful and constructive
- Provide clear explanations
- Suggest improvements
- Approve when satisfied

## Areas for Contribution

### High Priority
- [ ] Web UI for log analysis
- [ ] Slack/Teams integration
- [ ] Cost optimization features
- [ ] Performance improvements

### Medium Priority
- [ ] Additional log format support
- [ ] Expanded documentation
- [ ] Example scripts
- [ ] Test coverage improvements

### Low Priority
- [ ] Documentation improvements
- [ ] Code refactoring
- [ ] Code style enhancements

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error logs/screenshots

**Template**:
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: 
- Python version:
- Package versions:
```

### Feature Requests

Include:
- Use case/motivation
- Proposed solution
- Alternative solutions
- Potential impact

## Community Guidelines

- Be respectful and inclusive
- Welcome diverse perspectives
- Help others learn
- Attribute ideas and work
- Focus on the code, not the person

## Getting Help

- Check existing issues and discussions
- Read documentation thoroughly
- Ask in discussions before opening issues
- Join community chat/forums

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

All contributors will be recognized in the project README.

---

Thank you for contributing! Your help makes this project better. 🙏
