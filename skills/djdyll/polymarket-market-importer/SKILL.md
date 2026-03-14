---
name: polymarket-market-importer
description: Auto-discover and import Polymarket markets matching your keywords, tags, and volume criteria. Runs on a schedule so you never miss a new market worth trading. Set your filters once — the skill handles the rest.
metadata:
  author: "DjDyll"
  version: "1.0.0"
  displayName: "Polymarket Market Importer"
  difficulty: "beginner"
---

# 🎯 Polymarket Market Importer

> **This is a template.** Configure your keywords, categories, and volume filters — the skill auto-discovers and imports matching Polymarket markets on a schedule.

## What It Does

Searches Polymarket for new markets matching your criteria and imports them into Simmer automatically. Runs every 6 hours so you never miss a new market worth trading. Already-imported markets are tracked and skipped.

## Setup

1. **Install dependencies:**
   ```bash
   pip install simmer-sdk
   ```

2. **Set your API key:**
   ```bash
   export SIMMER_API_KEY="sk_live_..."
   ```

3. **Configure your filters:**
   ```bash
   python market_importer.py --set keywords=bitcoin,ethereum,solana
   python market_importer.py --set min_volume=25000
   python market_importer.py --set categories=crypto,politics
   python market_importer.py --set max_per_run=10
   ```

4. **Test with a dry run:**
   ```bash
   python market_importer.py
   ```

5. **Run live:**
   ```bash
   python market_importer.py --live
   ```

## Configuration

| Parameter | Env Var | Default | Description |
|-----------|---------|---------|-------------|
| `keywords` | `IMPORTER_KEYWORDS` | `bitcoin,ethereum` | Comma-separated search keywords |
| `min_volume` | `IMPORTER_MIN_VOLUME` | `10000` | Minimum 24h volume filter |
| `max_per_run` | `IMPORTER_MAX_PER_RUN` | `5` | Max markets to import per run |
| `categories` | `IMPORTER_CATEGORIES` | `crypto` | Comma-separated category filters |

## Quick Commands

```bash
# Dry run — see what would be imported
python market_importer.py

# Live import
python market_importer.py --live

# Show recently imported markets
python market_importer.py --positions

# Show current config
python market_importer.py --config

# Update config
python market_importer.py --set keywords=bitcoin,ethereum,xrp

# Quiet mode (only output on imports/errors)
python market_importer.py --live --quiet
```

## Example Output

```
🎯 Polymarket Market Importer
==================================================

  [LIVE MODE] Importing markets for real.

  Config: keywords=bitcoin,ethereum | min_volume=10000 | max_per_run=5 | categories=crypto

  Searching for: bitcoin
    Found 12 importable markets
    3 already imported, 9 new
    Category match: 7

  Searching for: ethereum
    Found 8 importable markets
    2 already imported, 6 new
    Category match: 5

  Importing: "Will BTC exceed $150k by July 2026?" (vol: $125,000)
    ✅ Imported successfully
  Importing: "Will ETH reach $5k by June 2026?" (vol: $89,000)
    ✅ Imported successfully

  Summary: 20 found | 5 already seen | 2 imported (max 5)
```

## Troubleshooting

- **"No importable markets found"** — Try broader keywords or lower `min_volume`.
- **"Import quota exceeded"** — Free accounts get 10 imports/day, Pro gets 50. Wait or upgrade.
- **"SIMMER_API_KEY not set"** — Export your API key: `export SIMMER_API_KEY="sk_live_..."`
- **Markets not matching categories** — Category filtering checks the market question text. Try different category keywords.

## Schedule

Runs every 6 hours via cron (`0 */6 * * *`). Adjust in `clawhub.json` if needed.
