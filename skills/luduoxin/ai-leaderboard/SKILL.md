---
name: AI Rankings Leaderboard
display_name: AI Rankings Leaderboard / AI 排行榜
description: Comprehensive AI leaderboard for LLM models and AI applications. Query model rankings, model IDs, and pricing from OpenRouter and Pinchbench. Trigger words include "AI rankings", "LLM leaderboard", "model comparison", "AI apps ranking", "best AI models", "model benchmark", "free models", "免费模型", "OpenRouter model ID", "OpenRouter 模型", "查找 OpenRouter", "OpenRouter 上的模型", "model ID for", "OpenRouter model parameter".
version: 1.7.0
---

# AI Rankings Leaderboard Skill

## Description

A comprehensive skill for querying AI model and application rankings from multiple authoritative sources. Get the latest insights on LLM performance, popularity, pricing, and value metrics.

## Data Sources

| Source | URL | Focus |
|--------|-----|-------|
| OpenRouter Rankings | https://openrouter.ai/rankings | Model usage & popularity |
| OpenRouter Apps | https://openrouter.ai/apps | AI applications ranking |
| OpenRouter Models | https://openrouter.ai/models | All available models with pricing |
| OpenRouter Free Models | https://openrouter.ai/models?q=free | Free models only |
| Pinchbench | https://pinchbench.com/ | Model benchmark (Success Rate, Speed, Cost, Value) |

## Features

### 1. OpenRouter Model Rankings
- **LLM Leaderboard**: Overall model usage rankings
- **Market Share**: Market share by model provider
- **Categories**: Rankings by use case
- **Languages**: Natural language support rankings
- **Programming**: Programming language support
- **Context Length**: Long context handling
- **Tool Calls**: Tool calling capabilities
- **Images**: Image processing volume

### 2. OpenRouter App Rankings
- **Most Popular**: Top apps by token usage
- **Trending**: Fastest growing apps this week
- **Categories**: Coding Agents, Productivity, Creative, Entertainment

### 3. OpenRouter Model Catalog
- **All Models**: Complete list of available models on OpenRouter
- **Free Models**: Models with $0 pricing (free to use)
- **Model ID**: The exact `model` parameter to use when calling OpenRouter API
- **Pricing Info**: Input/output token pricing

### 4. Pinchbench Benchmarks
- **Success Rate**: Task completion success percentage
- **Speed**: Response time performance
- **Cost**: Cost per run analysis
- **Value**: Price-performance ratio

## Trigger Keywords

- "AI rankings" / "AI 排行榜"
- "LLM leaderboard" / "LLM 排行"
- "model comparison" / "模型对比"
- "best AI models" / "最好的 AI 模型"
- "AI apps ranking" / "AI 应用排行"
- "model benchmark" / "模型评测"
- "free models" / "免费模型" / "free AI models"
- "OpenRouter models" / "OpenRouter 免费模型"
- "OpenRouter rankings" / "OpenRouter 排行"
- "Pinchbench"
- "OpenRouter model ID" / "OpenRouter 模型 ID"
- "查找 OpenRouter" / "OpenRouter 上的模型"
- "model ID for [模型名]" / "[模型名] model ID"
- "OpenRouter 上 [模型名]" / "OpenRouter [模型名] 模型"
- "OpenRouter model parameter"
- "调用量排行" / "使用量排行" / "top models" / "top 模型"
- "OpenRouter 调用量" / "OpenRouter 使用量"

## Runtime Tools

This skill requires:
- `execute_command`: Execute shell commands and scripts
- `use_skill`: Load browser-automation skill for JavaScript-rendered pages
- `web_fetch`: Fallback for simple HTTP requests

## Browser Automation Support

For JavaScript-rendered pages (OpenRouter Rankings), this skill uses browser automation:

1. **Load browser-automation skill first**:
   ```
   use_skill("browser-automation")
   ```

2. **Navigate to rankings page**:
   ```bash
   agent-browser open "https://openrouter.ai/rankings"
   agent-browser wait --load networkidle
   agent-browser eval "document.body.innerText"
   ```

3. **Key pages requiring browser**:
   - `https://openrouter.ai/rankings` - Model usage rankings (JS rendered)
   - `https://openrouter.ai/apps` - App rankings (JS rendered)

### ⚠️ Critical: Clicking "Show more" Button

The rankings page only shows **Top 10 by default**. To get Top 20+, you must click the "Show more" button.

**❌ WRONG METHODS (do NOT use):**
```bash
# These methods DO NOT work:
agent-browser click @e41                           # ref ID changes, unreliable
agent-browser find role button click --name "Show more"  # fails to click correctly
```

**✅ CORRECT METHOD - Use JavaScript with exact text match:**
```bash
# Step 1: Open page and wait for load
agent-browser open "https://openrouter.ai/rankings" && agent-browser wait --load networkidle

# Step 2: Click "Show more" using JavaScript (CRITICAL: must use exact text match)
agent-browser eval "const buttons = document.querySelectorAll('button'); for(let b of buttons) { if(b.innerText === 'Show more') { b.click(); break; } }"

# Step 3: Wait for content to load, then extract
agent-browser wait 3000 && agent-browser eval "document.body.innerText"

# Step 4: Close browser when done
agent-browser close
```

**Why this works:**
- `b.innerText === 'Show more'` ensures exact match (not "Show more..." or similar)
- Using `for...of` loop with `break` clicks only the first matching button
- 3 second wait allows React to re-render the expanded list

### ⚠️ Critical: Parse "LLM Leaderboard" Section Only

The OpenRouter rankings page contains **multiple sections**. When parsing usage data, you must extract from the **"LLM Leaderboard"** section only.

**Page Structure:**
```
https://openrouter.ai/rankings
├── Top Models (chart header)
├── LLM Leaderboard ← THIS is the usage ranking (parse this!)
│   ├── 1. MiniMax M2.5 (1.75T tokens)
│   ├── 2. Step 3.5 Flash (1.34T tokens)
│   ├── ... (Top 10 default, Top 20+ after "Show more")
│   └── [Show more] button
├── Market Share (different metric - don't mix!)
├── Categories (different metric)
├── Languages (different metric)
├── Top Apps (AI applications, not models)
└── ...
```

**⚠️ Common Parsing Mistake:**

When extracting Top 20, the page text may contain data from multiple sections. You must:

1. **Find the "LLM Leaderboard" heading** in the text
2. **Parse only the model list immediately after it** (numbered 1-20)
3. **Stop at "Market Share"** or next section heading

**Correct parsing approach:**
```
LLM Leaderboard section content:
"This Week
1.
MiniMax M2.5
by
minimax
1.75T tokens
6%
2.
Step 3.5 Flash (free)
..."

Parse pattern:
- Rank: number followed by "."
- Model: next line after rank
- Provider: line after "by"
- Tokens: line with "tokens"
- Change: percentage or "new"
```

**Do NOT mix data from:**
- Market Share (token share by provider, not individual models)
- Categories (rankings by use case)
- Top Apps (applications, not models)

## Usage Examples

### Query Model Rankings
```
User: "What are the top 10 AI models right now?"
-> Fetches OpenRouter rankings and displays top models with usage stats
```

### Query Free Models
```
User: "What free models are available on OpenRouter?"
-> Fetches https://openrouter.ai/models?q=free and lists all free models with their model IDs
```

### Get Model ID for API Calls
```
User: "What's the model ID for GPT-4o on OpenRouter?"
-> Fetches https://openrouter.ai/models and returns the exact model parameter to use
```

### Compare Model Performance
```
User: "Compare GPT-4 and Claude on Pinchbench"
-> Fetches Pinchbench data and compares success rate, speed, cost
```

### Find AI Applications
```
User: "What are the most popular AI coding agents?"
-> Fetches OpenRouter apps ranking filtered by coding category
```

### Value Analysis
```
User: "Which model has the best value on Pinchbench?"
-> Fetches Pinchbench Value tab data
```

## Output Format

### Model Rankings
```
==================================================
    AI Model Rankings (OpenRouter)
==================================================

Top 10 Models by Usage:

| Rank | Model | Provider | Tokens | Growth |
|------|-------|----------|--------|--------|
| 1 | GPT-4o | OpenAI | 2.5T | +15% |
| 2 | Claude 3.5 Sonnet | Anthropic | 1.8T | +22% |
...

Data Source: OpenRouter (Weekly Rankings)
==================================================
```

### Free Models List
```
==================================================
    Free Models on OpenRouter
==================================================

| Model Name | Model ID (for API) | Context |
|------------|-------------------|---------|
| GPT-4o Mini | openai/gpt-4o-mini | 128K |
| Llama 3.3 70B | meta-llama/llama-3.3-70b-instruct | 128K |
| DeepSeek V3 | deepseek/deepseek-chat | 64K |
...

💡 Usage: Set model parameter to the Model ID value
   Example: model="openai/gpt-4o-mini"

Data Source: OpenRouter Models
==================================================
```

### All Models with Pricing
```
==================================================
    OpenRouter Model Catalog
==================================================

| Model | Model ID | Input $/1M | Output $/1M |
|-------|----------|------------|-------------|
| GPT-4o | openai/gpt-4o | $2.50 | $10.00 |
| Claude 3.5 Sonnet | anthropic/claude-3.5-sonnet | $3.00 | $15.00 |
...

💡 Free models have $0.00 pricing
==================================================
```

### Application Rankings
```
==================================================
    AI Applications Rankings (OpenRouter)
==================================================

| Rank | App | Category | Usage |
|------|-----|----------|-------|
| 1 | Cursor | IDE Extension | 10.7T |
| 2 | Windsurf | IDE Extension | 5.2T |
...

Categories: Coding Agents, Productivity, Creative
==================================================
```

### Benchmark Results
```
==================================================
    Model Benchmark (Pinchbench)
==================================================

Success Rate Top 5:

| Rank | Model | Success % | Score |
|------|-------|-----------|-------|
| 1 | Claude 3.5 Sonnet | 95.2% | 95.2 |
| 2 | GPT-4o | 94.8% | 94.8 |
...

Tab: Success Rate | Speed | Cost | Value
==================================================
```

## Execution Instructions

### Method 1: Browser Automation for Rankings (Recommended for Top Models)

OpenRouter rankings page requires JavaScript rendering. Use browser-automation:

```bash
# Step 1: Load browser-automation skill (REQUIRED)
# The AI should call: use_skill("browser-automation")

# Step 2: Navigate to rankings page
agent-browser open "https://openrouter.ai/rankings" && agent-browser wait --load networkidle

# Step 3: Click "Show more" to expand from Top 10 to Top 20 (CRITICAL!)
agent-browser eval "const buttons = document.querySelectorAll('button'); for(let b of buttons) { if(b.innerText === 'Show more') { b.click(); break; } }"

# Step 4: Wait and extract content
agent-browser wait 3000 && agent-browser eval "document.body.innerText"

# Step 5: Close browser when done
agent-browser close
```

**⚠️ Important Notes:**
- Default view shows only **Top 10**. Must click "Show more" to get Top 20+
- Using `agent-browser click @ref` or `find role button` may NOT work correctly
- **Always use JavaScript with `innerText === 'Show more'`** for reliable clicking

**Browser automation is needed for**:
- Top Models (weekly usage rankings)
- Market Share by provider
- App Rankings
- Any JS-rendered content

### Method 2: Python Script for Model Catalog

Use the `query_leaderboard.py` script to fetch model data via OpenRouter API (no JavaScript needed):

```bash
# List free models
python3 "${SKILL_DIR}/query_leaderboard.py --free"

# Search models by name
python3 "${SKILL_DIR}/query_leaderboard.py -s glm"
python3 "${SKILL_DIR}/query_leaderboard.py -s gpt"

# Get specific model info
python3 "${SKILL_DIR}/query_leaderboard.py --id openai/gpt-4o"

# List all models with limit
python3 "${SKILL_DIR}/query_leaderboard.py --all --limit 50"
```

### Method 2.5: Python Script with Browser Automation

Use `fetch_rankings.py` for automated browser-based ranking queries:

```bash
# Get top models ranking (requires browser-automation skill loaded)
python3 "${SKILL_DIR}/fetch_rankings.py"

# Get apps ranking
python3 "${SKILL_DIR}/fetch_rankings.py --apps"
```

Note: This script wraps agent-browser CLI commands.

### Method 3: Web Fetch (Fallback)

When browser/Python is not available, use `web_fetch`:

1. **For model catalog**: Use OpenRouter API `https://openrouter.ai/api/v1/models`
2. **For benchmarks**: Fetch `https://pinchbench.com/`

**Note**: OpenRouter rankings page (`/rankings`) requires JavaScript rendering - use browser automation (Method 1).

**Important**: When displaying model information, always include the `Model ID` (the exact string to pass as the `model` parameter when calling OpenRouter API).

## Notes

- Data is updated regularly (OpenRouter weekly, Pinchbench near real-time)
- Pinchbench disclaimer: "For entertainment purposes only, should not be relied upon for critical decisions"
- Rankings reflect actual usage data from millions of users
- Free models have $0.00 pricing on OpenRouter
- **Model ID format**: Use the exact string (e.g., `openai/gpt-4o-mini`) as the `model` parameter in API calls

## OpenRouter API Usage

When calling OpenRouter API, use the Model ID:

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o-mini",  # <- Model ID from this skill
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Changelog

### v1.7.0
- **Security fix**: Removed `shell=True` from subprocess.run() in fetch_rankings.py
- Changed to use `subprocess.run(['agent-browser', 'arg1', 'arg2', ...])` format
- All commands are now hardcoded lists, preventing command injection
- Added security documentation to script

### v1.6.0
- **Critical**: Documented page structure - "LLM Leaderboard" is the usage ranking section
- Added page structure diagram showing multiple sections (Market Share, Categories, Top Apps)
- Added parsing guidance: extract from "LLM Leaderboard" section only, stop at "Market Share"
- Clarified that other sections have different metrics, should not be mixed

### v1.5.0
- **Critical fix**: Documented correct method to click "Show more" button
- Added troubleshooting for button clicking (ref ID unreliable, find role fails)
- Must use JavaScript `innerText === 'Show more'` for reliable clicking
- Default view is Top 10, clicking "Show more" expands to Top 20+

### v1.4.0
- Added browser-automation support for JavaScript-rendered pages
- Added display_name with Chinese/English bilingual support
- Reorganized execution methods with clear priority
- Browser automation is now the primary method for rankings queries

### v1.3.0
- Added Python script `query_leaderboard.py` using OpenRouter API
- Fixed JavaScript rendering issue for rankings page
- Improved model search and filtering capabilities
- Added free models detection

### v1.2.0
- Enhanced trigger keywords for model ID queries
- Added Chinese/English bilingual support

### v1.1.0
- Added free models query support
- Added all models catalog with pricing
- Added Model ID field for API usage
- Updated data sources and trigger keywords

### v1.0.0
- Initial release
- Support for OpenRouter rankings, apps, and Pinchbench benchmarks
- Multiple ranking dimensions: usage, success rate, speed, cost, value
