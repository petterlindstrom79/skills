---
description: Determine the smallest reliable skill stack for a goal
  using capability mapping, overlap detection, and deterministic
  scoring.
name: skillfit-optimizer
---

# SkillFit Optimizer

## Skill type

Agent configuration / Skill selection / Workflow optimization

## Safety profile

Low risk. Runs in **analysis mode by default** and only modifies the
environment when explicitly requested.

------------------------------------------------------------------------

# Purpose

SkillFit Optimizer helps determine the **smallest reliable skill stack**
needed to accomplish a user's goal.

Instead of installing many tools blindly, the optimizer:

-   analyzes the goal
-   maps required capabilities
-   identifies candidate skills
-   removes redundant tools
-   checks environment readiness
-   scores candidate stacks
-   recommends the most reliable configuration

This helps prevent:

-   tool sprawl
-   overlapping capabilities
-   fragile workflows
-   unnecessary dependencies

------------------------------------------------------------------------

# Quick Start

Example request:

"What is the best skill stack for editing PDFs and analyzing documents?"

The optimizer will:

1.  analyze the goal
2.  identify required capabilities
3.  build candidate skill stacks
4.  check environment readiness
5.  recommend the best stack

------------------------------------------------------------------------

# Triggers

Invoke this skill when users ask:

-   "What skills do I need for this task?"
-   "Optimize my skill stack."
-   "Recommend a minimal tool setup."
-   "Which skills overlap?"
-   "What tools should I install?"
-   "Simplify my workflow tools."

------------------------------------------------------------------------

# Required Inputs

-   user_goal
-   environment_info (optional)
-   preferred_profile (optional)

------------------------------------------------------------------------

# Capability Mapping

User goals are translated into capability categories.

Example:

Goal: "Edit PDFs and summarize documents"

Capabilities:

-   pdf_editing
-   document_analysis
-   summarization

------------------------------------------------------------------------

# Capability Matrix

Example capabilities and typical skill matches.

  Capability               Example Skills
  ------------------------ ----------------
  pdf_editing              nano-pdf
  document_analysis        data-analysis
  document_editing         word-docx
  spreadsheet_processing   excel-xlsx
  automation               skill-creator
  api_interaction          trello

------------------------------------------------------------------------

# Profiles

## Minimal

Smallest possible working stack.

Focus:

-   lowest setup complexity
-   minimal dependencies
-   fastest deployment

------------------------------------------------------------------------

## Balanced

Balanced tradeoff between capability coverage and reliability.

Recommended default profile.

------------------------------------------------------------------------

## Maximum

Largest stack providing maximum redundancy and capability coverage.

------------------------------------------------------------------------

# Runtime Steps

## 1. Analyze Goal

Extract required capabilities from the request.

------------------------------------------------------------------------

## 2. Build Capability Map

Translate the goal into structured capability categories.

------------------------------------------------------------------------

## 3. Discover Candidate Skills

Identify available skills capable of providing each capability.

Construct:

-   candidate skill list
-   capability coverage map

------------------------------------------------------------------------

## 4. Detect Overlap

Identify redundant tools performing the same capability.

Prefer fewer high-signal skills.

------------------------------------------------------------------------

## 5. Generate Candidate Stacks

Produce stacks for each profile:

-   Minimal
-   Balanced
-   Maximum

Each stack includes:

-   skills
-   capabilities covered
-   missing capabilities (if any)

------------------------------------------------------------------------

## 6. Run Environment Checks

Verify environment readiness.

Check for availability of common binaries:

python node jq curl git

Record results as:

-   available
-   missing
-   unknown

------------------------------------------------------------------------

## 7. Compute Stack Score

Stacks are scored across four dimensions.

Coverage --- capability satisfaction\
Reliability --- stability of tools\
Setup Friction --- installation complexity\
Overlap Discipline --- redundancy penalty

Score formula:

score = coverage \* 0.40 + reliability \* 0.30 + setup_friction \*
0.20 + overlap_discipline \* 0.10

Score range: 0--100

------------------------------------------------------------------------

## 8. Select Recommended Stack

Choose the highest scoring stack.

Tie‑break rules:

1.  fewer skills
2.  higher coverage
3.  lower setup friction

------------------------------------------------------------------------

## 9. Produce Recommendations

Return:

-   recommended stack
-   alternative stacks
-   missing dependencies
-   setup guidance

------------------------------------------------------------------------

# Output Contract

Return structured output:

{ "goal": "Edit PDFs and summarize documents", "recommended_profile":
"balanced", "recommended_stack": \[ "nano-pdf", "data-analysis" \],
"stack_score": 88, "capability_coverage": \[ "pdf_editing",
"document_analysis", "summarization" \], "environment_check": {
"python": "available", "jq": "available", "curl": "missing" },
"alternatives": { "minimal": \["nano-pdf"\], "maximum": \["nano-pdf",
"data-analysis", "skill-creator"\] } }

------------------------------------------------------------------------

# Best Practices

Prefer smaller stacks when possible.

Avoid overlapping tools that provide identical functionality.

Check environment readiness before installing skills.

Re-run the optimizer when workflows evolve.

------------------------------------------------------------------------

# Common Optimization Issues

## Skill Bloat

Too many tools installed for simple tasks.

Solution: prune redundant skills.

------------------------------------------------------------------------

## Capability Gaps

Required capability missing.

Solution: add a targeted skill.

------------------------------------------------------------------------

## Environment Mismatch

Required binaries unavailable.

Solution: install dependencies.

------------------------------------------------------------------------

# Related Skills

Agent Regression Check

Use Agent Regression Check after stack changes to verify that
configuration updates did not introduce regressions.

------------------------------------------------------------------------

# Limitations

SkillFit Optimizer:

-   does not execute workflows
-   cannot guarantee correctness of external tools
-   provides structured recommendations rather than guarantees

------------------------------------------------------------------------

# Implementation Note

If a helper script such as scripts/stack_check.py exists, use it for
environment checks. Otherwise perform lightweight PATH checks.
