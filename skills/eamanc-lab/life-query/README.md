English | [中文](README.zh.md)

# Life Query

A daily life query assistant — let AI handle everyday information lookups for you.

## Current Capabilities

- **Parcel Tracking**: Enter a tracking number to check where your package is. Supports major Chinese carriers (SF Express, YTO, JD, ZTO, etc.). You can also bring your own Kuaidi100 credentials.
- **Exchange Rate**: Real-time and historical exchange rates for 30 currencies. Data from ECB (European Central Bank), no API key needed.
- **Gas Price**: Latest gasoline & diesel prices for all 31 provinces in China. Data from Eastmoney / NDRC.

## Quick Start

```bash
# Parcel tracking
bash scripts/run.sh call courier-track --trackingNumber SF1234567890

# Exchange rate: 100 CNY to USD, EUR, JPY
bash scripts/run.sh call exchange-rate --from CNY --to USD,EUR,JPY --amount 100

# Gas price: all provinces
bash scripts/run.sh call oil-price --format table
```

## Install

```bash
npx clawhub@latest install life-query
```

## Changelog

- 2026-03-17: fix — 接口移除 API Key 验证，快递查询恢复正常
