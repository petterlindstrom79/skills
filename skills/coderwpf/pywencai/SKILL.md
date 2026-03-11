---
name: pywencai
description: Query Chinese A-share stock data from Tonghuashun Wencai (同花顺问财) using natural language.
version: 1.0.0
homepage: https://github.com/zsrl/pywencai
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","node"]}}}
---

# PyWenCai (同花顺问财数据查询)

Query Chinese A-share stock market data from [同花顺问财](https://www.iwencai.com/) using natural language queries via Python.

> ⚠️ **Cookie required**: You must provide a valid cookie from the Wencai website. See [How to get cookie](#how-to-get-cookie) below.

## Prerequisites

- **Python 3.7+**
- **Node.js v16+** (pywencai executes JS internally)
- **pip** package manager

## Install

```bash
pip install pywencai --upgrade
```

## How to get cookie

1. Open https://www.iwencai.com/ in your browser and log in.
2. Open DevTools (F12) → Network tab.
3. Perform any query on the page.
4. Find the request to `iwencai.com`, copy the `Cookie` header value.
5. Use that string as the `cookie` parameter.

## Basic usage

```python
import pywencai

res = pywencai.get(query='今日涨幅前10', cookie='your_cookie_here')
print(res)
```

## API: `pywencai.get(**kwargs)`

### Required parameters

- **query** — Natural language query string, e.g. `'今日涨停股票'`, `'市盈率小于20的股票'`
- **cookie** — Cookie string from Wencai website (required)

### Optional parameters

- **sort_key** — Column name to sort by, e.g. `'退市@退市日期'`
- **sort_order** — `'asc'` or `'desc'`
- **page** — Page number (default: `1`)
- **perpage** — Items per page (default & max: `100`)
- **loop** — `True` to fetch all pages; or integer `n` to fetch `n` pages
- **query_type** — Query category (default: `'stock'`). Options:
  - `stock` — A股股票
  - `zhishu` — 指数
  - `fund` — 基金
  - `hkstock` — 港股
  - `usstock` — 美股
  - `threeboard` — 新三板
  - `conbond` — 可转债
  - `insurance` — 保险
  - `futures` — 期货
  - `lccp` — 理财产品
- **retry** — Retry count on failure (default: `10`)
- **sleep** — Seconds between requests when looping (default: `0`)
- **log** — `True` to print logs to console
- **pro** — `True` for paid version (requires cookie)
- **no_detail** — `True` to always return `DataFrame` or `None` (never dict)
- **find** — List of stock codes to prioritize, e.g. `['600519', '000010']`
- **request_params** — Extra params for `requests`, e.g. `{'proxies': proxies}`

### Return value

- **List queries** → `pandas.DataFrame`
- **Detail queries** → `dict` (may contain text and DataFrames)

## Examples

### Find stocks with PE ratio < 20

```python
import pywencai

res = pywencai.get(query='市盈率小于20的股票', cookie='xxx')
print(res)
```

### Get delisted stocks sorted by date

```python
import pywencai

res = pywencai.get(
    query='退市股票',
    sort_key='退市@退市日期',
    sort_order='asc',
    cookie='xxx'
)
print(res)
```

### Fetch all pages with proxy

```python
import pywencai

proxies = {'http': 'http://proxy:8080', 'https': 'http://proxy:8080'}
res = pywencai.get(
    query='昨日涨幅',
    sort_order='asc',
    loop=True,
    log=True,
    cookie='xxx',
    request_params={'proxies': proxies}
)
print(res)
```

### Query index data

```python
import pywencai

res = pywencai.get(
    query='上证指数近5日涨跌幅',
    query_type='zhishu',
    cookie='xxx'
)
print(res)
```

### Query convertible bonds

```python
import pywencai

res = pywencai.get(
    query='可转债溢价率小于10%',
    query_type='conbond',
    cookie='xxx'
)
print(res)
```

## Tips

- **Low frequency usage recommended** — high-frequency calls may get blocked by Wencai.
- Always use the **latest version**: `pip install pywencai --upgrade`
- Query strings use **Chinese natural language** — write queries as you would on the Wencai website.
- When `loop=True` and `find` is set, `loop` is ignored and only first 100 results are returned.
- For paid data, set `pro=True` and provide a valid `cookie`.
