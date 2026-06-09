# Contributing to Sobry Home Assistant Integration

Thank you for your interest in contributing to the Sobry Home Assistant integration! We welcome contributions from everyone.

## 📋 Code of Conduct

This project and everyone participating in it is governed by the [Home Assistant Code of Conduct](https://www.home-assistant.io/code-of-conduct/). By participating, you are expected to uphold this code.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with the following information:

1. **Home Assistant version** (from Settings → System → About)
2. **Integration version** (from HACS or the integration card)
3. **Steps to reproduce** the issue
4. **Expected behavior**
5. **Actual behavior**
6. **Logs** (from Settings → System → Logs, filtered for `sobry`)
7. **Screenshots** (if applicable)

### Suggesting Enhancements

If you have an idea for a new feature or improvement, please open an issue on GitHub with:

1. A clear description of the feature
2. The use case or problem it solves
3. Any relevant examples or mockups

### Submitting Pull Requests

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your changes (e.g., `feature/your-feature` or `fix/your-bugfix`)
4. **Make your changes** following the coding standards below
5. **Test your changes** locally if possible
6. **Commit** your changes with clear, descriptive messages
7. **Push** your branch to GitHub
8. **Open a Pull Request** to the main repository

## 📛 Coding Standards

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints (Python 3.7+)
- Keep line length under 120 characters
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Include comments for complex logic

### Testing

- Add unit tests for new functionality in the `tests/` directory
- Use `pytest` with `pytest-asyncio` for async tests
- Mock external dependencies (e.g., API calls)
- Aim for high test coverage

### Documentation

- Update the `README.md` with any user-facing changes
- Update the `CHANGELOG.md` with your changes
- Keep documentation clear and concise
- Use examples where helpful

### Commits

- Use clear, descriptive commit messages
- Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat: add new feature`
  - `fix: fix a bug`
  - `docs: update documentation`
  - `style: formatting changes`
  - `refactor: code refactoring`
  - `test: add tests`
  - `chore: maintenance tasks`

## 🧪 Development Environment

### Prerequisites

- Python 3.9+
- pip
- virtualenv (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/pierrepinon/sobry-hacs.git
cd sobry-hacs

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements_dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=custom_components/sobry --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest tests/ -v
```

### Linting

```bash
# Run flake8
flake8 custom_components/sobry/

# Run black (code formatter)
black custom_components/sobry/

# Run isort (import sorter)
isort custom_components/sobry/

# Run mypy (type checker)
mypy custom_components/sobry/
```

## 📄 Pull Request Template

When submitting a Pull Request, please use the following template:

```markdown
## Summary

[Brief description of the changes]

## Related Issues

[List any related issues, e.g., Closes #123]

## Changes Made

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Test addition/improvement
- [ ] Other (please describe)

## Testing

[Describe how you tested your changes]

## Screenshots (if applicable)

[Add screenshots showing the changes]

## Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All tests pass
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if needed)
- [ ] No breaking changes
```

## 🎉 Recognition

All contributors will be recognized in the project's contributors list. Significant contributions may receive additional recognition.

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for your contributions! Together, we can make this integration even better.
