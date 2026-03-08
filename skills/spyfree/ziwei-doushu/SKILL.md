---
name: ziwei-doushu
description: 紫微斗数专业排盘技能（框架化解读版）。默认东八区北京口径（Asia/Shanghai, longitude=120.0），全离线运行（不联网、无 headless 浏览器依赖）；排盘图可选且失败不阻断，输出“排盘事实 + 传统经验框架”供后续二次判断。
---

# Ziwei Doushu

推荐命令：

```bash
python scripts/ziwei_chart.py \
  --date 1990-10-21 \
  --time 15:30 \
  --gender female \
  --year 2026 \
  --engine dual \
  --template pro \
  --format markdown
```

## 默认口径
- 时区：`Asia/Shanghai`
- 经度：`120.0`
- 引擎：`py`
- 报告默认：优先尝试输出 `JPG` 排盘图（依赖缺失会自动跳过，不影响文本报告）

## 常用参数
- `--engine py|js|dual`：主引擎/备用引擎/双引擎校验
- `--template lite|pro|executive`：输出密度
- `--chart none|svg|jpg`：是否输出图盘
- `--chart-quality 1-100`：JPG 质量，默认 `92`
- `--chart-backend auto|cairosvg`：JPG 渲染后端
  - `auto`：使用 `cairosvg`（纯离线、无浏览器）
- `--format markdown|json`：输出格式

## 输出结构
1. 排盘口径（时区、经度、统一计算时间）
2. 排盘事实（命身宫、十二宫、三方四正、四化、大限）
3. 传统研判框架（结论 + 盘面 + 经验，不写死具体建议）
4. 方法论来源（便于后续二次解读）

## 依赖
```bash
python -m venv .venv
.venv/bin/pip install -U iztro-py
npm install iztro
```

若需 JPG 导出，再安装：
```bash
.venv/bin/pip install -U cairosvg pillow
```

如果未安装图片依赖或图片生成失败，skill 会自动跳过排盘图，不影响文本报告输出。

最低建议版本：
- `iztro-py >= 0.3.4`（Python 主引擎）
- `iztro >= 2.5.7`（JS 备用引擎）

## 参考
- `references/mapping.md`
- `references/interpretation-framework.md`
