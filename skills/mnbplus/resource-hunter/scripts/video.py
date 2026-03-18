#!/usr/bin/env python3
"""
Video Downloader - 万能视频下载
基于 yt-dlp，支持 1000+ 网站
"""

import argparse
import json
import os
import subprocess
import sys
import re

# 下载目录：优先用 OpenClaw workspace，否则用 ~/Downloads
_oc_dl = os.path.expanduser("~/.openclaw/workspace/storage/downloads")
_home_dl = os.path.expanduser("~/Downloads")
DOWNLOAD_DIR = _oc_dl if os.path.isdir(os.path.expanduser("~/.openclaw")) else _home_dl

PLATFORMS = {
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "bilibili.com": "哔哩哔哩",
    "b23.tv": "哔哩哔哩",
    "tiktok.com": "TikTok",
    "douyin.com": "抖音",
    "instagram.com": "Instagram",
    "twitter.com": "Twitter/X",
    "x.com": "Twitter/X",
    "weibo.com": "微博",
    "v.qq.com": "腾讯视频",
    "iqiyi.com": "爱奇艺",
    "youku.com": "优酷",
    "acfun.cn": "AcFun",
    "nicovideo.jp": "NicoNico",
    "twitch.tv": "Twitch",
    "vimeo.com": "Vimeo",
    "facebook.com": "Facebook",
    "reddit.com": "Reddit",
}


def detect_platform(url):
    for domain, name in PLATFORMS.items():
        if domain in url:
            return name
    return "未知平台"


def run_ytdlp(args_list, capture=True):
    cmd = ["yt-dlp"] + args_list
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=300,
        )
        return result
    except FileNotFoundError:
        print("❌ 未找到 yt-dlp，请先安装: curl -L https://ghfast.top/https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp && chmod +x ~/.local/bin/yt-dlp", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("❌ 下载超时", file=sys.stderr)
        sys.exit(1)


def cmd_info(url, json_output=False):
    """获取视频信息和可用画质"""
    platform = detect_platform(url)
    print(f"🔍 正在获取 {platform} 视频信息...", file=sys.stderr)

    result = run_ytdlp(["-J", "--no-playlist", url])
    if result.returncode != 0:
        print(f"❌ 获取失败: {result.stderr[:200]}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("❌ 解析视频信息失败", file=sys.stderr)
        sys.exit(1)

    if json_output:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    title = data.get("title", "未知标题")
    duration = data.get("duration", 0)
    uploader = data.get("uploader", "")
    duration_str = f"{int(duration//60)}:{int(duration%60):02d}" if duration else "?"

    print(f"\n📺 {title}")
    print(f"   平台: {platform} | 时长: {duration_str} | 作者: {uploader}")
    print()

    # 提取可用格式
    formats = data.get("formats", [])
    video_formats = []
    seen_res = set()

    for f in formats:
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        height = f.get("height")
        fmt_id = f.get("format_id", "")
        ext = f.get("ext", "")
        filesize = f.get("filesize") or f.get("filesize_approx", 0)

        if vcodec == "none" or not height:
            continue
        if height in seen_res:
            continue
        seen_res.add(height)

        size_str = f"{filesize/1024/1024:.1f}MB" if filesize else "?"
        has_audio = "✓音" if acodec != "none" else "需合并"
        video_formats.append((height, fmt_id, ext, size_str, has_audio))

    video_formats.sort(key=lambda x: x[0], reverse=True)

    print("📊 可用画质:")
    print(f"   {'格式ID':<12} {'分辨率':<10} {'格式':<8} {'大小':<10} 音频")
    print("   " + "-" * 50)
    for height, fmt_id, ext, size, audio in video_formats:
        print(f"   {fmt_id:<12} {str(height)+'p':<10} {ext:<8} {size:<10} {audio}")

    # 推荐格式
    print()
    print("💡 推荐命令:")
    if video_formats:
        best = video_formats[0]
        print(f"   python3 video.py download '{url}' {best[1]}   # 最高画质 {best[0]}p")
        if len(video_formats) >= 3:
            mid = video_formats[len(video_formats)//2]
            print(f"   python3 video.py download '{url}' {mid[1]}   # 中等画质 {mid[0]}p")
    print(f"   python3 video.py download '{url}' best   # 自动最佳")


def cmd_download(url, fmt_id="best", output_dir=None, audio_only=False):
    """下载视频"""
    platform = detect_platform(url)
    out_dir = output_dir or DOWNLOAD_DIR
    os.makedirs(out_dir, exist_ok=True)

    print(f"⬇️  正在下载 {platform} 视频...", file=sys.stderr)

    yt_args = [
        "--no-playlist",
        "-o", os.path.join(out_dir, "%(title)s.%(ext)s"),
        "--merge-output-format", "mp4",
        "--no-warnings",
    ]

    if audio_only:
        yt_args += ["-x", "--audio-format", "mp3"]
    elif fmt_id == "best":
        yt_args += ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"]
    else:
        yt_args += ["-f", fmt_id]

    yt_args.append(url)

    result = run_ytdlp(yt_args, capture=False)
    if result.returncode != 0:
        print(f"❌ 下载失败", file=sys.stderr)
        sys.exit(1)

    # 找到下载的文件
    files = sorted(
        [os.path.join(out_dir, f) for f in os.listdir(out_dir)],
        key=os.path.getmtime,
        reverse=True
    )
    if files:
        latest = files[0]
        size = os.path.getsize(latest) / 1024 / 1024
        print(f"\n✅ 下载完成: {latest} ({size:.1f}MB)")
        return latest
    return None


def cmd_subtitle(url, lang="zh-Hans,zh,en"):
    """提取字幕/转录"""
    print(f"📝 提取字幕...", file=sys.stderr)
    result = run_ytdlp([
        "--skip-download",
        "--write-auto-sub",
        "--write-sub",
        "--sub-lang", lang,
        "--sub-format", "vtt",
        "-o", "/tmp/subtitle_%(title)s",
        url
    ])
    if result.returncode == 0:
        # 找字幕文件
        import glob
        files = glob.glob("/tmp/subtitle_*.vtt")
        if files:
            with open(files[0]) as f:
                content = f.read()
            # 清理 VTT 格式，只留文本
            lines = []
            for line in content.split("\n"):
                if not re.match(r"^(WEBVTT|\d{2}:|NOTE|$)", line) and "-->" not in line:
                    lines.append(line.strip())
            text = "\n".join(l for l in lines if l)
            print(text[:5000])
            os.unlink(files[0])
            return
    print("⚠️ 未找到字幕，该视频可能没有字幕")


def main():
    parser = argparse.ArgumentParser(description="万能视频下载器")
    sub = parser.add_subparsers(dest="cmd")

    # info 子命令
    p_info = sub.add_parser("info", help="查看视频信息和可用画质")
    p_info.add_argument("url", help="视频 URL")
    p_info.add_argument("--json", action="store_true", dest="json_output")

    # download 子命令
    p_dl = sub.add_parser("download", help="下载视频")
    p_dl.add_argument("url", help="视频 URL")
    p_dl.add_argument("format", nargs="?", default="best", help="格式ID或 best")
    p_dl.add_argument("--dir", help="输出目录")
    p_dl.add_argument("--audio", action="store_true", help="仅下载音频 (MP3)")

    # subtitle 子命令
    p_sub = sub.add_parser("subtitle", help="提取字幕")
    p_sub.add_argument("url", help="视频 URL")
    p_sub.add_argument("--lang", default="zh-Hans,zh,en", help="字幕语言")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    if args.cmd == "info":
        cmd_info(args.url, args.json_output)
    elif args.cmd == "download":
        cmd_download(args.url, args.format, args.dir, args.audio)
    elif args.cmd == "subtitle":
        cmd_subtitle(args.url, args.lang)


if __name__ == "__main__":
    main()
