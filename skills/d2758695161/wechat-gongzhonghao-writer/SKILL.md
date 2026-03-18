---
name: wechat-article-writer
description: "Write professional WeChat Official Account (微信公众号) articles with proper formatting, SEO, and engagement optimization. Generates complete articles with title hooks, structured body, call-to-actions, and reading-time estimates. Use when: writing WeChat articles, creating newsletter content in Chinese, drafting thought leadership pieces for Chinese audiences, or converting topics into publishable WeChat format."
version: 1.0.0
---

# WeChat Article Writer ✍️

Generate publish-ready articles for WeChat Official Accounts (微信公众号).

## Article Structure

### 1. Title (标题)
- Max 64 chars (22 chars optimal for preview)
- Patterns that work:
  - Number hook: "5个方法让你..." / "90%的人不知道..."
  - Curiosity gap: "为什么...？真相是..." 
  - Authority: "腾讯内部员工都在用的..."
  - Pain point: "月薪3千到3万，我只做了这一件事"
  - List: "2026年最值得关注的10个趋势"

### 2. Abstract (摘要)
- 54 chars max (shown in share cards)
- Summarize the core value proposition
- Include one emotional hook

### 3. Cover Image Suggestion
- Recommend image style, dimensions (900x383 for single, 200x200 for multi)
- Suggest text overlay if applicable

### 4. Body Structure
```
开头 (Hook) — 100-200字
├── 痛点共鸣 or 故事引入 or 数据震撼
│
正文 (Body) — 1000-2500字  
├── 小标题1 (加粗)
│   └── 论点 + 案例 + 总结
├── 小标题2
│   └── 论点 + 案例 + 总结
├── 小标题3
│   └── 论点 + 案例 + 总结
│
结尾 (CTA) — 100-200字
├── 总结金句
├── 互动引导（留言/转发/在看）
└── 下期预告（可选）
```

### 5. Formatting Rules
- Paragraphs: 3-4 lines max, then blank line
- Bold key phrases: **像这样**
- Use section dividers: ━━━━━━━━
- Emoji sparingly (professional tone, 2-3 per section max)
- Quote blocks for key insights
- No markdown headers (WeChat doesn't render them) — use **bold** for headers

### 6. Reading Time
- Calculate: ~400 chars/min for Chinese
- Display at top: "阅读时间：约X分钟"

### 7. SEO Keywords
- Suggest 3-5 keywords for WeChat search (搜一搜) optimization
- Place naturally in title, first paragraph, and subheadings

## Writing Styles

### 干货型 (Practical Value)
- Heavy on actionable tips
- Step-by-step instructions
- Screenshots/examples references
- "学完就能用"

### 故事型 (Storytelling)
- Personal narrative or case study
- Emotional arc: problem → struggle → breakthrough
- Relatable details
- "让人忍不住读完"

### 观点型 (Opinion/Analysis)
- Strong thesis statement
- Industry data + personal insight
- Contrarian or fresh angle
- "发人深省"

### 科普型 (Educational)
- Complex topic made simple
- Analogies and metaphors
- Progressive complexity
- "小白也能懂"

## Usage

1. User provides topic + target audience
2. Ask for preferred style (or suggest based on topic)
3. Generate complete article following structure above
4. Include title variations (2-3 options)
5. Suggest posting time and follow-up content ideas
