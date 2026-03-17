---
name: life-query
description: Query everyday life info — parcel tracking via Kuaidi100 for Chinese carriers (SF Express, ZTO, YTO, JD), real-time and historical currency exchange rates from ECB (30 currencies including CNY/USD/EUR/JPY), and gasoline/diesel prices for all 31 provinces in China from NDRC. Use when user asks "查快递", "track package", "物流查询", "包裹到哪了", "汇率", "exchange rate", "多少钱换", "美元人民币", "油价", "gas price", "今天92多少钱", "加油多少钱".
homepage: https://github.com/eamanc-lab/life-query
---

# Life Query — 日常生活查询助手

快递物流跟踪、实时汇率换算、全国油价查询。

## 外部服务声明

本 skill 通过中转服务 `https://api.fenxianglife.com` 查询快递数据，该服务再调用快递100等数据源。你提供的快递单号会发送到该端点。

默认提供一定的免费查询额度，无需任何配置即可使用。如果免费额度不够，可以配置自己的快递100凭证：

1. 前往 [快递100 API](https://api.kuaidi100.com/) 注册账号并开通实时查询接口
2. 获取 `授权Key` 和 `Customer`
3. 配置环境变量：

```bash
export KUAIDI100_KEY=你的授权Key
export KUAIDI100_CUSTOMER=你的Customer编码
```

配置后查询时会自动读取，无需每次手动传入。也可以通过命令行参数临时覆盖：

```bash
bash scripts/run.sh call courier-track --trackingNumber SF1234567890 \
  --kuaidi100Key YOUR_KEY --kuaidi100Customer YOUR_CUSTOMER
```

## 可用接口

| 接口 | 类型 | 说明 |
|------|------|------|
| courier-track | YAML | 查询快递物流轨迹 |
| exchange-rate | 脚本 | 查询实时/历史汇率，货币换算（数据来源欧洲央行） |
| oil-price | 脚本 | 查询全国各省油价（数据来源东方财富/国家发改委） |

## 使用方式

### 快递查询

```bash
# 查快递（自动识别快递公司）
bash scripts/run.sh call courier-track --trackingNumber SF1234567890

# 指定快递公司
bash scripts/run.sh call courier-track --trackingNumber SF1234567890 --carrierCode shunfeng
```

### 汇率查询

```bash
# 100 人民币换算成美元、欧元、日元
bash scripts/run.sh call exchange-rate --from CNY --to USD,EUR,JPY --amount 100

# 查询某天的历史汇率
bash scripts/run.sh call exchange-rate --from USD --to CNY --date 2025-01-01

# 查询一段时间内的汇率走势
bash scripts/run.sh call exchange-rate --from USD --to CNY --startDate 2026-03-01 --endDate 2026-03-10

# 从某天到今天
bash scripts/run.sh call exchange-rate --from USD --to CNY --startDate 2026-03-01 --endDate ""

# 表格格式输出
bash scripts/run.sh call exchange-rate --from CNY --to USD,EUR,JPY --format table
```

### 油价查询

```bash
# 查询全国所有省份最新油价
bash scripts/run.sh call oil-price

# 查询指定省份（如北京）
bash scripts/run.sh call oil-price --city 北京

# 查询指定省份的历史油价（取最近5条）
bash scripts/run.sh call oil-price --city 北京 --pageSize 5

# 表格格式输出
bash scripts/run.sh call oil-price --format table
```

## 自然语言映射

| 用户说 | 接口 | 关键参数 |
|--------|------|---------|
| "帮我查一下 SF1234567890" | courier-track | trackingNumber=SF1234567890 |
| "这个单号的物流在哪里" | courier-track | trackingNumber=... |
| "100美元换多少人民币" | exchange-rate | from=USD, to=CNY, amount=100 |
| "今天美元汇率多少" | exchange-rate | from=USD, to=CNY |
| "最近一周日元走势" | exchange-rate | from=JPY, to=CNY, startDate/endDate |
| "今天油价多少" | oil-price | 默认全国 |
| "北京92号汽油多少钱" | oil-price | city=北京 |
| "广东最近几次油价调整" | oil-price | city=广东, pageSize=5 |
