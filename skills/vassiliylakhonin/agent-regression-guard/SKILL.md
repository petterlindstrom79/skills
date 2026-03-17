---
description: Compare before-vs-after agent behavior, detect regressions,
  and return a deterministic release verdict with prioritized fixes.
name: agent-regression-check
---

# Agent Regression Check

## What this skill does

Use this skill to evaluate whether an agent change introduced
regressions.

It compares **before vs after** behavior across a defined case suite,
identifies what got worse, applies deterministic release gates, and
returns a clear verdict:

-   go
-   conditional_go
-   no_go
-   rollback

This is an **offline regression-check skill**. It does not replace
production monitoring or live experiments.

------------------------------------------------------------------------

# Best use cases

Use this skill for:

-   prompt updates
-   model switches
-   tool integration changes
-   retrieval changes
-   orchestration changes
-   hotfix verification
-   pre-release quality checks

Typical user requests:

-   "Did this update break anything?"
-   "Compare before and after."
-   "Is this safe to deploy?"
-   "Check for regressions after the model change."
-   "Should we roll this back?"
-   "Which failures got worse?"

------------------------------------------------------------------------

# When not to use

Do not use this skill if:

-   there is no comparable before/after evidence
-   the case sets differ and cannot be matched reliably
-   the suite is too small to support a release decision
-   the task requires online experimentation
-   the user wants brainstorming instead of deterministic assessment

If evidence quality is weak, say so explicitly and lower confidence.

------------------------------------------------------------------------

# Required inputs

Provide these whenever possible:

-   change_summary
-   before_cases
-   after_cases
-   risk_level (low, medium, high)

Example input:

``` json
{
  "cases": [
    {
      "id": "case_001",
      "task_type": "faq",
      "critical": true,
      "input": "How do I reset my password?",
      "expected_behavior": "Provides reset steps and fallback.",
      "before_output": "...",
      "after_output": "...",
      "before_tools": [],
      "after_tools": []
    }
  ]
}
```

------------------------------------------------------------------------

# Optional inputs

These improve evaluation quality:

-   suite_manifest
-   thresholds
-   strict_mode
-   output_path

------------------------------------------------------------------------

# Matching rules

Cases must match by **stable id**.

If IDs do not match:

-   flag suite inconsistency
-   reduce confidence
-   avoid aligning by position unless explicitly requested

------------------------------------------------------------------------

# Deterministic scoring rubric

Each case is scored across four dimensions.

## Correctness

2 = correct\
1 = partially correct\
0 = incorrect

## Relevance

2 = fully relevant\
1 = somewhat relevant\
0 = off-target

## Actionability

2 = actionable\
1 = partially actionable\
0 = not actionable

## Tool reliability

2 = correct tool usage\
1 = minor tool issue\
0 = tool failure

------------------------------------------------------------------------

# Case outcome rules

### pass

correctness ≥ 2\
relevance ≥ 1\
actionability ≥ 1\
tool reliability ≥ 1

### soft_fail

usable answer but degraded quality.

### fail

-   correctness = 0
-   safety/fallback missing
-   tool failure
-   after worse than before

Any fail on a **critical case** is high severity.

------------------------------------------------------------------------

# Aggregated metrics

Compute:

-   overall_pass_rate
-   critical_pass_rate
-   soft_fail_rate
-   tool_reliability_rate
-   average_correctness
-   average_relevance
-   average_actionability

Also compute deltas:

-   overall_pass_rate_delta
-   critical_pass_rate_delta
-   tool_reliability_delta

Never hide negative deltas.

------------------------------------------------------------------------

# Default release gates

## Low risk

overall_pass_rate ≥ 0.90\
critical_pass_rate ≥ 0.95

## Medium risk

overall_pass_rate ≥ 0.95\
critical_pass_rate = 1.00\
tool_reliability ≥ 0.95

## High risk

overall_pass_rate ≥ 0.98\
critical_pass_rate = 1.00\
tool_reliability ≥ 0.98

Human review recommended.

------------------------------------------------------------------------

# Verdict rules

Return exactly one verdict.

## go

All gates pass.

## conditional_go

Minor issues but no critical regressions.

## no_go

Gates fail. Fixes required.

## rollback

Critical regressions detected.

------------------------------------------------------------------------

# Failure clustering

Group failures by likely cause.

Examples:

-   instruction_following_drift
-   factuality_drop
-   retrieval_miss
-   tool_call_failure
-   format_noncompliance
-   missing_fallback
-   hallucinated_capability

Each cluster should include:

-   name
-   severity
-   affected cases
-   likely cause
-   suggested fix direction

------------------------------------------------------------------------

# Anti-gaming rules

Flag explicitly:

-   different case sets before/after
-   missing critical cases
-   incomplete tool traces
-   changed expectations
-   too few cases for a release decision

If detected:

-   lower confidence
-   explain limitations

------------------------------------------------------------------------

# Confidence levels

Return:

-   high
-   medium
-   low

Confidence depends on:

-   suite size
-   representativeness
-   case matching quality
-   tool trace completeness

------------------------------------------------------------------------

# Output contract

Return results in this structure:

``` json
{
  "change_summary": "Switched model and simplified system prompt",
  "risk_level": "medium",
  "confidence": "medium",
  "suite_summary": {
    "total_cases": 18,
    "critical_cases": 6
  },
  "scorecard": {
    "overall_pass_rate": 0.89,
    "critical_pass_rate": 0.83,
    "tool_reliability_rate": 0.94
  },
  "deltas": {
    "overall_pass_rate_delta": -0.08
  },
  "verdict": "no_go",
  "top_regressions": [
    {
      "case_id": "case_003",
      "summary": "Fallback step missing"
    }
  ],
  "recommended_fixes": [
    "Restore fallback instruction",
    "Retest critical FAQ flows"
  ]
}
```

------------------------------------------------------------------------

# Response format

Responses should include:

1.  executive summary
2.  scorecard
3.  regressions
4.  clusters
5.  verdict
6.  recommended fixes
7.  confidence

------------------------------------------------------------------------

# Limitations

This skill cannot:

-   guarantee production improvement
-   replace monitoring
-   perfectly infer user impact from a small suite

High-risk changes should still involve human review.

------------------------------------------------------------------------

# Implementation note

If a scorer script exists, use it.

Otherwise apply this rubric manually.

Never suppress regressions. Never skip failing cases.
