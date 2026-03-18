#!/usr/bin/env python3
"""
Hunt - 智能资源猎手主入口
自动分析请求，选择最优搜索路径，聚合结果
"""

import argparse
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run(script, args, timeout=20):
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, script)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "⏱️ 搜索超时", 1
    except Exception as e:
        return f"❌ 错误: {e}", 1


def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def cn_to_en_hint(keyword):
    """从中文关键词中提取可能的英文名（括号内或末尾英文）"""
    # 括号内英文: 星际穿越 (Interstellar)
    m = re.search(r'[（(]([A-Za-z][^）)]+)[）)]', keyword)
    if m:
        return m.group(1).strip()
    # 末尾英文块（含年份、季集号）
    m = re.search(r'([A-Za-z][A-Za-z0-9\s\.\-:]{3,})', keyword)
    if m:
        result = m.group(1).strip()
        result = re.sub(r'\s+[A-Z]$', '', result).strip()
        if len(result) >= 3:
            return result
    return None


def detect_type(keyword):
    """智能判断资源类型"""
    kw = keyword.lower()
    # 视频链接
    url_patterns = ["http://", "https://", "www.", "youtu", "bilibili", "b23.tv",
                    "tiktok", "douyin", "instagram", "twitter", "weibo"]
    if any(p in kw for p in url_patterns):
        return "video_url"
    # 磁力/种子
    if kw.startswith("magnet:") or kw.endswith(".torrent"):
        return "magnet"
    # 动漫特征
    anime_patterns = ["动漫", "动画", "番剧", "新番", "ova", "特典", "字幕组",
                      "季", "完结", "连载", "漫画", "轻小说",
                      r"s\d+e\d+", r"ep\d+", r"\d+话", r"\d+集",
                      "attack on titan", "one piece", "naruto", "demon slayer",
                      "鬼灭", "海贼", "火影", "进击", "巨人", "咒术", "回战"]
    if any(re.search(p, kw) for p in anime_patterns):
        return "anime"
    # 美剧特征
    tv_patterns = [r"s\d{2}e\d{2}", "season", "episode", "美剧", "英剧", "韩剧"]
    if any(re.search(p, kw) for p in tv_patterns):
        return "tv"
    # 软件/游戏
    soft_patterns = ["软件", "游戏", "破解", "安装包", ".exe", ".apk", "steam",
                     "keygen", "crack", "portable"]
    if any(p in kw for p in soft_patterns):
        return "software"
    # 音乐
    music_patterns = ["音乐", "专辑", "单曲", "flac", "mp3", "无损", "ost", "soundtrack"]
    if any(p in kw for p in music_patterns):
        return "music"
    # 电子书
    book_patterns = ["电子书", "epub", "pdf", "小说", "漫画", "manga", "comic"]
    if any(p in kw for p in book_patterns):
        return "book"
    # 默认：电影/通用
    return "general"


def hunt(keyword, mode=None, limit=8, verbose=False, pan_only=False, torrent_only=False, page=1):
    resource_type = mode or detect_type(keyword)

    print(f"🎯 正在搜索: {keyword}")
    print(f"📌 类型判断: {resource_type}")
    print()

    # 视频链接直接处理
    if resource_type == "video_url":
        print("🎬 检测到视频链接，获取画质信息...")
        out, code = run("video.py", ["info", keyword])
        print(out)
        return

    # 磁力直接输出
    if resource_type == "magnet":
        print(f"🧲 磁力链接:\n{keyword}")
        return

    results = []
    pan_output = ""
    torrent_output = ""

    # ── 并发搜索：网盘 + 种子 ──────────────────────────────────
    import threading

    # 准备网盘关键词
    pan_kw = keyword
    if not torrent_only and has_chinese(keyword):
        cn_only = re.sub(r'[A-Za-z]+', ' ', keyword).strip()
        cn_only = re.sub(r'\b(19|20)\d{2}\b', '', cn_only).strip()
        cn_only = re.sub(r'\s{2,}', ' ', cn_only).strip()
        if len(cn_only) >= 2:
            pan_kw = cn_only
    pan_kw_base = pan_kw  # 保存原始关键词用于回退
    if resource_type == "music" and not any(k in pan_kw for k in ["无损", "flac", "FLAC", "mp3", "ost"]):
        pan_kw = pan_kw + " 无损"

    # 准备种子关键词
    torrent_kw = keyword
    torrent_extra = []
    if not pan_only:
        if resource_type == "anime": torrent_extra = ["--anime"]
        elif resource_type == "tv": torrent_extra = ["--tv"]
        elif resource_type in ("general", "movie"): torrent_extra = ["--movie"]
        if has_chinese(keyword):
            en = cn_to_en_hint(keyword)
            if en:
                torrent_kw = en

    # 并发执行
    def do_pan():
        if torrent_only:
            return
        print("🔍 搜索网盘资源...")
        pan_args = [pan_kw, "--fallback", "--page", str(page)]
        if limit <= 3:  # quick 模式，每类只显示1条
            pan_args += ["--max", "1"]
        out, code = run("pansou.py", pan_args, timeout=18)
        if code == 0 and "未找到" not in out and "❌" not in out:
            pan_output_box[0] = out
            print("  ✓ 网盘搜索完成")
        elif pan_kw != pan_kw_base:
            # 带修饰词搜索失败，回退到原始关键词
            print(f"  🔄 回退搜索: {pan_kw_base}")
            out2, code2 = run("pansou.py", [pan_kw_base, "--fallback", "--page", str(page)], timeout=18)
            if code2 == 0 and "未找到" not in out2 and "❌" not in out2:
                pan_output_box[0] = out2
                print("  ✓ 网盘搜索完成（回退）")
            else:
                print("  ⚠️ 网盘无结果")
        else:
            # 尝试英文名回退（如果有英文提示）
            en_fallback = cn_to_en_hint(keyword)
            if en_fallback and en_fallback != keyword:
                print(f"  🔄 英文回退搜索: {en_fallback}")
                out3, code3 = run("pansou.py", [en_fallback, "--fallback", "--page", str(page)], timeout=18)
                if code3 == 0 and "未找到" not in out3 and "❌" not in out3:
                    pan_output_box[0] = out3
                    print("  ✓ 网盘搜索完成（英文回退）")
                else:
                    print("  ⚠️ 网盘无结果")
            else:
                print("  ⚠️ 网盘无结果")

    def do_torrent():
        if pan_only:
            return
        # 纯中文且无英文名提示时，TPB 搜索无意义，跳过
        if has_chinese(keyword) and torrent_kw == keyword:
            print("🧲 种子搜索跳过（纯中文，建议加英文名）")
            return
        print("🧲 搜索种子资源...")
        if torrent_kw != keyword:
            print(f"  💡 中文转英文搜索: {torrent_kw}")
        out, code = run("torrent.py", [torrent_kw, "--limit", str(limit)] + torrent_extra, timeout=18)
        if code == 0 and "未找到" not in out and "❌" not in out:
            torrent_output_box[0] = out
            print("  ✓ 种子搜索完成")
        else:
            print("  ⚠️ 种子无结果")

    pan_output_box = [""]
    torrent_output_box = [""]
    t1 = threading.Thread(target=do_pan)
    t2 = threading.Thread(target=do_torrent)
    t1.start(); t2.start()
    t1.join(timeout=20); t2.join(timeout=20)
    pan_output = pan_output_box[0]
    torrent_output = torrent_output_box[0]

    print()
    print("═" * 50)

    # 摘要行
    summary = []
    if pan_output:
        m = re.search(r'共\s*(\d+)\s*条结果', pan_output)
        if m: summary.append(f"🗂️ 网盘 {m.group(1)} 条")
    if torrent_output:
        m = re.search(r'共找到\s*(\d+)\s*条种子', torrent_output)
        if m: summary.append(f"🧲 种子 {m.group(1)} 条")
    if summary:
        print("📊 找到: " + " | ".join(summary))
        print()

    # 输出结果
    if pan_output:
        print(pan_output)
        print()

    if torrent_output:
        print(torrent_output)

    if not pan_output and not torrent_output:
        print(f"😔 未找到 '{keyword}' 的相关资源")
        print()
        print("💡 建议：")
        print("  • 尝试英文名（如：The Wandering Earth）")
        print("  • 加上年份（如：流浪地球 2023）")
        print("  • 减少关键词")
        print(f"  • 手动搜索: https://www.2fun.live/pan?kw={keyword}")
    elif torrent_output and not pan_output:
        print()
        print("💡 磁力链接使用方法：复制磁力链接到 qBittorrent/迅雷 等下载器打开")


def main():
    parser = argparse.ArgumentParser(
        description="🎯 Resource Hunter — 全路径资源获取",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  hunt.py '流浪地球2'              # 自动搜索
  hunt.py '进击的巨人' --anime     # 动漫模式
  hunt.py 'Breaking Bad' --tv      # 美剧模式
  hunt.py 'https://youtu.be/xxx'  # 视频下载
  hunt.py '软件名' --software      # 软件搜索
        """
    )
    parser.add_argument("keyword", help="搜索关键词或视频链接")
    parser.add_argument("--anime", action="store_true", help="动漫模式")
    parser.add_argument("--tv", action="store_true", help="美剧/剧集模式")
    parser.add_argument("--movie", action="store_true", help="电影模式")
    parser.add_argument("--software", action="store_true", help="软件模式")
    parser.add_argument("--music", action="store_true", help="音乐模式")
    parser.add_argument("--limit", type=int, default=8, help="种子最多显示数")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--pan-only", action="store_true", help="只搜网盘")
    parser.add_argument("--torrent-only", action="store_true", help="只搜种子")
    parser.add_argument("--page", type=int, default=1, help="网盘结果页码")
    parser.add_argument("--quick", action="store_true", help="快速模式：只返回最佳结果")
    parser.add_argument("--sub", action="store_true", help="优先搜索带中文字幕版本")
    parser.add_argument("--4k", action="store_true", dest="uhd", help="优先搜索4K版本")
    args = parser.parse_args()

    mode = None
    if args.anime: mode = "anime"
    elif args.tv: mode = "tv"
    elif args.movie: mode = "movie"
    elif args.software: mode = "software"
    elif args.music: mode = "music"

    lim = 3 if args.quick else args.limit
    kw = args.keyword
    if args.sub:
        kw = kw + " 中字" if not any(w in kw for w in ["中字", "字幕", "subtitle"]) else kw
    if args.uhd:
        kw = kw + " 4K" if "4k" not in kw.lower() and "2160" not in kw else kw
    hunt(kw, mode, lim, args.verbose,
         pan_only=args.pan_only, torrent_only=args.torrent_only, page=args.page)


if __name__ == "__main__":
    main()
