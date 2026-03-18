# Mentor Schemas

## Project
```json
{"project_id":"string","goal":"string","constraints":"object","requested_output":"string","status":"string","created_at":"string","updated_at":"string"}
```

## TaskNode
```json
{"task_id":"string","title":"string","description":"string","dependencies":["string"],"candidate_skill":"string","status":"string — pending|ready|running|blocked|failed|complete|archived","retry_count":"number","priority":"number","expected_artifacts":["string"],"blocking_reason":"string|null"}
```

## SkillInvocation
```json
{"task_id":"string","skill_name":"string","skill_version":"string","input_hash":"string","start_time":"string","end_time":"string","success":"boolean","retry_count":"number","artifacts_produced":["string"],"model":"string|null","provider":"string|null"}
```

## VariantProposal
```json
{"proposal_id":"string","target_skill":"string","base_version":"string","observed_problem":"string","supporting_evidence":["string"],"proposed_changes":"string","expected_improvement":"string","minimum_runs":"number"}
```

## VariantDecision
```json
{"variant_id":"string","target_skill":"string","decision":"string — promote|continue_testing|archive|reject|emergency_rollback","rationale":"string","aggregate_scores":"object","confidence":"string","timestamp":"string"}
```
