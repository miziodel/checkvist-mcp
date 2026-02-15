---
title: Agent Testing Workflow
created: 2026-02-14
status: active
---

# Agent Testing Workflow

## Context
This document describes the established workflow for running tests in this project when working with AI agents (specifically Antigravity on macOS).

## The Challenge
AI agents running in sandboxed environments (like Antigravity) cannot directly execute Python commands from virtual environments due to macOS security restrictions (SIP/TCC).

### Technical Root Cause
- **Sandbox Blocking**: The agent's process cannot access `.pyc` files in `__pycache__/` directories
- **Path Resolution**: `realpath()` calls on `.venv/bin/` fail with `Operation not permitted`
- **Binary Creation**: `pip install` of packages with `.so` files is blocked

## Established Workflow

### 1. Test Execution (User)
The user manually runs tests from their terminal:

```bash
source .venv/bin/activate
pytest
```

### 2. Result Analysis (Agent)
The agent:
- Reads test output from terminal history
- Identifies failing tests
- Analyzes stack traces
- Proposes fixes

### 3. Fix Implementation (Agent)
The agent:
- Modifies test files or source code
- Documents changes
- Requests user to re-run tests

### 4. Verification (User)
The user runs `pytest` again to verify fixes.

## Why This Works
- **Security**: No need to grant "Full Disk Access" to the agent
- **Simplicity**: User maintains full control over test execution
- **Effectiveness**: Agent can still analyze and fix issues based on output

## Alternative Approaches (Not Recommended)

### Option A: Full Disk Access
- **Risk**: HIGH - Agent gains access to entire filesystem
- **Use Case**: Only if agent needs to autonomously run tests without user intervention

### Option B: Homebrew Python Direct
- **Risk**: LOW - But limited effectiveness
- **Issue**: Still fails on `.pyc` file access with Python 3.13+

## Best Practices
1. Keep `.venv` managed by the user (creation, activation, pip installs)
2. Agent focuses on analysis and code fixes, not test execution
3. Document this limitation in README for other AI assistants
4. Use this workflow as the standard for all Python projects with similar constraints

## Related Documentation
- [mac-dev-hygiene skill](~/.gemini/antigravity/skills/mac-dev-hygiene/SKILL.md) - Technical details on sandbox limitations
- [README.md](../README.md) - Quick reference note for users
