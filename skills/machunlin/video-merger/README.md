# Video Merger
> 多片段短视频自动拼接工具，支持按文件名排序、统一音视频参数、淡入淡出转场，适合AI短剧、分镜头视频批量拼接

## 功能特性
✅ 严格按文件名数字序号排序，保证剧情顺序正确  
✅ 自动保持原始分辨率/支持自定义输出分辨率  
✅ 统一帧率、编码，保证播放流畅  
✅ 支持淡入淡出转场效果，可自定义转场时长  
✅ 自动同步音轨，完整保留原音频  
✅ 轻量无依赖，仅需ffmpeg和Python3

## 安装
```bash
# 安装依赖
brew install ffmpeg  # macOS
# 或 sudo apt install ffmpeg # Ubuntu/Debian

# 克隆项目
git clone https://github.com/[your-username]/video-merger.git
cd video-merger
```

## 使用方法
```bash
# 基础使用：保持原始分辨率拼接
python3 scripts/merge_full_video.py --input /path/to/your/segments --output ./full_video.mp4

# 自定义分辨率和转场时长
python3 scripts/merge_full_video.py --input /path/to/segments --output ./full_1080p.mp4 --resolution 1080x1920 --transition 1.0
```

## 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 分镜头视频所在目录，文件需以`数字_`开头命名 | 必填 |
| `--output` | 输出视频文件路径 | 必填 |
| `--resolution` | 自定义输出分辨率，如`1080x1920` | 保持原始分辨率 |
| `--transition` | 淡入淡出转场时长（秒） | 0.5 |

## 适用场景
- AI生成短剧分镜头批量拼接
- 录制的分段视频自动合并
- 短视频批量生产处理

## License
MIT
