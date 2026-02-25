# Contributing to Git Commander

Thank you for your interest in contributing to Git Commander! This document explains how to contribute effectively.

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're building this together.

---

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/gitc.git
cd gitc
```

### 2. Set Up Development Environment

```bash
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
pytest
```

---

## Development Principles

✅ **Keep Architecture Clean**

- No hidden magic or implicit behavior
- Explicit over implicit
- Clear separation of concerns

✅ **Plugin API Stability**

- Don't break plugin contracts
- Major version bump for breaking changes
- Maintain backward compatibility

✅ **Type Safety**

- Add type hints to all public APIs
- Run `mypy` regularly:
  ```bash
  mypy src/gitc
  ```

✅ **Test Coverage**

- Add tests for new features
- Aim for >90% coverage
- Test both happy path and errors

---

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-feature
git checkout -b fix/my-bug
```

### 2. Make Changes

Keep commits atomic and focused.

### 3. Run Tests and Linting

```bash
pytest
mypy src/gitc
black src/gitc tests
ruff check src/gitc tests
```

### 4. Add Tests

If adding a feature:

```python
# tests/test_my_feature.py
def test_my_feature():
    # Arrange
    # Act
    # Assert
```

### 5. Submit PR

Include:
- Description of change
- Motivation / use case
- Related issues
- Test coverage

---

## Pull Request Guidelines

- **Title:** Clear and concise (`[core] Add feature X`, `[plugins] Fix plugin Y`)
- **Description:** Explain what and why
- **Tests:** Must pass CI
- **Type hints:** Required for public APIs
- **Documentation:** Update docs if needed

---

## Code Style

### Format with Black

```bash
black src/gitc tests
```

### Lint with Ruff

```bash
ruff check src/gitc tests
```

### Type Check with MyPy

```bash
mypy src/gitc
```

---

## Plugin Development

For plugin contributions:

1. Keep logic simple and focused
2. Follow handler signature:
   ```python
   def handler(match: re.Match, ctx: CommandContext) -> str | list[str]
   ```
3. Include docstrings
4. Add tests in plugin package
5. Document the plugin pattern

---

## Reporting Issues

### Bug Report

Include:
- OS and Python version
- gitc version
- Steps to reproduce
- Expected vs actual behavior
- Full error output with `--debug`

### Feature Request

Include:
- Use case motivating the request
- Proposed syntax (if applicable)
- Example usage

---

## Documentation

### Updating Docs

- `docs/ARCHITECTURE.md` – System design (core changes)
- `docs/PLUGIN_API.md` – Plugin interface (plugin changes)
- `docs/ROADMAP.md` – Planning
- README.md – User-facing

### Writing Style

- Clear and concise
- Code examples included
- Avoid jargon where possible

---

## Commit Message Format

```
[track] Brief summary (50 chars max)

Optional: Longer description explaining the change.
- What was done
- Why it was done
- Any related issues (#123)
```

**Tracks:** `core`, `plugins`, `docs`, `packaging`, `legal`

Example:
```
[core] Add plugin priority system

Allows plugins to define execution order via priority parameter.
Enables deterministic token expansion for multiple matching patterns.

Fixes #42
```

---

## Release Process

Only maintainers handle releases, but here's the process:

1. Prepare release branch: `release/v0.2.0`
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md`
4. Create GitHub release
5. Build and upload to PyPI
6. Merge back to main

---

## Questions?

- Check existing issues
- Ask on GitHub Discussions (future)
- Comment on relevant issue

---

## Recognition

Contributors are credited in:
- CONTRIBUTORS file
- GitHub contributors page
- Release notes

Thank you for contributing! 🙏
