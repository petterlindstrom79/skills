#!/usr/bin/env python3
"""
Torrent Search - 磁力/种子资源搜索
聚合 TPB / Nyaa / EZTV / YTS 多引擎
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
}

TRACKERS = (
    "&tr=udp://tracker.openbittorrent.com:80"
    "&tr=udp://tracker.opentrackr.org:1337"
    "&tr=udp://open.demonii.com:1337"
    "&tr=udp://tracker.torrent.eu.org:451"
    "&tr=udp://tracker.cyberia.is:6969"
    "&tr=udp://exodus.desync.com:6969"
    "&tr=udp://tracker.tiny-vps.com:6969"
    "&tr=udp://tracker.moeking.me:6969"
    "&tr=udp://tracker.dler.org:6969"
    "&tr=https://tracker.gbitt.info/announce"
    "&tr=https://tracker.tamersunion.org/announce"
)

# 质量关键词评分
QUALITY_PATTERNS = [
    (r'remux', 300),
    (r'2160p|4k|uhd', 200),
    (r'bluray|blu-ray|bdrip', 100),
    (r'1080p', 50),
    (r'webrip|web-dl|webdl', 20),
    (r'hevc|x265|h\.265', 10),
    (r'720p', -30),
    (r'cam|ts|hdts|hdrip|dvdscr', -500),
]


def quality_score(name: str, seeders: int, year: str = "") -> int:
    """综合质量评分：画质优先 + 做种数辅助 + 年份匹配"""
    score = min(seeders, 200)  # 做种数贡献（上限200，避免压制画质权重）
    name_lower = name.lower()
    for pattern, pts in QUALITY_PATTERNS:
        if re.search(pattern, name_lower):
            score += pts
    # 年份匹配加分
    if year and year in name:
        score += 30
    return score


def fetch(url, timeout=10):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def fetch_json(url, timeout=10):
    raw = fetch(url, timeout)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def format_size(size_bytes):
    if not size_bytes:
        return "?"
    size_bytes = int(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}PB"


def make_magnet(info_hash, name):
    return f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}{TRACKERS}"


# ── 引擎 1: ThePirateBay ──────────────────────────────────────────
def search_tpb(keyword, limit=10):
    url = f"https://apibay.org/q.php?q={urllib.parse.quote(keyword)}&cat=0"
    data = fetch_json(url)
    if not data or not isinstance(data, list):
        return []
    results = []
    for item in data[:limit]:
        if item.get("name") == "No results returned":
            break
        info_hash = item.get("info_hash", "")
        name = item.get("name", "")
        results.append({
            "title": name,
            "magnet": make_magnet(info_hash, name),
            "info_hash": info_hash,
            "size": format_size(item.get("size", 0)),
            "seeds": int(item.get("seeders", 0)),
            "leechs": int(item.get("leechers", 0)),
            "source": "TPB",
            "added": item.get("added", ""),
        })
    return results


# ── 引擎 2: Nyaa (动漫专用) ──────────────────────────────────────
def search_nyaa(keyword, limit=10, category="0_0"):
    url = f"https://nyaa.si/?f=0&c={category}&q={urllib.parse.quote(keyword)}&page=rss"
    raw = fetch(url, timeout=6)  # Nyaa 国内不稳定，快速失败
    if not raw:
        return []
    results = []
    items = re.findall(r"<item>(.*?)</item>", raw, re.DOTALL)
    for item in items[:limit]:
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item)
        magnet = re.search(r"<nyaa:magnetUri><!\[CDATA\[(.*?)\]\]></nyaa:magnetUri>", item)
        size = re.search(r"<nyaa:size>(.*?)</nyaa:size>", item)
        seeds = re.search(r"<nyaa:seeders>(\d+)</nyaa:seeders>", item)
        leechs = re.search(r"<nyaa:leechers>(\d+)</nyaa:leechers>", item)
        if title and magnet:
            results.append({
                "title": title.group(1),
                "magnet": magnet.group(1),
                "size": size.group(1) if size else "?",
                "seeds": int(seeds.group(1)) if seeds else 0,
                "leechs": int(leechs.group(1)) if leechs else 0,
                "source": "Nyaa",
                "added": "",
            })
    return sorted(results, key=lambda x: quality_score(x.get("title", ""), x.get("seeds", 0)), reverse=True)


# ── 引擎 3: YTS (高清电影专用) ────────────────────────────────────
def search_yts(keyword, limit=10):
    url = f"https://yts.mx/api/v2/list_movies.json?query_terms={urllib.parse.quote(keyword)}&limit={limit}&sort_by=seeds"
    data = fetch_json(url)
    if not data:
        return []
    movies = data.get("data", {}).get("movies") or []
    results = []
    for movie in movies[:limit]:
        title = movie.get("title_long", movie.get("title", ""))
        for torrent in movie.get("torrents", []):
            info_hash = torrent.get("hash", "")
            quality = torrent.get("quality", "")
            codec = torrent.get("video_codec", "")
            results.append({
                "title": f"{title} [{quality} {codec}]",
                "magnet": make_magnet(info_hash, title),
                "size": torrent.get("size", "?"),
                "seeds": torrent.get("seeds", 0),
                "leechs": torrent.get("peers", 0),
                "source": "YTS",
                "added": torrent.get("date_uploaded", ""),
            })
    return sorted(results, key=lambda x: quality_score(x.get("title", ""), x.get("seeds", 0)), reverse=True)


# ── 引擎 4: EZTV (美剧专用) ──────────────────────────────────────
def search_eztv(keyword, limit=10):
    url = f"https://eztv.re/api/get-torrents?imdb_id=0&limit={limit}&page=1&keywords={urllib.parse.quote(keyword)}"
    data = fetch_json(url)
    if not data:
        return []
    results = []
    for item in (data.get("torrents") or [])[:limit]:
        title = item.get("title", "")
        magnet = item.get("magnet_url", "")
        if not magnet:
            info_hash = item.get("hash", "")
            magnet = make_magnet(info_hash, title) if info_hash else ""
        if title and magnet:
            results.append({
                "title": title,
                "magnet": magnet,
                "size": format_size(item.get("size_bytes", 0)),
                "seeds": item.get("seeds", 0),
                "leechs": item.get("peers", 0),
                "source": "EZTV",
                "added": "",
            })
    return sorted(results, key=lambda x: quality_score(x.get("title", ""), x.get("seeds", 0)), reverse=True)


def deduplicate(results):
    seen = set()
    out = []
    for r in results:
        key = r["title"].lower()[:50]
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def seeds_icon(n):
    if n >= 100: return "🟢"
    if n >= 20: return "🟡"
    if n >= 1: return "🟠"
    return "🔴"


def format_output(keyword, results, limit):
    if not results:
        return (
            f"🧲 未找到 '{keyword}' 的种子\n"
            "💡 建议：\n"
            "  • 尝试英文名搜索\n"
            "  • 换用网盘搜索（pansou.py）\n"
            "  • 减少关键词"
        )
    lines = [f"🧲 {keyword} — 共找到 {len(results)} 条种子", ""]
    for i, r in enumerate(results[:limit], 1):
        icon = seeds_icon(r["seeds"])
        lines.append(f"{i}. {r['title'][:70]}")
        lines.append(f"   {icon} 做种:{r['seeds']} 下载:{r['leechs']} | 大小:{r['size']} | 来源:{r['source']}")
        lines.append(f"   `{r['magnet'][:120]}...`")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="磁力/种子多引擎搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--engine", choices=["tpb", "nyaa", "yts", "eztv", "all"], default="all")
    parser.add_argument("--limit", type=int, default=10, help="最多显示条数")
    parser.add_argument("--anime", action="store_true", help="动漫模式（Nyaa优先）")
    parser.add_argument("--movie", action="store_true", help="电影模式（YTS优先）")
    parser.add_argument("--tv", action="store_true", help="美剧模式（EZTV优先）")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    results = []

    if args.anime:
        # 并发搜索 Nyaa 和 TPB，避免 Nyaa 超时拖慢整体
        import threading
        nyaa_res, tpb_res = [], []
        def _nyaa(): nyaa_res.extend(search_nyaa(args.keyword, args.limit))
        def _tpb(): tpb_res.extend(search_tpb(args.keyword, max(args.limit * 2, 10)))
        t1 = threading.Thread(target=_nyaa)
        t2 = threading.Thread(target=_tpb)
        t1.start(); t2.start()
        t1.join(timeout=8); t2.join(timeout=12)
        results += nyaa_res + tpb_res
    elif args.movie:
        # YTS 国内不可用，直接用 TPB；多取以便质量排序后截取
        results += search_tpb(args.keyword, max(args.limit * 3, 20))
    elif args.tv:
        # 并发搜索 EZTV 和 TPB
        import threading
        eztv_res, tpb_res = [], []
        def _eztv(): eztv_res.extend(search_eztv(args.keyword, args.limit))
        def _tpb(): tpb_res.extend(search_tpb(args.keyword, max(args.limit * 2, 10)))
        t1 = threading.Thread(target=_eztv)
        t2 = threading.Thread(target=_tpb)
        t1.start(); t2.start()
        t1.join(timeout=10); t2.join(timeout=12)
        results += eztv_res + tpb_res
    elif args.engine == "tpb":
        results = search_tpb(args.keyword, args.limit)
    elif args.engine == "nyaa":
        results = search_nyaa(args.keyword, args.limit)
    elif args.engine == "yts":
        results = search_yts(args.keyword, args.limit)
    elif args.engine == "eztv":
        results = search_eztv(args.keyword, args.limit)
    else:  # all
        # 并发搜索所有引擎
        import threading
        tpb_res, nyaa_res = [], []
        def _tpb(): tpb_res.extend(search_tpb(args.keyword, max(args.limit * 3, 20)))
        def _nyaa(): nyaa_res.extend(search_nyaa(args.keyword, min(args.limit, 5)))
        t1 = threading.Thread(target=_tpb)
        t2 = threading.Thread(target=_nyaa)
        t1.start(); t2.start()
        t1.join(timeout=12); t2.join(timeout=8)
        results += tpb_res + nyaa_res
        # YTS 在国内不可用，跳过

    results = deduplicate(results)
    # 提取关键词里的年份
    year_m = re.search(r'\b(19|20)\d{2}\b', args.keyword)
    year = year_m.group(0) if year_m else ""
    results = sorted(results, key=lambda x: quality_score(x.get("title", ""), x.get("seeds", 0), year), reverse=True)

    if args.json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(format_output(args.keyword, results, args.limit))


if __name__ == "__main__":
    main()
