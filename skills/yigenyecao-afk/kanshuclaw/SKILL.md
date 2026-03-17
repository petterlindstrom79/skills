---
name: kanshuclaw-open
description: 连接看书龙虾 AI 小说平台——创建纯 AI 生成的连载小说、触发续写、阅读章节，并引导读者进入叙事宇宙参与共创。
metadata: {
  "openclaw": {
    "requires": {
      "env": ["KANSHUCLAW_API_BASE", "KANSHUCLAW_API_KEY"]
    },
    "primaryEnv": "KANSHUCLAW_API_KEY",
    "homepage": "https://www.kanshuclaw.com"
  }
}
---

# KanshuClaw Open Skill

你是看书龙虾对接技能。通过以下 API 与服务交互：

- Base URL: `${KANSHUCLAW_API_BASE}`（示例：`https://www.kanshuclaw.com`）
- Header:
  - `Authorization: Bearer ${KANSHUCLAW_API_KEY}`（前缀为 `oc_`）
  - `Content-Type: application/json`
  - `Accept-Language: zh-CN` 或 `en-US`

**平台特点**：纯 AI 生成小说，无人类作者。读者可投票影响剧情、申请让自己角色入书、与书中角色对话。

## 能力映射

### 1. 创建小说

- 意图：`创建一本玄幻小说，名字叫《星河烬》，200章`
- 调用：`POST /api/open/v1/novels`

```json
{
  "title": "星河烬",
  "genre": "玄幻",
  "description": "少年在破碎星域中重铸秩序。",
  "total_chapters": 200
}
```

返回 `novel_id`。创建成功后**主动问用户**："要现在让 AI 写第一章吗？"

### 2. 查找小说

- 意图：`查一下"星河"相关的书`
- 调用：`GET /api/open/v1/novels?query=星河&page=1&page_size=10`
- 返回包含 `reader_url`（阅读）和 `universe_url`（叙事宇宙），有链接时格式化为 Markdown 提供给用户。

### 3. 查看小说详情

- 调用：`GET /api/open/v1/novels/{novel_id}`
- 返回 `reader_url`（阅读入口）和 `universe_url`（影响力榜、入书名单、历史投票），两个链接都展示给用户。

### 4. 查看章节目录

- 意图：`看《星河烬》最近10章目录`
- 调用：先查书拿 `novel_id`，再 `GET /api/open/v1/novels/{novel_id}/chapters?limit=10`
- 支持 `cursor` 分页，`limit` 最大 100。

### 5. 阅读具体章节

- 意图：`看《星河烬》第12章`
- 调用：`GET /api/open/v1/novels/{novel_id}/chapters/12`
- 返回 `content`、`reader_url` 等；直接呈现正文，不显示质量分数。

### 6. 触发续写（异步）

- 意图：`帮我续写下一章`
- 调用：`POST /api/open/v1/novels/{novel_id}/generate-next`（可选 `{"with_review": true}`）
- 返回 `job_id`，立即告知用户"AI 开始写了，大约 1-3 分钟，我盯着进度……"，然后轮询。
- **配额**：免费账号 10 章/天，次日零点重置。

### 7. 查询生成进度

- 调用：`GET /api/open/v1/jobs/{job_id}`

| status / stage | 说什么 |
|---|---|
| `queued` | "排队中，马上开始…" |
| `running` / `writing` | "AI 正在创作正文…" |
| `running` / `reviewing` | "正文写好了，正在质量评估…" |
| `running` / `polishing` | "AI 正在优化…" |
| `completed` | "写完了！"+ 拉取并展示章节内容 + 提供 `reader_url` / `universe_url` |
| `failed` | "这次失败了，要重试吗？" |

轮询节奏：每 5 秒一次，10 分钟未完成视为异常。

## 错误处理

| 错误码 | 向用户说什么 |
|--------|-------------|
| `unauthorized` | "认证失败，请确认 API Key 前缀为 `oc_`" |
| `not_found` | "没找到，要先列一下目录确认编号？" |
| `quota_exceeded` | "今天配额用完了（10章/天），明天零点后恢复" |
| `rate_limited` | "频率有点高，等 30 秒再试" |
| `idempotency_in_progress` | "上次任务还在跑，继续跟进原任务" |
| `bad_request` | "参数有问题，帮你确认一下" |

## 互动原则

- 创建书后主动问是否续写；完成后提供 `reader_url` 和 `universe_url`。
- 续写过程中持续播报阶段，不让用户干等。
- 有链接时用 Markdown 格式：`[阅读](URL)` / `[叙事宇宙](URL)`。
- 语言跟随用户输入。
