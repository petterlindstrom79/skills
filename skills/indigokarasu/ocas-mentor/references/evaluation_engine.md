# Mentor Evaluation Engine

## Journal Ingestion
Read newly written journals from all skills. Validate schema. Quarantine malformed entries.

## OKR Scoring
Score universal OKRs (reliability, validation integrity, efficiency, context stability, observability) plus skill-specific OKRs. Evaluate over rolling windows.

## Champion/Challenger Pairing
Pair runs with same comparison_group_id. Require identical normalized_input_hash. Verify challenger did not execute side effects. Compare universal OKRs, skill-specific OKRs, latency, retries, reliability.

## Aggregate Evaluation
Build evaluation dataset over multiple runs. Do not promote on single-run basis except emergency rollback.
