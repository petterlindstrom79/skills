---
name: provider-sync
description: "Review and sync one provider's models and related fields into a local OpenClaw config file. Usage: /provider_sync [provider=<id>] [mode=dry-run|check-only|apply]"
user-invocable: true
license: MIT
spdx: MIT
---

# Provider Sync

**触发方式：在聊天里输入 `/provider_sync`**

Sync upstream provider metadata into local OpenClaw config with a review-first workflow.

## v2.0.0 重要变更（Breaking）
- 默认会**裁剪**（prune）`agents.defaults.models`：让 `/models` 的菜单条目数 **永远与** `models.providers.<provider>.models`（上游真实返回）对齐。
- 如你希望保留旧行为（不删除白名单条目），使用 `--no-prune-agent-aliases`。

## What it does

- fetches upstream provider metadata or model lists
- maps and normalizes model entries for OpenClaw
- previews diffs before any real write
- writes minimal changes to one provider subtree and creates a backup

## Slash command (规范流程)

### Scope / 权限收紧（你已确认启用）

- **群聊**：只允许 `dry-run` / `check-only`（只读）。
- **私聊**：允许 `dry-run` + `apply` + `新增 provider` + `重启`。
- 群聊中如果触发 `apply` / `新增 provider` / `重启`：直接拒绝，并提示“请私聊操作”。

This skill is **user-invocable** as: `/provider_sync` (note the underscore).

Design goals:

- **Always dry-run first** → show diff summary → explicit confirmation → apply.
- Default to **provider-scoped writes only** (`models.providers.<provider-id>`).
- Treat **Gateway restart** as a separate, explicit step.

### Canonical usage

- Interactive wizard (recommended):
  - `/provider_sync`
- Dry-run (default):
  - `/provider_sync provider=<id>`
- Check-only:
  - `/provider_sync provider=<id> mode=check-only`
- Apply (still gated by an explicit confirmation step; button tap is acceptable confirmation):
  - `/provider_sync provider=<id> mode=apply`

Supported args (all optional unless noted):

- `provider=<id>` (required)
- `config=<path>` (default: `/root/.openclaw/openclaw.json`)
- `endpoint=<url>` (default: derived from provider baseUrl: `${baseUrl}/models`)
- `mapping=<path>` (default: `{baseDir}/references/mapping.openai-models.json`)
- `mode=dry-run|check-only|apply` (default: `dry-run`)
- `normalize=1|0` (default: `1`)
- `profile=generic|gemini` (default: `generic`)
- `preserve=1|0` (default: `1`)
- `probe=openai-responses,openai-completions` (optional)

### Interaction rule (when args missing)

If `provider` is missing, **do not guess**.

On Telegram (inline buttons enabled), first send a short **greeting + identity** line so the user knows what this skill is, then present **inline button choices**.

### Productized Telegram copy（更顺口，但不油腻）

目标：默认 1 条消息讲清楚；不刷屏；关键节点（写配置/重启）二次确认；细节按需展开。
- Telegram 优先“单条面板”：尽量编辑（edit）同一条消息来更新状态/按钮（运行中→完成→确认页），只有在需要保留回执或编辑受限时才新发消息。

**/provider_sync（无参数）— 欢迎 + 引导 + buttons（推荐 2~3 行）：**
- 「Provider Sync 在这。」
- 「我帮你把上游模型列表拉下来对比一下，看看本地配置要不要更新。」
- 「默认先预览（dry-run）：不写配置、不重启。选一个 provider 开始：」

**Small-speed optimization:** tapping a provider button should immediately run the **dry-run** (no extra “go/continue” step).

**Perceived-speed optimization（Telegram）：** always send an immediate ACK before doing any non-trivial work.
- 对所有按钮回调（dry-run/apply/确认写入/重启/默认模型切换/新增provider向导），都先秒回一条「收到，正在处理…」，再执行实际操作；避免用户误以为没点上。

**点了 provider 之后 — 开跑提示（2 行）：**
- 「收到，我开始跑预览：拉模型列表 → 对比差异（不写配置）。」
- 「如果超过 10 秒还没出结果，我会回来报个进度。」

**运行超过 10s — 进度提示（只发一次，别刷屏）：**
- 「还在跑，别急。一般是上游接口/网络慢，或者列表比较大；我拿到结果马上回。」

**结果文案（建议）：**
- 无变更（diff=0）：
  - 「搞定：这次没变化 ✅ 本地配置已经是最新的。」
  - 直接展示“本地现有 models”（让用户知道具体是哪几个）：
    - 模型数量少（<=8 个）→ **换行列表**
    - 模型数量多（>8 个）→ 单行用 ` / ` 分隔，只展示前 8 个 + 「…等共 M 个」
  - 排障信息（endpoint/cache/耗时）默认不发，放到「详情」里。
- 有变更（只给计数 + 下一步）：
  - 「跑完了：发现有变化，但我还没写配置。」
  - 「新增 {addCount}、移除 {removeCount}、更新 {updateCount}。要不要 Apply 写进去？（写之前会先备份）」

**Apply（写配置）— 二次确认建议文案：**
- 第一次点 Apply → 进入确认页：
  - 「确认一下：你要我把这些变更写进配置文件吗？我会先自动备份一份，方便回滚。」
  - 「写完也不会自动重启；重启要你再点一次（防手滑）。」

**Restart（重启）— 二次确认建议文案：**
- 第一次点“重启…” → 进入确认页：
  - 「再确认一次：现在要重启 Gateway 吗？」
  - 「我多问一句是为了防手滑——重启会短暂中断对话/任务。确定再点“确认重启”。」

**Details（按需展开，不默认刷屏）：**
- 默认不发 endpoint/cache/timeout。
- 用户点「详情」(`ps:d:<providerId>`) 或发生错误时，再发一条“详情”消息，包含（全部脱敏）：
  - provider / endpoint / HTTP status
  - cache: on/off + hit + ttl/age（不展示任何密钥）
  - timing: fetchMs / totalMs
  - timeout 值
- 用户点「收起详情」(`ps:dx`) 后：回一条「OK，已收起。」即可。

**Recommended button layout（Telegram）：**
- 第一屏（provider picker）：`cliplus` / `cli-usa` / `newapi` / `新增 provider` / `取消`
- 运行中：`详情` / `取消`
- 结果屏（无变更）：`切换 provider` / `详情` / `结束`
- 结果屏（有变更）：`Apply` / `详情` / `切换 provider` / `结束`
- 错误屏：`重试` / `详情` / `切换 provider` / `结束`

**可选功能：🧹 清理 `/models`（让菜单“变干净”）**
- 背景：当 `models.mode = "merge"` 时，`/models` 会把“内置 catalog + 你的 provider 配置”合并展示，容易出现“provider-sync 显示 4 个，但 /models 显示 22 个”的割裂。
- 解决：提供一个按钮把 `models.mode` 切到 `"replace"`（只展示配置文件里显式定义的 models）。
- 安全：这是 **全局配置**（影响所有 provider 的模型目录展示），必须 **二次确认** 后才写入；写入前自动备份；写入后不自动重启（重启另按一次确认）。
- 推荐放置：在“结果屏（无变更）”也可以提供 `🧹 清理 /models` 按钮（仅当当前 `models.mode` 不是 `replace` 时显示）。

**Add new provider (私聊限定，需二次确认)：**
- 入口按钮：`新增 provider`（callback 建议：`ps:add`）
- 交互：优先按“知名 provider 默认 URL”给快捷选择；其他 provider 让用户手填 baseUrl。

**知名 provider 默认 URL（最小集合，避免不兼容坑）：**
- `openai` → 官方：`https://api.openai.com/v1`（OpenAI 兼容）
- `gemini` → 先确认「官方原生 / 中转(OpenAI兼容)」
  - 官方原生：`https://generativelanguage.googleapis.com/v1beta`（通常需 `x-goog-api-key`；不一定兼容 `/v1/models` 流程）
  - 中转(OpenAI兼容)：用户提供 `.../v1`
- `anthropic` → 不直接给官方 URL（非 `/v1/models` 口径），默认引导走「中转(OpenAI兼容)」并让用户提供 `.../v1`

- 交互：询问并收集 `providerId` / `baseUrl` / `apiKey(可选，不回显)`
- 安全流程：
  1) 先用给定 baseUrl 跑一次 dry-run 拉 `/models`（验证可用）
  2) 用户确认后再写入 `models.providers.<providerId>`（写前备份）
  3) 写入后再单独询问是否重启
- 群聊：不提供该入口（避免误触写配置）。

**Tone（输出规则）：**
- 先结论后细节：第一行先说“没变化/有变化/失败”。
- 每条尽量 2~3 行；长列表只在“详情/差异”里展开。
- 术语少用：`cacheHit` → 「命中缓存/没命中，需要真去拉一次」；`fetchMs/totalMs` → 「拉接口 Xms / 总共 Yms」。
- 永不展示 apiKey / Authorization / Cookie。

**Real-speed optimization (script):** `scripts/provider_sync.py` includes a local cache (TTL + ETag/Last-Modified conditional requests). Tune with `--cache-ttl-seconds` (default 600), `--cache-dir`, and disable via `--no-cache`. Also supports `--timeout` for slow upstreams.

- Provider picker buttons: `ps:p:<providerId>` → immediately run dry-run
- Provider picker extra:
  - `ps:add` (start add-new-provider wizard; private chat only)
- Post dry-run buttons:
  - `ps:ap:<providerId>` (apply → go to confirm page)
  - `ps:apc:<providerId>` (apply confirm → write config)
  - `ps:pick` (switch provider)
  - `ps:done` (finish)
  - `ps:cn` (cancel)
  - `ps:d:<providerId>` (details: show endpoint/cache/timeout/timing; never show apiKey)
  - `ps:dx` (details: hide)
- Restart picker buttons (after apply):
  - `ps:rs:prep` (restart → go to confirm page)
  - `ps:rs:yes` (restart confirm)
  - `ps:rs:no` (not now)

- Clean `/models` (toggle catalog mode; global):
  - `ps:mm:prep` (models.mode change → go to confirm page)
  - `ps:mm:yes` (confirm: set `models.mode` to `replace`)
  - `ps:mm:no` (cancel models.mode change)

- Prune provider whitelist (彻底对齐 `/models` 的计数):
  - `ps:wl:prep:<providerId>` (go to confirm page)
  - `ps:wl:yes:<providerId>` (confirm: prune `agents.defaults.models` entries for this provider to match `models.providers.<providerId>.models`)
  - `ps:wl:no` (cancel)

- Default text model switch (after apply, optional):
  - `ps:dm:keep` (keep existing `agents.defaults.model`)
  - `ps:dm:skip` (do nothing for now)
  - `ps:dm:pick:<providerId>` (pick a model from this provider to set as default text model)
  - `ps:dm:set:<providerId>:<idx>` (select model by index from `models.providers.<providerId>.models`)
  - `ps:dm:apply:<providerId>:<idx>` (confirm + write `agents.defaults.model`)

Telegram callback clicks are delivered back as an inbound message:

- `callback_data: ps:p:cliplus`

Parse that and continue the flow.

## Inputs and access

- This skill reads a local OpenClaw config file and may write provider-scoped changes after confirmation.
- Always confirm the target config path before a real write.
- A common path is `/root/.openclaw/openclaw.json`, but do not assume it blindly.
- Protected upstream endpoints may require explicit headers such as `Authorization`.
- Credentials should come from the user or an already configured local environment; never print secrets in summaries or logs.

## Safe workflow (agent execution)

1. **Parse args** from the slash command message.
2. **Resolve config path** (default `/root/.openclaw/openclaw.json`). If the file does not exist, stop and ask for the correct path.
3. **Resolve provider**:
   - Read available provider ids from `models.providers` in the config.
   - If the requested provider id is missing, show the list and stop.
4. **Resolve endpoint**:
   - If the user provided `endpoint=...`, use it.
   - Otherwise, read `models.providers.<provider-id>.baseUrl` and set:
     - `endpoint = <baseUrl>.rstrip('/') + '/models'`

5. **Auth header (avoid one extra round-trip)**:
   - If `models.providers.<provider-id>.apiKey` exists, add:
     - `Authorization: Bearer <apiKey>`
   - This prevents an initial 401 → retry cycle.
5. **Resolve mapping**:
   - Default to `{baseDir}/references/mapping.openai-models.json`.
6. **Run dry-run first** (or check-only), always with machine-readable output:

```bash
python3 {baseDir}/scripts/provider_sync.py \
  --config <config> \
  --provider-id <provider> \
  --use-provider-config \
  --mapping-file <mapping> \
  --normalize-models \
  --preserve-existing-model-fields \
  --normalize-profile <generic|gemini> \
  --probe-api-modes <optional> \
  --output json \
  --dry-run

# 彻底对齐（可选）：同时裁剪白名单，让 `/models` 计数=真实 provider models
# （仍建议先 dry-run）
#   --prune-agent-aliases   # 现在默认开启；如需保留旧白名单可用 --no-prune-agent-aliases
```

Notes:
- `--use-provider-config` will derive `endpoint` from `models.providers.<id>.baseUrl` and add `Authorization: Bearer <apiKey>` automatically when available.
- By default JSON output is **summary-only** (no full model list). Add `--include-models` if you need per-model detail.

7. **Summarize**:
   - Changed paths count (`changes`)
   - Model delta: added/removed/changed ids
   - Probe results (if present) and picked mode

8. **Apply gate**:
   - If the user explicitly confirms (either by typing `apply`/`yes` **or tapping an Apply inline button**), re-run the same command **without** `--dry-run`.
   - After apply, report the backup path and updated config path.

9. **Restart gate (separate)**:
   - Offer two inline buttons: Restart / Not now.
   - Only restart after explicit confirmation.
   - **Telegram UX rule:** when the user taps Restart, **send an acknowledgement message first** (e.g. "收到，正在重启…") and only then restart the Gateway. The restart may terminate the current in-flight request, so the ack must be sent before the restart.

10. **可选：清理 `/models`（全局 catalog 行为）**：
   - 触发方式：用户点 `ps:mm:prep` → 进入确认页（`ps:mm:yes` / `ps:mm:no`）。
   - 动作：在 `ps:mm:yes` 后写入 `models.mode = "replace"`（写前备份；不自动重启）。
   - 实现建议：优先用“安全写配置”链路（例如 config-guardian 的 atomic apply）而不是手改 JSON。

## Main script

Use: `scripts/provider_sync.py`

Example:

```bash
python3 scripts/provider_sync.py \
  --config /root/.openclaw/openclaw.json \
  --provider-id cliplus \
  --endpoint https://api.example.com/v1/models \
  --mapping-file references/mapping.openai-models.json \
  --normalize-models \
  --preserve-existing-model-fields \
  --probe-api-modes openai-responses,openai-completions \
  --dry-run
```

## Useful flags

- `--config` — target config path
- `--check-only` — validate without writing
- `--dry-run` — preview planned changes
- `--normalize-models` — normalize upstream model entries
- `--normalize-profile gemini` — Gemini-specific normalization
- `--preserve-existing-model-fields` — keep local model capability fields where possible
- `--include-model` / `--exclude-model` — narrow model scope
- `--output json` — machine-readable summary

## Read references when needed

- `references/examples.md`
- `references/provider-patterns.md`
- `references/field-normalization.md`
- `references/gemini.md`
- `references/safety-rules.md`
- `references/mapping.example.json`

## Safety

- Prefer **check-only / dry-run → confirm → apply**.
- Do not write outside `models.providers.<provider-id>` unless explicitly requested.
- Do not auto-restart or auto-apply runtime changes by default.
- Keep backups on real writes and report raw errors if a write fails.
