---
name: check-balance
description: Check USDC balance across networks (Base, Solana)
user-invocable: true
disable-model-invocation: false
allowed-tools: ["Bash(npx agnic@latest *)"]
---

# Check Balance

Check the user's USDC balance across supported networks.

## Steps

1. Verify authentication:
   ```bash
   npx agnic@latest status --json
   ```
   If not authenticated, provide `--token`, set `AGNIC_TOKEN`, or run `npx agnic@latest auth login`.

2. Check balance for all networks:
   ```bash
   npx agnic@latest balance --json
   ```

3. Or check a specific network:
   ```bash
   npx agnic@latest balance --network base --json
   npx agnic@latest balance --network solana --json
   ```

## Expected Output

```json
[
  { "network": "base", "balance": "125.50", "address": "0x..." },
  { "network": "solana", "balance": "0", "address": "N/A" }
]
```

## Supported Networks

- `base` — Base mainnet (EVM, primary)
- `solana` — Solana mainnet
- `base-sepolia` — Base testnet
- `solana-devnet` — Solana devnet

## Error Handling

- If not authenticated: prompt user to provide `--token`, set `AGNIC_TOKEN`, or run `npx agnic@latest auth login`
- If a network returns an error, report it and show available balances
