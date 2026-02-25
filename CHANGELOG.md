# Changelog

## [Unreleased]

### Added
- **File picker plugin (`%qfile`)**: New built-in plugin for interactive file/directory selection
  - Syntax: `%qfile` (current directory) or `%qfile:/path/to/dir` (custom path)
  - TUI dialog with Midnight Commander-style blue theme
  - Hides hidden files by default, shows file/directory indicators
  - Auto-registered in plugin autoloader
  - Unit tests: 3 new tests covering pattern matching and autoloading

### Fixed
- Removed unused imports flagged by ruff linter
  - Removed `os` import from `src/gitc/registry.py`
  - Removed `re` import from `tests/test_registry.py`
- Fixed mypy type checking issues in entry_points handling
  - Added proper `type: ignore[arg-type]` directives for compatibility with both old and new importlib.metadata API
- Applied black code formatting to all source files
  - Ensures consistent code style across the project

### Quality Improvements
- All CI checks now pass cleanly:
  - **ruff**: 0 linting errors
  - **black**: All files formatted
  - **mypy**: No type errors
  - **pytest**: 11/11 tests passing ✓
  - **Coverage**: 40% overall (73% registry, 100% context, 100% init)

### Files Changed
- `src/gitc/plugins/file.py` (NEW): File picker plugin implementation
- `src/gitc/registry.py`: Auto-register qfile plugin in `autoload_plugins()`
- `tests/test_registry.py`: Added 3 new tests for qfile plugin
- `.github/workflows/ci.yml`: Configured CI with ruff, black, mypy, pytest+coverage

## [Previous Releases]

See Git history for earlier changes including:
- Branch picker plugin (`%qbranch`)
- Plugin registry system
- Command context system
- Documentation and licensing
