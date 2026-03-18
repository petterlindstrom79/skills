# Resource Sources Reference

## 网盘聚合搜索

| 站点 | API | 说明 |
|------|-----|------|
| 2fun.live | `https://s.2fun.live/api/search?q=关键词` | 主力，支持10+云盘 |
| hunhepan.com | `https://www.hunhepan.com/api/search?q=关键词` | 备用 |
| pansou.vip | `https://pansou.vip/api` | 备用 |

### 支持云盘类型
- ☁️ aliyun — 阿里云盘
- ⚡ quark — 夸克网盘
- 🔵 baidu — 百度网盘
- 🔷 115 — 115网盘
- 🟣 pikpak — PikPak
- 🟠 uc — UC网盘
- 🔴 xunlei — 迅雷云盘
- 🟢 123 — 123网盘
- 🔹 tianyi — 天翼云盘
- 🧲 magnet — 磁力链接
- 🔗 ed2k — ED2K

## 种子/磁力搜索

| 引擎 | 地址 | 适合 |
|------|------|------|
| ThePirateBay | `https://apibay.org/q.php?q=关键词` | 通用 |
| Nyaa | `https://nyaa.si/?f=0&c=0_0&q=关键词&page=rss` | 动漫/日剧 |
| 1337x | `https://www.1377x.to/search/关键词/1/` | 通用 |

## 视频下载支持平台（yt-dlp）

国内：哔哩哔哩、抖音、微博、腾讯视频、爱奇艺、优酷、AcFun、斗鱼、虎牙  
国外：YouTube、Instagram、TikTok、Twitter/X、Facebook、Reddit、Twitch、Vimeo、NicoNico  
总计支持 1000+ 网站

## 决策矩阵

| 用户需求 | 优先策略 | 脚本 |
|----------|----------|------|
| 电影/电视剧 | 网盘搜索 → 种子 | pansou.py → torrent.py |
| 动漫 | Nyaa种子 → 网盘 | torrent.py --anime → pansou.py |
| 视频链接下载 | yt-dlp直接下载 | video.py download |
| 软件/游戏 | 网盘搜索 → 磁力 | pansou.py → torrent.py |
| 音乐 | yt-dlp音频 → 网盘 | video.py --audio → pansou.py |
| 字幕/文本 | yt-dlp字幕提取 | video.py subtitle |
