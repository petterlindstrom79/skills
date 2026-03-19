---
name: iterative-code-review
displayName: Iterative Code Review
description: |
  Iterative code review using multiple independent subagent reviews. Use when user asks to review PR, code, or mentions "review", "审查", "检查代码", "代码质量". Automatically fixes all issues through review-fix-review cycles until consecutive two rounds have no new issues.
license: MIT
version: 2.7
metadata:
  {"openclaw":{"emoji":"🔍","category":"code-quality"}}
---

# Code Review Skill

Iterative code review through **parallel independent subagent reviews** until all issues are resolved.

## Core Principle

**Every review round spawns 3 PARALLEL subagents** - Maximizes issue detection, ensures comprehensive coverage.

---

## ⚠️ Pre-flight Checks

### Check 1: Model (CRITICAL)

**推荐使用当前代码能力最强的模型，由用户决定！**

**要求**：
- `thinking: "high"` - **必须启用**，提高审查质量
- 推荐模型（按代码能力排序）：
  1. `bailian/glm-5` - 推荐，代码能力强
  2. `bailian/qwen3.5-plus` - 备选
  3. 其他用户指定的模型

**实现方式**：

```javascript
// 推荐模型列表（按代码能力排序）
const RECOMMENDED_MODELS = [
  { id: 'bailian/glm-5', name: 'GLM-5', reason: '代码能力强，推荐' },
  { id: 'bailian/qwen3.5-plus', name: 'Qwen 3.5 Plus', reason: '备选' }
];

// 询问用户选择模型
console.log(`
🔍 Model 选择

推荐模型（按代码能力排序）：
${RECOMMENDED_MODELS.map((m, i) => `${i + 1}. ${m.id} - ${m.reason}`).join('\n')}

请选择模型（输入编号或完整模型 ID），默认使用 ${RECOMMENDED_MODELS[0].id}：
`);

const userChoice = await waitForUserInput();
let selectedModel;

if (!userChoice || userChoice.trim() === '') {
  selectedModel = RECOMMENDED_MODELS[0].id;
  console.log(`✅ 使用默认模型: ${selectedModel}`);
} else if (/^\d+$/.test(userChoice.trim())) {
  const index = parseInt(userChoice.trim(), 10) - 1;
  if (index >= 0 && index < RECOMMENDED_MODELS.length) {
    selectedModel = RECOMMENDED_MODELS[index].id;
    console.log(`✅ 使用模型: ${selectedModel}`);
  } else {
    console.log(`⚠️ 无效编号，使用默认模型: ${RECOMMENDED_MODELS[0].id}`);
    selectedModel = RECOMMENDED_MODELS[0].id;
  }
} else {
  selectedModel = userChoice.trim();
  console.log(`✅ 使用用户指定模型: ${selectedModel}`);
}

// Spawn 时必须启用 thinking: "high"
sessions_spawn({
  runtime: "subagent",
  model: selectedModel,
  thinking: "high",  // ⚠️ 必须启用
  task: `...`
});
```

**关键规则**：
1. **thinking: "high"** - 必须启用，不可跳过
2. **用户决定模型** - 推荐但不强制
3. **默认模型** - 如果用户不选择，使用推荐的第一个模型

### Check 2: maxSpawnDepth

```bash
openclaw config get agents.defaults.subagents.maxSpawnDepth
```

| Value | Status |
|-------|--------|
| `≥1` | ✅ Proceed |
| `0` | ❌ Abort - inform user to update config |

### Check 3: 变更规模检测（动态超时）

根据变更规模自动调整超时时间：

```bash
# 检测变更文件数量
CHANGED_FILES=$(git diff --name-only origin/develop HEAD | wc -l)
```

| 规模 | 文件数 | Reviewer 超时 | Fixer 超时 |
|------|--------|--------------|-----------|
| 小型 | <10 | 2 分钟 | 3 分钟 |
| 中型 | 10-50 | 3 分钟 | 5 分钟 |
| 大型 | >50 | 5 分钟 | 8 分钟 |

**实现方式**：
```javascript
const changedFiles = execSync('git diff --name-only origin/develop HEAD | wc -l').toString().trim();
const fileCount = parseInt(changedFiles, 10);

let reviewerTimeout, fixerTimeout;
if (fileCount < 10) {
  reviewerTimeout = 120; fixerTimeout = 180;
} else if (fileCount < 50) {
  reviewerTimeout = 180; fixerTimeout = 300;
} else {
  reviewerTimeout = 300; fixerTimeout = 480;
}
```

### Check 4: 新增代码识别（⚠️ 关键！）

**必须识别本次 PR 新增的代码，而非只关注"修复了什么"！**

```bash
# 检测新增代码行数
git diff origin/develop HEAD --stat | tail -1
```

**为什么重要？**

历史教训：PR #64 经过 7 轮 review 后，重新审查仍发现 22 个新问题。原因：
- 之前的 review 只关注"修复了什么"
- **忽略了新增代码（+684 行）的问题**

**新增代码审查清单**：

| 检查项 | 说明 |
|--------|------|
| 新增代码的安全性 | 加密、输入验证、权限检查 |
| 新增代码的测试覆盖 | 是否有对应单元测试 |
| 新增代码的边界条件 | 空值、极端情况、错误处理 |
| 新增代码的资源清理 | 定时器、内存、连接 |

**实现方式**：
```javascript
// 在 spawn reviewer 时，明确告知新增代码范围
const newCodeStats = execSync('git diff origin/develop HEAD --shortstat').toString();
const newFiles = execSync('git diff --name-only --diff-filter=A origin/develop HEAD').toString();

// 在 reviewer task 中包含：
`
## ⚠️ 新增代码审查（必须检查！）

本次 PR 新增代码统计：
${newCodeStats}

新增文件：
${newFiles}

**必须检查新增代码的**：
1. 安全性（加密、输入验证、权限）
2. 测试覆盖
3. 边界条件
4. 资源清理
`
```

### Check 5: PR 历史检查（⚠️ 关键！避免重复发现问题）

**在开始 Review 前，必须读取 PR 的 commit history！**

```bash
# 获取 PR 的 commit history
git log --oneline origin/develop..HEAD

# 获取最近 N 个 commit 的详细 message
git log --oneline -10 origin/develop..HEAD
```

**为什么重要？**

历史教训（PR #64）：
- PR 已经经过 Round 1-7 的 review
- 有 17+ 个 commits 修复了各种问题
- 新的 review 没有检查历史，把已修复的问题当成"新问题"
- **浪费了用户时间，造成困惑**

**必须读取的信息**：

```bash
# 1. 查看 commit messages，了解已修复的问题
git log --oneline origin/develop..HEAD

# 2. 查看最近一个 commit 的变更（delta review）
git show --stat HEAD

# 3. 查看 PR 信息
gh pr view <number> --json title,body,commits
```

**实现方式**：

```javascript
// Pre-flight Check 5: PR 历史检查
const commits = execSync('git log --oneline origin/develop..HEAD').toString().trim();
const commitCount = commits.split('\n').length;
const lastCommitMsg = execSync('git log -1 --pretty=format:"%s%n%b" HEAD').toString();

// 输出历史摘要给用户
console.log(`
📋 PR 历史摘要
├─ Total commits: ${commitCount}
├─ Latest commit: ${lastCommitMsg.split('\n')[0]}
└─ Full history:
${commits}
`);

// 解析已修复的问题
const fixedIssues = parseFixedIssues(commits);
console.log(`
✅ 已修复的问题（不需要再检查）：
${fixedIssues.map(i => `- ${i}`).join('\n')}
`);
```

**关键规则**：

1. **只 review delta** - 审查最新 commit 与上一个 commit 的差异
2. **跳过已修复的问题** - 如果 commit message 明确说已修复，不要再报告
3. **理解 PR 演进** - 知道哪些问题是新的，哪些是历史的

**Delta Review 实现**：

```bash
# Round 1: 审查 develop..HEAD 的完整变更
git diff origin/develop HEAD

# Round 2+: 只审查最新 commit 的变更
git diff HEAD~1 HEAD
```

**历史教训总结**：

```
❌ 错误做法：
- 直接开始全量 review
- 把已修复的问题当成"新问题"
- 不看 commit message，不了解 PR 演进

✅ 正确做法：
- 先读取 PR commit history
- 解析已修复的问题列表
- 只 review delta（最新变更）
- 避免重复报告已修复的问题
```

### Check 6: Review 模式选择（⚠️ 必须询问用户！）

**在开始 Review 前，根据场景决定是否询问用户选择 Review 模式！**

```bash
# 获取 commit 数量
COMMIT_COUNT=$(git log --oneline origin/develop..HEAD | wc -l)
```

**判断逻辑**：

| 场景 | 行为 | 原因 |
|------|------|------|
| **整个代码仓库 review** | 直接 Full Review | 无 PR 范围，必须全量检查 |
| **PR 只有 1 个 commit** | 直接 Full Review | 无需询问，直接全量 |
| **PR 有多个 commits** | 询问用户选择 | 让用户决定审查范围 |

**场景识别**：

```javascript
// 判断是否是整个代码仓库 review
// 如果没有指定 PR/分支，或者用户明确说"review 整个项目"，就是全仓库 review
const isFullRepoReview = !hasSpecificPR && !hasSpecificBranch;
```

**询问逻辑**：

```
// 如果是整个代码仓库 review → 直接 Full Review
if (isFullRepoReview) {
  reviewMode = 'full';
  console.log('🔍 整个代码仓库 Review，使用 Full Review 模式');
}

// 如果 PR 只有 1 个 commit → 直接 Full Review
else if (commitCount === 1) {
  reviewMode = 'full';
  console.log('✅ 只有 1 个 commit，直接 Full Review');
}

// 如果 PR 有多个 commits → 询问用户
else {
  console.log(`
🔍 Review 模式选择

本次 PR 已有 ${commitCount} 个 commits，您希望：

A. Delta Review - 只审查最新 commit（更高效）
B. Full Review - 审查所有变更（更全面）

请选择 (A/B)：
  `);
  
  const userChoice = await waitForUserInput();
  
  if (userChoice.toLowerCase() === 'a') {
    reviewMode = 'delta';
  } else if (userChoice.toLowerCase() === 'b') {
    reviewMode = 'full';
  } else {
    console.log('⚠️ 无效选择，默认使用 Delta Review');
    reviewMode = 'delta';
  }
}
```

**两种模式对比**：

| 模式 | 审查范围 | 适用场景 | 效率 |
|------|---------|---------|------|
| **Delta Review** | HEAD~1..HEAD | 多轮迭代、连续 review | 高 |
| **Full Review** | develop..HEAD 或全仓库 | 首次 review、全量检查、整个项目 review | 低 |

**关键规则**：

1. **整个代码仓库 review**：直接 Full Review，无需询问
2. **commit 数量 = 1**：直接 Full Review，无需询问
3. **commit 数量 > 1**：必须询问用户选择模式
4. **默认选择**：如果用户输入无效，默认 Delta Review
5. **Round 2+**：如果 Round 1 是 Full Review，Round 2+ 自动切换到 Delta Review

---

## ⚠️ Pre-flight Checks 输出格式

**每个 Pre-flight Check 的结果都必须输出给用户！**

```
🔍 Pre-flight Checks

┌─────────────────────────────────────────────────────────┐
│ Check 1: Model                                          │
│ ├─ 推荐模型: bailian/glm-5, bailian/qwen3.5-plus       │
│ ├─ 用户选择: bailian/glm-5                              │
│ ├─ thinking: high ✅                                    │
│ └─ Result: ✅ PASS                                      │
├─────────────────────────────────────────────────────────┤
│ Check 2: maxSpawnDepth                                  │
│ ├─ 当前值: 2                                            │
│ └─ Result: ✅ PASS (≥1)                                 │
├─────────────────────────────────────────────────────────┤
│ Check 3: 变更规模检测                                    │
│ ├─ 变更文件: 11 个                                      │
│ ├─ 规模: 中型                                           │
│ ├─ Reviewer 超时: 3 分钟                                │
│ ├─ Fixer 超时: 5 分钟                                   │
│ └─ Result: ✅ PASS                                      │
├─────────────────────────────────────────────────────────┤
│ Check 4: 新增代码识别                                    │
│ ├─ 新增代码: +684 行                                    │
│ ├─ 新增文件: 3 个                                       │
│ └─ Result: ✅ PASS                                      │
├─────────────────────────────────────────────────────────┤
│ Check 5: PR 历史检查                                     │
│ ├─ Total commits: 14                                    │
│ ├─ Latest: fix(security): ::x.x.x.x IPv4 compatible     │
│ ├─ 已修复问题: 17+ 个                                   │
│ └─ Result: ✅ PASS                                      │
├─────────────────────────────────────────────────────────┤
│ Check 6: Review 模式选择                                 │
│ ├─ 场景: PR 有多个 commits                              │
│ ├─ 用户选择: Delta Review                               │
│ └─ Result: ✅ PASS                                      │
└─────────────────────────────────────────────────────────┘

✅ All Pre-flight Checks PASSED，开始 Review...
```

**实现方式**：

```javascript
function outputPreflightResults(checks) {
  console.log(`
🔍 Pre-flight Checks

┌─────────────────────────────────────────────────────────┐
${checks.map(c => `│ ${c.name}
│ ${c.details.map(d => `├─ ${d}`).join('\n│ ')}
│ └─ Result: ${c.passed ? '✅ PASS' : '❌ FAIL'}`).join('\n├─────────────────────────────────────────────────────────┤\n')}
└─────────────────────────────────────────────────────────┘

${checks.every(c => c.passed) ? '✅ All Pre-flight Checks PASSED，开始 Review...' : '❌ Pre-flight Checks FAILED，请处理上述问题'}
  `);
}
```

**关键规则**：
1. **每个 Check 都要输出** - 不能省略任何一个
2. **清晰显示结果** - PASS 或 FAIL
3. **显示详细信息** - 让用户了解每个 check 的具体内容
4. **最终汇总** - 显示 All PASSED 或 FAILED

---

## Workflow

### Round Structure

```
┌─────────────────────────────────────────────────────────┐
│  Review Round N                                          │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│  │Reviewer1│  │Reviewer2│  │Reviewer3│  ← 并行 3 个      │
│  └────┬────┘  └────┬────┘  └────┬────┘                  │
│       │            │            │                        │
│       └────────────┼────────────┘                        │
│                    ▼                                     │
│            ┌──────────────┐                              │
│            │ 汇总问题列表  │                              │
│            └──────┬───────┘                              │
│                   ▼                                      │
│            ┌──────────────┐                              │
│            │   Fixer      │  ← 单个 subagent 修复        │
│            └──────────────┘                              │
│                                                          │
│  → 如果有问题修复，进入下一轮 Review Round N+1            │
│  → 如果无新问题，Review 完成                              │
└─────────────────────────────────────────────────────────┘
```

### 1. 并行 Spawn 3 个 Reviewer Subagents

```javascript
// Pre-flight: 获取 PR 历史
const commitHistory = execSync('git log --oneline origin/develop..HEAD').toString().trim();
const lastCommitMsg = execSync('git log -1 --pretty=format:"%s%n%b" HEAD').toString();
const lastCommitStats = execSync('git show --stat HEAD').toString();

// 输出历史摘要
console.log(`
📋 PR 历史摘要
├─ Latest commit: ${lastCommitMsg.split('\n')[0]}
└─ Commits: ${commitHistory.split('\n').length}
`);

// 同时 spawn 3 个 reviewer
const reviewers = [
  { label: "reviewer-1", focus: "功能正确性、测试覆盖" },
  { label: "reviewer-2", focus: "代码质量、最佳实践" },
  { label: "reviewer-3", focus: "安全性、边界情况" }
];

// 并行 spawn（不等待完成）
reviewers.forEach(r => {
  sessions_spawn({
    label: `{branch}-review-{round}-${r.label}`,
    runtime: "subagent",
    model: "bailian/glm-5",
    thinking: "high",
    timeoutSeconds: 180,  // 3 分钟超时
    task: `Review 代码变更：

## 你的角色
- Label: ${r.label}
- 关注点: ${r.focus}

## Review 范围
- 分支: {branchName}
- 对比: develop...HEAD

---

## ⚠️ PR 历史信息（避免重复发现问题！）

### Commit History
\`\`\`
${commitHistory}
\`\`\`

### Latest Commit
\`\`\`
${lastCommitMsg}
\`\`\`

### ⚠️ 已修复的问题（不需要再报告）

根据 commit messages，以下问题已修复：
${parseFixedIssues(commitHistory).map(i => `- ${i}`).join('\n')}

**重要**：不要报告 commit message 中明确说已修复的问题！

---

## ⚠️ Delta Review（关键！）

**Round 2+ 只审查最新 commit 的变更**：
\`\`\`bash
git diff HEAD~1 HEAD
\`\`\`

最新 commit 的变更统计：
\`\`\`
${lastCommitStats}
\`\`\`

---

## ⚠️ 标准化审查清单（必须逐项检查）

### 一、修复验证（Round 2+ 必做）
- [ ] 上一轮的问题是否已正确修复？
- [ ] 修复是否引入新问题？

### 二、新增代码审查（⚠️ 关键！）
- [ ] **安全性**：新增代码的加密、输入验证、权限检查是否正确？
- [ ] **测试覆盖**：新增代码是否有对应单元测试？
- [ ] **边界条件**：新增代码的空值、极端情况、错误处理是否完整？
- [ ] **资源清理**：新增代码的定时器、内存、连接是否正确清理？

### 三、角色专项检查

#### 角色-1 专项（功能正确性）
- [ ] 业务逻辑是否符合需求
- [ ] 条件判断是否完整
- [ ] 循环终止条件正确
- [ ] 边界值是否处理

#### 角色-2 专项（代码质量）
- [ ] 变量命名清晰
- [ ] 函数长度合理（<50行）
- [ ] 无重复代码
- [ ] 注释充分

#### 角色-3 专项（安全性）
- [ ] 外部输入验证
- [ ] 权限检查完整
- [ ] 无注入漏洞（SQL/XSS/命令）
- [ ] 敏感数据处理安全

---

## 输出格式

### 问题列表

| 编号 | 级别 | 问题描述 | 文件:行号 |
|------|------|---------|-----------|
| 1 | P0 | xxx | src/xxx.ts:10 |
| 2 | P1 | xxx | src/yyy.ts:20 |

### 建议
- 建议 1
- 建议 2`
  });
});
```

### 2. 等待所有 Reviewer 完成，汇总结果

```javascript
// 等待 3 个 reviewer 完成
const results = await Promise.all([
  subagents.waitFor("reviewer-1"),
  subagents.waitFor("reviewer-2"),
  subagents.waitFor("reviewer-3")
]);

// 汇总问题列表（去重）
const allIssues = mergeAndDeduplicate(results);
```

### 3. Spawn Fixer Subagent（如有问题）

**P1: 超时与重试机制**

```javascript
const FIXER_TIMEOUT_MS = 5 * 60 * 1000;  // 5 分钟超时
const REVIEWER_TIMEOUT_MS = 3 * 60 * 1000;  // 3 分钟超时
const MAX_RETRIES = 3;

// 带超时和重试的 spawn 函数
async function spawnWithRetry(config, timeoutMs, maxRetries = MAX_RETRIES) {
  let lastError = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const sessionId = sessions_spawn(config);
      
      // 等待完成，带超时
      const result = await waitForCompletion(sessionId, timeoutMs);
      
      if (result.status === "timeout") {
        throw new Error(`Subagent timeout after ${timeoutMs}ms`);
      }
      
      return { success: true, result };
    } catch (error) {
      lastError = error;
      console.warn(`Attempt ${attempt}/${maxRetries} failed: ${error.message}`);
      
      if (attempt < maxRetries) {
        console.log(`Retrying in 10 seconds...`);
        await sleep(10000);
      }
    }
  }
  
  return { success: false, error: lastError };
}

// 检查必须修复的问题（P0/P1/P2）
function getMustFixIssues(issues) {
  return issues.filter(i => ['P0', 'P1', 'P2'].includes(i.level));
}

if (allIssues.length > 0) {
  const mustFixIssues = getMustFixIssues(allIssues);
  const p3Issues = allIssues.filter(i => i.level === 'P3');
  const suggestionIssues = allIssues.filter(i => i.level === '建议' || i.level === '低');
  
  const result = await spawnWithRetry({
    label: `{branch}-fixer-{round}`,
    runtime: "subagent",
    model: "bailian/glm-5",
    thinking: "high",
    timeoutSeconds: 300,  // 5 分钟硬超时
    task: `修复以下问题：

## 问题列表

### 必须修复 (P0/P1/P2)
${formatIssues(mustFixIssues)}

### 尽量修复 (P3)
${p3Issues.length > 0 ? formatIssues(p3Issues) : '（无）'}

### 建议修复 (建议/低)
${suggestionIssues.length > 0 ? formatIssues(suggestionIssues) : '（无）'}

## 修复要求
1. **必须**修复所有 P0/P1/P2 问题
2. **尽量**修复 P3 问题（除非风险过高）
3. **考虑**修复建议级别问题（如果简单且安全）
4. 如果跳过某个问题，请在回复中说明原因
5. 保持代码风格一致
6. 更新相关测试

## 完成后
- 提交 commit（使用 conventional commits 格式）
- 不要推送到 main`
  }, FIXER_TIMEOUT_MS);
  
  // 处理 Fixer 失败
  if (!result.success) {
    console.error(`Fixer failed after ${MAX_RETRIES} attempts:`, result.error);
    
    // 如果有必须修复的问题但 Fixer 失败，报告错误
    if (mustFixIssues.length > 0) {
      return {
        status: "FIXER_FAILED",
        message: `Fixer 无法完成修复，请人工介入`,
        unresolvedIssues: mustFixIssues,
        error: result.error
      };
    }
    
    // 如果只有 P3 问题，可以继续
    console.log("仅有 P3 问题未修复，继续流程...");
  }
  
  // 进入下一轮 review
  return startNextRound();
}
```

### 3.5 进度汇报（每轮结束时）

**每轮 Review 结束后，必须向用户输出摘要：**

```
📊 Round N 完成
├─ 发现问题: X 个 (P0: a, P1: b, P2: c, P3: d)
├─ 修复状态: ✅ 已修复 / ⚠️ 部分修复
├─ 累计修复: XX 个问题
└─ 当前状态: 继续下一轮 / 接近完成 (consecutiveCleanRounds: N/2)
```

**实现方式**：
```javascript
function reportProgress(round, issues, fixedCount, cleanRounds) {
  const p0 = issues.filter(i => i.level === 'P0').length;
  const p1 = issues.filter(i => i.level === 'P1').length;
  const p2 = issues.filter(i => i.level === 'P2').length;
  const p3 = issues.filter(i => i.level === 'P3').length;
  
  const status = issues.length === 0 ? '✅ 无问题' : '⚠️ 需修复';
  const progress = cleanRounds >= 2 ? '✅ Review 完成!' : `继续下一轮 (${cleanRounds}/2)`;
  
  console.log(`
📊 Round ${round} 完成
├─ 发现问题: ${issues.length} 个 (P0: ${p0}, P1: ${p1}, P2: ${p2}, P3: ${p3})
├─ 修复状态: ${status}
├─ 累计修复: ${fixedCount} 个问题
└─ 当前状态: ${progress}
  `);
}
```

**注意**：这有助于用户了解进度，特别是在多轮 Review 时。

### 4. 退出标准（强制要求）

**⚠️ 必须同时满足以下条件才能结束 Review：**

```
1. 连续两轮 Review 都未发现任何 P0/P1/P2 问题
2. 所有发现的问题（包括 P3）都已修复或已说明跳过原因
```

**具体判断逻辑**：

```javascript
const MAX_ROUNDS = 10;  // 最大轮次限制，防止无限循环
const FIXER_TIMEOUT_MS = 5 * 60 * 1000;  // Fixer 超时：5 分钟
const REVIEWER_TIMEOUT_MS = 3 * 60 * 1000;  // Reviewer 超时：3 分钟
const MAX_RETRIES = 3;  // 最大重试次数

let consecutiveCleanRounds = 0;  // 连续无问题的轮数
let currentRound = 0;
let hasUnresolvedP3 = false;  // 是否有未处理的 P3

function checkCompletion(currentRoundIssues, allP3Resolved) {
  currentRound++;
  
  // P0: 最大轮次检查 - 防止无限循环
  if (currentRound >= MAX_ROUNDS) {
    return {
      status: "MAX_ROUNDS_EXCEEDED",
      message: `已达到最大轮次 ${MAX_ROUNDS}，强制退出。请人工检查未解决的问题。`
    };
  }
  
  // 检查 P0/P1/P2 问题
  const mustFixIssues = currentRoundIssues.filter(i => 
    ['P0', 'P1', 'P2'].includes(i.level)
  );
  
  // 检查 P3 问题
  const p3Issues = currentRoundIssues.filter(i => i.level === 'P3');
  
  if (mustFixIssues.length === 0 && p3Issues.length === 0) {
    // 本轮无任何问题
    consecutiveCleanRounds++;
    
    if (consecutiveCleanRounds >= 2 && allP3Resolved) {
      return { status: "REVIEW_COMPLETE" }; // 连续两轮无问题 + P3 已处理
    }
  } else {
    // 发现问题，重置计数
    consecutiveCleanRounds = 0;
    if (p3Issues.length > 0) {
      hasUnresolvedP3 = true;
    }
  }
  
  return { status: "CONTINUE" }; // 需要继续
}
```

**⚠️ 重要：连续两轮的逻辑**

```
consecutiveCleanRounds 的含义是"连续多少轮没有发现新问题"

Round 1: 发现问题 → Fixer → consecutiveCleanRounds = 0
Round 2: 无 P0/P1/P2/P3 → consecutiveCleanRounds = 1 → 继续下一轮
Round 3: 无 P0/P1/P2/P3 → consecutiveCleanRounds = 2 → ✅ 可以结束

如果 Round 3 发现新问题：
Round 3: 发现问题 → consecutiveCleanRounds = 0 → Fixer
Round 4: 无问题 → consecutiveCleanRounds = 1
Round 5: 无问题 → consecutiveCleanRounds = 2 → ✅ 可以结束
```

**为什么需要连续两轮？**
- 避免单轮遗漏 bug 的异常退出
- 确保修复后没有引入新问题
- 提高代码审查质量

**示例**：
```
Round 1: 发现 10 个问题 → Fixer 修复
Round 2: 发现 3 个新问题 → Fixer 修复
Round 3: 无问题 → consecutiveCleanRounds = 1
Round 4: 无问题 → consecutiveCleanRounds = 2 → ✅ 结束
```

**如果 Round 4 发现新问题**：
```
Round 4: 发现 1 个问题 → consecutiveCleanRounds = 0 → 继续循环
Round 5: 无问题 → consecutiveCleanRounds = 1
Round 6: 无问题 → consecutiveCleanRounds = 2 → ✅ 结束
```

**达到最大轮次时**：
```
Round 10: 仍有问题 → ⚠️ MAX_ROUNDS_EXCEEDED
→ 强制退出，报告未解决问题列表
→ 建议人工介入
```

---

## Issue Severity

| Level | Definition | Examples | Fix Requirement |
|-------|------------|----------|-----------------|
| **P0** | Critical - Fix immediately | Runtime errors, security vulnerabilities | 必须 |
| **P1** | High - Fix this iteration | Functional defects, missing error handling | 必须 |
| **P2** | Medium - Should fix | Code quality, test coverage gaps | 必须 |
| **P3** | Low - Fix in same PR | Code style, documentation, minor improvements | 尽量修复 |

### P3 处理规则

**⚠️ P3 不是"跳过"，而是"尽量修复"！**

Fixer 对 P3 的处理：
1. ✅ **优先修复**：简单、低风险、不影响稳定性的 P3 问题
2. ⚠️ **谨慎处理**：需要较大改动的 P3，评估风险后决定
3. ❌ **跳过并说明**：高风险或耗时过长的 P3，在回复中说明原因

**示例：**
```
✅ 可修复的 P3：
- 移除 console.log
- 添加注释
- 变量重命名
- 简化条件表达式

⚠️ 需评估的 P3：
- 提取方法（可能影响调用链）
- 类型定义重构（可能影响多处）

❌ 应跳过的 P3：
- 大规模代码重组
- 需要引入新依赖
- 可能破坏测试的改动
```

---

## Reviewer 角色分工

| Reviewer | 关注点 | 检查项 |
|----------|--------|--------|
| **Reviewer-1** | 功能正确性 | 业务逻辑、测试覆盖、边界条件 |
| **Reviewer-2** | 代码质量 | 代码结构、命名规范、可维护性 |
| **Reviewer-3** | 安全性 | 安全漏洞、输入验证、权限控制 |

---

## 汇总逻辑

```javascript
function mergeAndDeduplicate(results) {
  const issues = [];
  const seen = new Set();
  
  for (const result of results) {
    for (const issue of result.issues) {
      const key = `${issue.level}:${issue.file}:${issue.line}`;
      if (!seen.has(key)) {
        seen.add(key);
        issues.push(issue);
      }
    }
  }
  
  // 按 P0 > P1 > P2 > P3 排序
  return issues.sort((a, b) => {
    const order = { P0: 0, P1: 1, P2: 2, P3: 3 };
    return order[a.level] - order[b.level];
  });
}
```

## 解析已修复问题

```javascript
/**
 * 从 commit history 中解析已修复的问题
 * 用于避免重复发现已修复的问题
 */
function parseFixedIssues(commitHistory) {
  const fixedIssues = [];
  const lines = commitHistory.split('\n');
  
  for (const line of lines) {
    // 匹配常见的问题标识格式
    // 例如: "P1-1: xxx", "P2-3: xxx", "fix: xxx"
    const issuePatterns = [
      /P[0-3]-\d+[:：]/g,           // P1-1: xxx
      /fix\([^)]+\):/g,             // fix(security): xxx
      /P[0-3]:\s/g,                 // P1: xxx
      /(replay|timestamp|nonce|SSRF|XSS|注入)/gi  // 关键词
    ];
    
    for (const pattern of issuePatterns) {
      const matches = line.match(pattern);
      if (matches) {
        fixedIssues.push(...matches);
      }
    }
  }
  
  // 去重
  return [...new Set(fixedIssues)];
}
```

---

## ⚠️ 强制自动循环（不要问用户）

```
Review Round 1 → Fixer → Review Round 2 → Fixer → ... → 连续两轮无问题 → 结束
                                    ↓
                          （最多 10 轮）
                                    ↓
                          超时/失败 → 重试 3 次 → 人工介入
```

**禁止行为**：
- ❌ 不要在 Review 后问"需要修复吗？"
- ❌ 不要在 Fixer 后问"要继续 Review 吗？"
- ❌ 不要中断自动循环流程
- ❌ 不要在单轮无问题后就结束

**正确流程**：
1. 检查 `currentRound >= MAX_ROUNDS`，若达到上限则强制退出
2. 并行 spawn 3 个 reviewer（带超时）
3. 等待全部完成，处理超时/失败（重试 3 次）
4. 汇总问题，仅检查 P0/P1/P2（P3 可选）
5. 如果有问题 → spawn Fixer（带超时和重试）→ 回到步骤 1
6. 如果无问题 → consecutiveCleanRounds++
7. 如果 consecutiveCleanRounds < 2 → 回到步骤 1
8. 如果 consecutiveCleanRounds >= 2 → ✅ 结束，提交 PR

**异常处理路径**：
- Reviewer 超时/失败 → 重试 3 次 → 仍失败则报告错误
- Fixer 超时/失败 → 重试 3 次 → 仍有 P0/P1/P2 则人工介入
- 达到 MAX_ROUNDS → 强制退出，报告未解决问题

## Key Points

1. **⚠️ PR 历史检查优先** - 开始前必须读取 commit history，避免重复发现已修复的问题
2. **⚠️ Review 模式询问** - commit 数量 > 1 时，必须询问用户选择 Delta 还是 Full Review
3. **⚠️ Pre-flight Checks 输出** - 每个 Check 的结果都必须输出给用户
4. **Model 推荐不强制** - 推荐代码能力最强的模型，由用户决定
5. **thinking: "high" 必须启用** - 提高 Review 质量
6. **Delta vs Full** - Round 2+ 默认 Delta Review，除非用户选择 Full Review
7. **3 个 reviewer 并行** - 最大化问题发现
8. **1 个 fixer 串行** - 统一修复，避免冲突
9. **强制使用检查清单** - Reviewer 必须按 checklist 逐项检查
10. **去重汇总** - 避免重复修复同一问题
11. **连续两轮无问题才结束** - 避免单轮遗漏 bug
12. **自动提交 PR** - Review 完成后自动提交
13. **MAX_ROUNDS = 10** - 防止无限循环
14. **超时机制** - Fixer 5 分钟，Reviewer 3 分钟
15. **重试机制** - 失败最多重试 3 次
16. **P3 尽量修复** - 退出时所有问题都应处理（修复或说明跳过原因）
17. **新增代码强制独立审查** - 不要只关注"修复了什么"，必须审查新增代码的安全性、测试覆盖、边界条件、资源清理

---

## 退出标准图示

### 正常流程（连续两轮无问题）

```
Round 1: 发现问题 → Fixer → clean = 0
    ↓
Round 2: 发现问题 → Fixer → clean = 0
    ↓
Round 3: 无问题 → clean = 1 → 继续下一轮（必须连续两轮）
    ↓
Round 4: 无问题 → clean = 2 → ✅ END
```

### 有新问题继续

```
Round 4: 发现问题 → clean = 0 → Fixer
    ↓
Round 5: 无问题 → clean = 1
    ↓
Round 6: 无问题 → clean = 2 → ✅ END
```

### Round 3 发现新问题的流程

```
Round 2: 无问题 → clean = 1
    ↓
Round 3: 发现新问题 → clean = 0 → Fixer
    ↓
Round 4: 无问题 → clean = 1
    ↓
Round 5: 无问题 → clean = 2 → ✅ END
```

### 达到最大轮次

```
Round 10: 仍有问题
    ↓
⚠️ MAX_ROUNDS_EXCEEDED
    ↓
强制退出，报告未解决问题 → 人工介入
```

### 异常处理

```
Fixer 超时/失败
    ↓
重试 1 → 重试 2 → 重试 3
    ↓
仍失败？
    ├─ 有 P0/P1/P2 问题 → ⚠️ FIXER_FAILED → 人工介入
    └─ 仅 P3 问题 → 记录未处理项 → 继续流程
```

### P3 未完全处理的流程

```
Round 2: 发现 P3 问题 → Fixer 尝试修复
    ↓
Fixer 回复: "P3-xxx 跳过，原因: 风险过高"
    ↓
Round 3: 无新问题 → clean = 1
    ↓
Round 4: 无新问题 → clean = 2 → ✅ END
    ↓
最终报告: "Review 完成，P3-xxx 已跳过（原因: 风险过高）"
```

---

## References

- [checklist.md](references/checklist.md) - Complete review checklist