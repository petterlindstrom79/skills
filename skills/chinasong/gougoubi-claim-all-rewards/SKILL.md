---
name: gougoubi-claim-all-rewards
description: One-click claim of all rewards for specified addresses, including winner rewards, governance rewards, and LP rewards. Supports direct profile-method claim without scanning conditions.
metadata: {"clawdbot":{"emoji":"💰","os":["darwin","linux","win32"]}}
---

# Gougoubi Claim All Rewards

Claim all available rewards for one or multiple addresses in one run.

## When To Use

- User asks to claim all rewards for one or more addresses.
- User asks to avoid slow condition scanning and use profile method.

## Input

```json
{
  "addresses": ["0x...", "0x...", "0x..."],
  "method": "profile|quick|full-scan"
}
```

Defaults:

- `method=profile` (fast path, one-click style)

## Deterministic Flow

1. Validate addresses.
2. Choose method:
   - `profile`: claim by profile reward-detail style (recommended).
   - `quick`: fast direct claim script.
   - `full-scan`: exhaustive fallback.
3. Execute claim for each address.
4. Collect tx hashes and per-type claimed amount if available.
5. Return summary.

## Output

```json
{
  "ok": true,
  "method": "profile",
  "addresses": ["0x..."],
  "claimedTxCount": 0,
  "results": [
    {
      "address": "0x...",
      "winnerRewardClaimed": true,
      "governanceRewardClaimed": true,
      "lpRewardClaimed": true,
      "txHashes": ["0x..."]
    }
  ]
}
```

## Script Mapping In This Project

- `scripts/pbft-claim-rewards-profile-method.mjs`
- `scripts/pbft-claim-rewards-quick.mjs`
- `scripts/pbft-claim-three-address-rewards.mjs`

## Boundaries

- Do not require condition scan when user asks one-click profile method.
- Keep idempotent behavior (safe re-run).

