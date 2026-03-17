---
name: polymarket-celebrity-social-trader
description: Trades Polymarket prediction markets on celebrity events, viral social media moments, Elon Musk tweet counts, influencer milestones, and reality TV outcomes. Use when you want to exploit retail emotional overreaction and social media momentum signals on entertainment markets.
metadata:
  author: Diagnostikon
  version: "1.0"
  displayName: Celebrity & Social Media Trader
  difficulty: beginner
---

# Celebrity & Social Media Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Social velocity signal: Twitter/X engagement rate in first hour predicts market outcome better than Polymarket price. Remix: Twitter API v2 engagement metrics, Social Blade YouTube analytics API, Elon tweet tracker.


## Edge Thesis

Celebrity markets are the most emotionally traded category on Polymarket — fans, haters, and memers all pile in. This creates large, exploitable mispricings:

- **Elon tweet count markets**: Elon's tweet rate is very consistent week-over-week (~350–400 tweets/week in 2026). When Polymarket prices a count as <30% likely that is already a near-certainty based on his historical rate, strong YES edge exists
- **Hype-fade pattern**: Markets on celebrity projects (album, film, product launch) get bid up 20–30% above true probability in the 48h around announcement, then fade as hype cools
- **Reality TV voting**: Reality TV outcome markets (Dancing with the Stars, Survivor) track very closely with social media engagement metrics published by Nielsen Social Content Ratings
- **Feud/beef markets**: Celebrity beef markets systematically overprice reconciliation (fans want to believe) — fade to NO

### Remix Signal Ideas
- **Social Blade**: https://socialblade.com/ — YouTube/Twitch/Instagram analytics
- **Twitter/X API v2**: Engagement rate and impression data
- **Elon Tweet Counter**: https://xtracker.io/ or custom Twitter API query
- **Google Trends API**: Search interest as proxy for cultural salience


## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only with `--live` flag.**

| Scenario | Mode | Financial risk |
|---|---|---|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

`autostart: false` and `cron: null` — nothing runs automatically until you configure it in Simmer UI.

## Required Credentials

| Variable | Required | Notes |
|---|---|---|
| `SIMMER_API_KEY` | Yes | Trading authority. Treat as high-value credential. |

## Tunables (Risk Parameters)

All declared as `tunables` in `clawhub.json` and adjustable from the Simmer UI.

| Variable | Default | Purpose |
|---|---|---|
| `SIMMER_MAX_POSITION` | See clawhub.json | Max USDC per trade |
| `SIMMER_MIN_VOLUME` | See clawhub.json | Min market volume filter |
| `SIMMER_MAX_SPREAD` | See clawhub.json | Max bid-ask spread |
| `SIMMER_MIN_DAYS` | See clawhub.json | Min days until resolution |
| `SIMMER_MAX_POSITIONS` | See clawhub.json | Max concurrent open positions |

## Dependency

`simmer-sdk` by Simmer Markets (SpartanLabsXyz)
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
