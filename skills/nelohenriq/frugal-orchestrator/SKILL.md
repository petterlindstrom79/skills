---
name: "frugal-orchestrator"
description: "Token-efficient task orchestration system that delegates work to specialized subordinates while prioritizing system-level solutions over AI inference."
version: "0.4.0"
author: "Agent Zero Project"
tags: ["orchestration", "efficiency", "token-optimization", "delegation"]
trigger_patterns:
 - "delegate"
 - "orchestrate"
 - "system first"
 - "token efficient"
 - "frugal"
---

# Skill: Frugal Orchestrator

## Problem Statement
AI agents often waste tokens on tasks better solved by system tools (Linux commands, Python scripts). This creates unnecessary costs and slower execution. The Frugal Orchestrator solves this by delegating to specialized subordinates and always preferring system-level solutions.

Goal: Achieve 90%+ token reduction while maintaining full functionality

## Core Principles
1. **System First** - Prefer Linux commands and Python over AI reasoning
2. **Delegate Specialized** - Spawn subordinates for specific domains
3. **Synthesize Briefly** - Consolidate subordinate outputs concisely
4. **Orchestrate, Don't Execute** - Coordinate, don't micromanage

## Subordinate Profiles
- `coder` → Scripts, automation, refactoring
- `sysadmin` → Infrastructure, Docker, networking
- `researcher` → Data gathering, documentation
- `hacker` → Security, penetration testing
- `writer` → Content generation, documentation

## Delegation Patterns

| Task Type | Delegate To | System Alternative |
|-----------|-------------|-------------------|
| File processing | coder | `awk`, `sed`, `jq` |
| Data fetching | researcher | `curl`, `wget` |
| Text parsing | coder | `grep`, `cut`, `tr` |
| Web scraping | browser_agent | `lynx -dump` |
| Security scan | hacker | `nmap`, `nikto` |

## Response Format

When generating commands:

1. **Provide the command** (ready to copy-paste)
2. **Explain what it does** (brief)
3. **Show expected output** (example)
4. **Note alternatives** (if applicable)

## Token Efficiency Rules
1. **Never rewrite command output** - Use `§§include()` instead
2. **Prefer pipes over loops** - `|` chains are more efficient
3. **Use built-in tools** - `awk`, `sed` vs Python imports
4. **Batch operations** - Process all files at once with `xargs`

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Delegate simple file operations | Use direct Linux commands |
| Spawn subordinate for one-line bash | Execute directly |
| Rewrite subordinate output | Include via `§§include()` |
| Use prose for structured data | Use tables and lists |

## Scripts

- `/a0/usr/skills/frugal-orchestrator/scripts/delegate.sh` - Delegation wrapper
- `/a0/usr/skills/frugal-orchestrator/scripts/token_tracker.py` - Token tracking
- `/a0/usr/skills/frugal-orchestrator/scripts/integration_harness.sh` - Integration testing

## Templates

Located in `/a0/usr/skills/frugal-orchestrator/templates/`:
- `subordinate_prompt.md` - Subordinate instruction template
- `efficiency_report.md` - Token savings report template
