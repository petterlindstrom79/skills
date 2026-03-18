# slide-creator — 产品文档

> 私有工作文档，不进入 skill repo。
> 最后更新：2026-03-14

---

## 产品定位

**目标用户：** 不会写代码的普通工作者（职场人、教育者、创业者）

**核心价值：** AI 帮你从零生成演示文稿，零依赖单 HTML 文件，浏览器直接打开

**差异化：**
- 不是"开发者工具"，不需要 Node.js / 构建工具 / Markdown 语法
- AI 负责内容创作 + 风格选择，用户只需描述需求
- 19 种开箱即用设计预设，视觉品质远超通用 AI 生成物
- 体验简单、性能流畅是最高优先级，不为功能堆砌牺牲这两点

---

## 竞品分析：Slidev（sli.dev）

### Slidev 是什么

面向开发者的 Markdown 驱动演示工具，Vue 3 + Vite + TypeScript 技术栈。

### Slidev 的强项
- Presenter Mode：双窗口同步，演讲者/观众分离
- Monaco 内嵌实时代码编辑器（现场改代码演示）
- Mermaid 图表原生支持
- 实时画笔标注
- Git 友好（纯文本 Markdown 源文件）
- 主题生态（社区贡献）
- 录制 + 摄像头画中画

### Slidev 的弱项（我们的机会）
- 需要 Node.js + npm，非开发者无法使用
- 内容要自己写，没有 AI 辅助
- 学习曲线陡峭（Markdown、Vue 组件、frontmatter）
- 主题配置复杂，不适合快速出图

### 结论
两者用户群基本不重叠。不需要功能追赶，专注做好"AI 帮普通人生成幻灯片"这件事。

---

## 功能路线图

### P0 — 已完成

#### ✅ Presenter Mode（演讲者模式）v1.5.2~1.5.3
**价值：** 真实演讲场景的刚需，极大提升正式使用体验
**实现方案：**
- 生成的 HTML 检测 `?presenter` URL 参数
- 演讲者视图显示：当前幻灯片缩略图、下一张预览、备注（speaker notes）、计时器
- 主窗口与演讲者窗口通过浏览器原生 `BroadcastChannel` API 同步（无网络请求，本地通信）
- 对主窗口零性能影响
- 启用方式：主窗口右键菜单或快捷键 `P` 打开演讲者窗口

**依赖：** 生成时需要把 speaker notes 写入 HTML（现在放在 `PRESENTATION_SCRIPT.md`，需要同时内联进 HTML）

---

### P1 — 已完成

#### ✅ 图表支持（内联 SVG）v1.6.1
**价值：** 流程图、架构图、时序图不再需要用户提供图片，Claude 直接生成
**实现方案（零运行时性能影响）：**
- 生成阶段：Claude 输出 Mermaid 语法
- 调用 `mermaid-cli`（`npx mmdc`）或 Python 库将其渲染为 SVG
- SVG 直接内联进 HTML，最终产物无任何 JS 依赖
- 如果环境没有 mermaid-cli，fallback 为文字描述 + 简单 CSS 框

#### ✅ 本地主题系统 v1.6.1
**价值：** 高级用户可扩展风格，长期可形成社区主题生态
**实现方案（不做 registry，只做本地文件夹）：**
```
~/.claude/skills/slide-creator/
  themes/
    my-theme/
      reference.md    ← 风格描述，Claude 读取
      starter.html    ← 可选起始模板
```
- SKILL.md 生成前扫描 `themes/` 目录，追加到预设列表
- 用户 clone 主题文件夹即可使用，零安装命令
- 普通用户完全无感知

---

### P2 — 观察期（暂不做）

#### 实时画笔标注
- 技术可行（Canvas overlay + pointer events），但：
  - 目标用户主要用鼠标，不是触控笔
  - 标注无法保存，实用价值有限
  - 等用户明确提出需求再做

#### 录制 + 摄像头画中画
- 对"录课"场景有价值
- 实现成本较高，且浏览器摄像头权限在 `file://` 协议下受限
- 暂列观察

#### 主题 Registry / ClawHub 主题市场
- 等本地主题系统跑通、社区规模形成后再考虑

---

## 设计原则

1. **体验简单优先** — 每个新功能问自己：非开发者第一次见到会困惑吗？
2. **性能不妥协** — 新增功能不得影响幻灯片切换流畅度，重功能做成可选加载
3. **零依赖哲学** — 生成产物是单 HTML 文件，运行时不引入外部库
4. **渐进增强** — 高级功能（Presenter Mode、图表）对不用的人完全透明

---

## 版本记录

| 版本 | 主要变化 |
|------|---------|
| v1.5.1 | 19 种预设、Chinese Chan、截图画廊、修复触控板惯性滚动 |
| v1.5.0 | 新增 Aurora Mesh / Enterprise Dark / Glassmorphism / Neo-Brutalism / Japanese Zen / Data Story |
| v1.4.x | Blue Sky starter 模板、PPTX 导出改用 Playwright + 系统 Chrome |
