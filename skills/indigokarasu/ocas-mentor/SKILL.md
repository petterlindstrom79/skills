---
name: ocas-mentor
description: >
  Self-improving orchestration and evaluation engine for long-running
  multi-skill workflows. Analyzes journals, evaluates variants, and
  proposes skill improvements.
---

# Mentor

Mentor is the control plane for long-running autonomous work. It decomposes goals into task graphs, supervises execution across skills, detects and repairs failures, and continuously evaluates orchestration quality. During heartbeat cycles, it analyzes journals, compares champion vs challenger variants, and proposes skill improvements.

Mentor is one skill with two invocation modes sharing state, telemetry, and learning.

## When to use

- Manage a long-running multi-step project
- Coordinate work across multiple skills
- Evaluate skill performance from journal data
- Compare champion vs challenger variant runs
- Generate improvement proposals for Forge

## When not to use

- Web research — use Sift
- Building new skills — use Forge
- User communication — use Dispatch
- Behavioral pattern analysis — use Corvus

## Core promise

Decompose complex goals into supervised task graphs. Detect and repair failures. Evaluate skill quality over time. Propose improvements. Improve both the ecosystem and its own orchestration.

## Commands

- `mentor.project.create` — create a project with goal, constraints, and requested output
- `mentor.project.status` — current project state, task graph, execution progress
- `mentor.project.replan` — trigger strategy-level replan
- `mentor.task.list` — tasks with statuses, dependencies, blocking reasons
- `mentor.heartbeat.light` — lightweight pass: update aggregates, queue work
- `mentor.heartbeat.deep` — deep pass: full scoring, trend analysis, proposals
- `mentor.variants.list` — active champion/challenger pairs with evaluation status
- `mentor.variants.decide` — emit promotion decision for a variant
- `mentor.proposals.list` — pending skill improvement proposals
- `mentor.proposals.create` — generate a variant proposal for a target skill
- `mentor.status` — active projects, pending evaluations, self-improvement metrics

## Mode A — Runtime orchestration

Triggered by explicit invocation. Creates a project record, builds a task graph, executes and supervises tasks, dynamically replans when blocked.

Task states: pending, ready, running, blocked, failed, complete, archived.

Scheduling: execute only tasks with complete dependencies. Prioritize critical path. Bounded parallelism. Bounded retries.

## Mode B — Heartbeat evolution

Triggered periodically. Pipeline: ingest journals → validate schema → aggregate metrics → pair champion/challenger → score OKRs → detect anomalies → evaluate variants → generate proposals → emit decisions → write journal.

## Layered evaluation loops

- **Layer 1 — Micro Action** (ms-sec): validate single outputs. Retry, local repair, fallback.
- **Layer 2 — Task Execution** (sec-min): ensure task completion. Retry, switch skill, split task.
- **Layer 3 — Strategy** (min-hr): improve active project plan. Reorder, insert, merge, parallelize.
- **Layer 4 — Evolution** (hr-wk): improve skills and policies. Propose variants, promote/archive.

## Failure repair policy

Order: retry with refined framing → alternate skill → split task → revise ordering → escalate to strategy loop. Never retry indefinitely. Every repair action journaled.

## Safety invariants

- Challenger variants never execute side effects
- Comparisons only on identical normalized inputs
- Malformed journals quarantined, not trusted
- Promotion requires sufficient evidence over multiple runs
- Mentor journals its own orchestration decisions

## Support file map

- `references/schemas.md` — Project, TaskNode, SkillInvocation, VariantProposal, VariantEvaluation, VariantDecision
- `references/orchestration_engine.md` — goal decomposition, scheduling, skill selection, failure repair
- `references/evaluation_engine.md` — journal ingestion, OKR scoring, champion/challenger pairing
- `references/evolution_engine.md` — improvement detection, proposal generation, promotion criteria, self-improvement

## Storage layout

```
.mentor/
  config.json
  projects/
  evaluations/
  journals.jsonl
  decisions.jsonl
```

## Validation rules

- Task graph contains no circular dependencies
- Every task has a candidate skill assignment
- Champion/challenger pairs have identical input hashes
- Promotion decisions cite aggregate evidence, not single runs
