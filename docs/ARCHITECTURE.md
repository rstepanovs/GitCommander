# Git Commander – Architecture

## Overview

Git Commander (gitc) is a pluggable command-line preprocessor for Git.

It intercepts command-line arguments, expands special tokens (e.g. `%qbranch`),
and then executes the resulting `git` command.

---

## Core Flow

1. User runs:

    gitc checkout %qbranch

2. Engine parses argv
3. PluginRegistry scans arguments
4. Matching plugin handler is invoked
5. Token is replaced with result
6. Final command is executed:

   git checkout feature/my-branch

---

## Core Components

### 1. GitCommander
Entry point of the application.
Responsible for:
- argument parsing
- plugin loading
- invoking registry
- executing git

---

### 2. PluginRegistry

Responsibilities:
- registering plugin rules
- storing regex patterns
- transforming argv
- prioritizing rules

---

### 3. Plugin Rule

Each rule defines:

- name
- regex pattern
- handler(match, context)
- priority

Example:

```python
reg.register(
    name="qbranch-picker",
    pattern=r"%qbranch(?:\:(?P<scope>local|remote))?",
    handler=handle_branch,
    priority=10,
)


4. CommandContext

Contains:

cwd

environment

debug flag

Passed to plugin handlers.

Design Principles

No magic

Deterministic behavior

No hidden state

Explicit token activation

Plugin isolation

Future Extensions

Inline replacement inside strings

Multi-token expansion

Plugin config file

Remote plugin registry

Shell integration



---

# 📁 2️⃣ `PLUGIN_API.md`

```markdown
# Git Commander – Plugin API

## Philosophy

Plugins must be:
- isolated
- simple
- dependency-independent from internal modules
- forward-compatible

---

## Registration Contract

Each plugin must expose:

```python
def setup(reg: PluginRegistry) -> None:
    ...

And register via entry point:

[project.entry-points."gitc.plugins"]
my_plugin = "my_package:setup"

Handler Signature
def handler(match: re.Match, context: CommandContext) -> str | list[str]

Return:

str → replaces token

list[str] → expands into multiple arguments

Raise:

KeyboardInterrupt → cancel command

Exception → abort with error

Example: Branch Picker
def setup(reg):
    reg.register(
        name="branch-picker",
        pattern=r"%branch",
        handler=handle_branch
    )
API Stability

PLUGIN_API_VERSION = 1

Future major versions must preserve:

handler signature

context object

registration mechanism

Breaking changes → major version bump.



---

# 📁 3️⃣ `ROADMAP.md`

```markdown
# Git Commander – Roadmap

## v0.1 – Core Engine

- PluginRegistry
- Autoload via entry points
- Basic `%branch`
- --dry-run
- --debug
- Tests for registry

---

## v0.2 – Token Expansion Enhancements

- Inline replacement
- Multiple token support
- Multi-result expansion
- Conflict detection

---

## v0.3 – UX Improvements

- Fuzzy search
- Theming
- Config file
- Plugin enable/disable

---

## v1.0 – Stable API

- Plugin API freeze
- Full documentation
- Example plugins repository
- CI pipeline
- Typed public API


