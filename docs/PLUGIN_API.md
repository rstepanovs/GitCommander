# Git Commander – Plugin API

## Philosophy

Plugins must be:

- **Isolated** – No global state
- **Simple** – Single responsibility
- **Independent** – Don't depend on internal modules
- **Forward-compatible** – Work with future versions

---

## Registration Contract

Each plugin must expose a `setup` function:

```python
from gitc.registry import PluginRegistry

def setup(reg: PluginRegistry) -> None:
    """Register plugin rules."""
    reg.register(
        name="my-plugin",
        pattern=r"%my_token",
        handler=my_handler,
    )
```

### Entry Point (for separate packages)

In `pyproject.toml`:

```toml
[project.entry-points."gitc.plugins"]
my_plugin = "my_package:setup"
```

---

## Handler Signature

```python
def handler(match: re.Match[str], context: CommandContext) -> str | list[str]
```

### Parameters

- `match`: Regex match object from pattern
  - Access groups: `match.group(0)`, `match.groupdict()`
- `context`: Execution context
  - `context.cwd`: Current working directory
  - `context.env`: Environment variables
  - `context.debug`: Debug mode flag

### Return Values

| Type | Behavior |
|------|----------|
| `str` | Replaces the token with this value |
| `list[str]` | Expands into multiple arguments |

### Exceptions

| Exception | Meaning |
|-----------|---------|
| `KeyboardInterrupt` | User cancelled, exit code 130 |
| Any other `Exception` | Error message + exit code 2 |

---

## Example: Simple Token

```python
import re
from gitc.registry import PluginRegistry
from gitc.context import CommandContext

def setup(reg: PluginRegistry) -> None:
    reg.register(
        name="current-branch",
        pattern=r"%current",
        handler=get_current_branch,
    )

def get_current_branch(match: re.Match, ctx: CommandContext) -> str:
    import subprocess
    p = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=ctx.cwd,
    )
    return p.stdout.strip()
```

Usage:
```bash
gitc merge %current    # merges branch into current
```

---

## Example: Parameterized Token

```python
import re
from gitc.registry import PluginRegistry

def setup(reg: PluginRegistry) -> None:
    # Match: %qbranch, %qbranch:local, %qbranch:remote
    # Default (no :scope) includes all branches
    reg.register(
        name="qbranch-picker",
        pattern=r"%qbranch(?:\:(?P<scope>local|remote))?",
        handler=pick_branch,
        priority=10,
    )

def pick_branch(match, ctx):
    scope = match.groupdict().get("scope") or "all"
    # ... show UI and return selected branch
```

Usage:
```bash
gitc checkout %qbranch        # All branches (local + remote)
gitc merge %qbranch:local     # Local branches only
gitc rebase %qbranch:remote   # Remote branches only
```

---

## Example: Multi-Result Expansion

```python
def setup(reg: PluginRegistry) -> None:
    reg.register(
        name="modified-files",
        pattern=r"%modified",
        handler=get_modified_files,
    )

def get_modified_files(match, ctx) -> list[str]:
    # Return list of files → expands in command
    return ["file1.py", "file2.py", "file3.py"]
```

Usage:
```bash
gitc add %modified    # expands to: git add file1.py file2.py file3.py
```

---

## Accessing Git Information

**Recommended:** Call `git` as subprocess in handler

```python
import subprocess

def handler(match, ctx) -> str:
    p = subprocess.run(
        ["git", "get-something"],
        cwd=ctx.cwd,
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Git error: {p.stderr}")
    return p.stdout.strip()
```

---

## Priority and Ordering

```python
reg.register(name="plugin1", pattern=r"%foo", handler=h1, priority=10)
reg.register(name="plugin2", pattern=r"%bar", handler=h2, priority=20)
```

Lower priority = processed first.

---

## API Stability

### Current Version: 1

The following interfaces are stable and won't change without major version bump:

- `handler(match: re.Match[str], context: CommandContext) -> str | list[str]`
- `PluginRegistry.register(...)`
- `CommandContext` structure

### Breaking Changes Policy

- Major version bump (1.0 → 2.0) allowed for breaking changes
- Plugins must check version compatibility if needed

---

## Best Practices

✅ **Do**

- Keep handlers simple and fast
- Handle errors gracefully
- Use `ctx.cwd` for commands
- Test with `--debug` flag
- Document your plugin's patterns

❌ **Don't**

- Import internal gitc modules
- Modify `ctx` or `registry`
- Leave processes running
- Assume specific shell environment
- Use relative paths without `cwd`

---

## File Plugin Format

For plugins in `~/.config/gitc/plugins/`:

**File:** `~/.config/gitc/plugins/custom_plugin.py`

```python
from gitc.registry import PluginRegistry

def setup(reg: PluginRegistry) -> None:
    reg.register(name="custom", pattern=r"%custom", handler=my_handler)

def my_handler(match, ctx):
    return "result"
```

Automatically loaded on startup.

---

## Testing Your Plugin

```python
import pytest
from gitc.registry import PluginRegistry
from gitc.context import CommandContext

def test_my_plugin():
    reg = PluginRegistry()
    from my_plugin import setup
    setup(reg)
    
    ctx = CommandContext(cwd="/tmp", env={})
    transformed = reg.transform_argv(["%my_token", "arg2"], ctx)
    
    assert transformed == ["expected_value", "arg2"]
```
