---
name: council-v2
description: >
  Publishable multi-model council review system for code review, plan review,
  architecture review, decision review, structured critique, adversarial review,
  second opinion, pre-flight review, final review before merge, QA council,
  sanity check with multiple models, and review-before-shipping workflows.
version: 2.0.0
---

# Council v2

A hardened, publishable OpenClaw skill for multi-model council reviews.
It dispatches independent reviewers, collects structured JSON, and applies a
**mechanical synthesis protocol** so the final verdict is driven by votes and
critical findings — not orchestrator vibes.

Primary entrypoint: `bash scripts/council.sh review <type> [file]`

## When to Use

Use when a single model reviewing its own work is not enough:
- Code review before merge or deployment
- Plan review before committing resources
- Architecture review for important technical decisions
- Decision review when multiple plausible options exist
- Security-sensitive or irreversible choices
- Pre-flight review, adversarial critique, or second-opinion work

## When Not to Use

Do **not** use for:
- One-line fixes or trivial edits
- Low-stakes decisions where overhead exceeds risk
- Purely factual lookups with no judgment call
- Work already reviewed recently with no material change

## Council Tiers

### Standard Council — 3 reviewers
Use for routine code, plan, and decision reviews.

| Role | Model alias | Purpose |
|------|-------------|---------|
| Architecture Synthesizer | `opus` | Holistic reasoning and maintainability |
| Adversarial Critic | `gpt-5.4` | Finds holes, contradictions, weak assumptions |
| Security & Risk | `grok4` | Security, misuse, manipulation, blast radius |

### Full Council — 5 reviewers
Use for high-stakes reviews, architecture changes, security audits, and anything irreversible.

| Role | Model alias | Purpose |
|------|-------------|---------|
| Architecture Synthesizer | `opus` | Holistic reasoning and synthesis |
| Adversarial Critic | `gpt-5.4` | Aggressive critique and edge cases |
| Security & Risk | `grok4` | Security, abuse, policy, and risk |
| First Principles | `deepseek` | Assumption stripping and first-principles analysis |
| Structural Verifier | `gemini` | Process design, systems fit, scale, and failure modes |

## Mandatory Full Council Triggers

Use **Full Council** automatically when any of these are true:
- Changes to AGENTS.md, constitutions, or operating rules
- New tool, plugin, or capability installation
- Security-related decisions or source/security audits
- External communications policy changes
- Orchestrator confidence below 0.7
- Irreversible or high-blast-radius actions

Everything else defaults to Standard Council.

## Mechanical Synthesis Rules

The v2 protocol is intentionally narrow:
1. **Majority vote decides.** The synthesizer narrates; it does not override.
2. **Critical finding auto-block.** Any reviewer finding with `severity=critical` blocks approval.
3. **Splits default conservative.** Ambiguous or tied results resolve to modify/reject.
4. **Conditional votes count as half.** `approve_with_conditions = 0.5`.
5. **Anti-consensus check on unanimous outcomes.** Strongest serious counterargument must be surfaced.
6. **Raw outputs shown on Full Council.** Operator sees source verdicts, not just the summary.
7. **All reviewers vote (including Opus).** Synthesis is done by `synthesize.py` (script), not a model. Orchestrator writes the narrative but cannot change the verdict.
8. **Minority reports are always preserved.** Strongest dissent is never buried.

See `references/synthesis-rules.md` for examples and edge cases.

## Review Types

| Type | Typical use |
|------|-------------|
| `code` | Source files, scripts, patches, PR diffs |
| `plan` | Proposals, project plans, rollout plans |
| `architecture` | Systems design, infra decisions, workflows |
| `decision` | A/B/C choices with tradeoffs |

Definitions: `references/review-types.md`

## Quick Start

```bash
# Standard code review
bash scripts/council.sh review code src/auth.py

# Force full plan review
bash scripts/council.sh review plan proposal.md --tier full

# Architecture review from stdin
cat design.md | bash scripts/council.sh review architecture --tier full

# Decision review with options
bash scripts/council.sh review decision options.md --options "SQLite,Postgres,Cloud SQL"

# Emit orchestration plan as JSON
bash scripts/council.sh review code src/auth.py --format json
```

## How It Works

1. Loads content from file or stdin
2. Selects Standard or Full tier
3. Builds reviewer prompts from `references/role-prompts.md`
4. Emits an orchestration plan suitable for `sessions_spawn`
5. Collects reviewer JSON outputs
6. Runs `python3 scripts/synthesize.py ...`
7. Optionally runs a monthly retrospective via `scripts/retro.sh`

## Installation

Install with ClawHub when published:

```bash
clawhub install council-v2
```

Manual install during development:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R council-v2 ~/.openclaw/workspace/skills/
```

Requirements:
- `bash`
- `python3`
- OpenClaw with `sessions_spawn` available for reviewer dispatch

No hardcoded absolute paths are used; scripts resolve relative to the skill directory.

## Configuration

Model aliases default to:
- `opus`
- `gpt-5.4`
- `grok4`
- `deepseek`
- `gemini`

Override via flags in `scripts/council.sh` if your environment uses different aliases.

## Monthly Retro Protocol

Run on the first Sunday of the month or after several consequential reviews:

```bash
bash scripts/retro.sh path/to/council-log-dir
```

The retro samples past decisions, checks correctness in hindsight, and highlights reviewer signal-to-noise.

## References

- `references/review-types.md`
- `references/role-prompts.md`
- `references/schema.md`
- `references/synthesis-rules.md`
