---
name: resource-hunter
description: "🎯 全路径资源猎手 — 一个命令找到任何资源。聚合搜索阿里云盘/夸克/百度/115/UC 等 10+ 云盘分享链接，TPB/EZTV/Nyaa 磁力种子，B站/YouTube 等 1000+ 网站视频下载。智能类型识别，并发搜索，画质优先排序。无需 API Key，完全免费。"
metadata: {"openclaw":{"emoji":"🎯"}}
---

# 🎯 Resource Hunter — 全路径资源猎手

> 一个命令，找到任何资源。网盘 + 种子 + 视频下载，三路并举，无需 API Key。

## ✨ 特性

- **10+ 云盘聚合** — 阿里云盘、夸克、百度、115、UC、PikPak、123网盘等同时搜索
- **3大种子引擎** — TPB、EZTV（美剧专用）、Nyaa（动漫专用）并发搜索
- **1000+ 视频网站** — B站、抖音、YouTube、TikTok 等直链下载
- **智能识别** — 自动判断电影/动漫/美剧/音乐/软件，选择最优搜索策略
- **画质优先** — REMUX > 4K/UHD > BluRay > 1080p 智能排序
- **自动提取密码** — 网盘分享链接密码自动识别提取
- **无需 API Key** — 全部使用免费公开接口
- **并发高速** — 网盘+种子同时搜索，4秒内出结果

## 🚀 快速开始

```bash
SKILL_DIR="$(openclaw skills path resource-hunter)/scripts"

# 搜索电影（中英文混合效果最佳）
python3 "$SKILL_DIR/hunt.py" '流浪地球2 The Wandering Earth 2023' --movie

# 搜索动漫
python3 "$SKILL_DIR/hunt.py" '进击的巨人 Attack on Titan' --anime

# 搜索音乐（自动加无损关键词）
python3 "$SKILL_DIR/hunt.py" '周杰伦' --music

# 搜索软件
python3 "$SKILL_DIR/hunt.py" 'Adobe Photoshop 2024' --software

# 视频链接直接下载
python3 "$SKILL_DIR/hunt.py" 'https://www.bilibili.com/video/BV1xx...'
```

## 📋 参数说明

| 参数 | 说明 |
|------|------|
| `--movie` | 电影模式 |
| `--anime` | 动漫模式（启用 Nyaa）|
| `--tv` | 美剧模式（启用 EZTV）|
| `--music` | 音乐模式（自动加无损）|
| `--software` | 软件模式 |
| `--quick` | 快速模式（每云盘1条，更简洁）|
| `--sub` | 优先带中文字幕版本 |
| `--4k` | 优先4K版本 |
| `--pan-only` | 只搜网盘 |
| `--torrent-only` | 只搜种子（建议英文关键词）|
| `--page N` | 翻页查看更多结果 |

## 🔧 依赖

- **网盘/种子搜索**：无需任何依赖，开箱即用
- **视频下载**：需安装 [yt-dlp](https://github.com/yt-dlp/yt-dlp)

```bash
# 安装 yt-dlp（可选，仅视频下载需要）
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp && chmod +x ~/.local/bin/yt-dlp
```

## 📊 数据来源

| 功能 | 数据源 | 费用 |
|------|--------|------|
| 网盘搜索 | 2fun.live PanSou | 免费 |
| 种子搜索 | The Pirate Bay | 免费 |
| 美剧种子 | EZTV | 免费 |
| 动漫种子 | Nyaa.si | 免费 |
| 视频下载 | yt-dlp | 免费 |
