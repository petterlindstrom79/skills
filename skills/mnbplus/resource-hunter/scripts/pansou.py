#!/usr/bin/env python3
"""
PanSou - 网盘资源聚合搜索
支持阿里云盘、夸克、百度、115、PikPak 等
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse

# 2fun.live 为免费公开 API，无需 API key

CLOUD_ICONS = {
    "aliyun": "☁️ 阿里云盘",
    "alipan": "☁️ 阿里云盘",
    "quark": "⚡ 夸克网盘",
    "baidu": "🔵 百度网盘",
    "115": "🔷 115网盘",
    "pikpak": "🟣 PikPak",
    "uc": "🟠 UC网盘",
    "xunlei": "🔴 迅雷云盘",
    "thunder": "🔴 迅雷云盘",
    "123": "🟢 123网盘",
    "tianyi": "🔹 天翼云盘",
    "189": "🔹 天翼云盘",
    "magnet": "🧲 磁力链接",
    "ed2k": "🔗 ED2K",
    "mobile": "📱 移动云盘",
    "mega": "🌐 MEGA",
    "mediafire": "🌐 MediaFire",
    "gdrive": "🌐 Google Drive",
    "onedrive": "🌐 OneDrive",
    "cowtransfer": "🐄 奶牛快传",
    "lanzou": "🔗 蓝奏云",
    "other": "📦 其他",
}

# URL 域名到云盘类型的映射
DOMAIN_TYPE_MAP = {
    "aliyundrive.com": "aliyun",
    "alipan.com": "aliyun",
    "pan.quark.cn": "quark",
    "pan.baidu.com": "baidu",
    "115.com": "115",
    "115cdn.com": "115",
    "mypikpak.com": "pikpak",
    "drive.uc.cn": "uc",
    "pan.xunlei.com": "xunlei",
    "123pan.com": "123",
    "123684.com": "123",
    "123865.com": "123",
    "123912.com": "123",
    "cloud.189.cn": "tianyi",
    "caiyun.139.com": "mobile",
    "pan.pikpak.com": "pikpak",
    "mega.nz": "mega",
    "mediafire.com": "mediafire",
    "drive.google.com": "gdrive",
    "onedrive.live.com": "onedrive",
    "cowtransfer.com": "cowtransfer",
    "lanzou": "lanzou",
    "lanzoux.com": "lanzou",
    "lanzouq.com": "lanzou",
}


def infer_type_from_url(url):
    """从 URL 域名推断云盘类型"""
    # 精确域名匹配
    for domain, cloud_type in DOMAIN_TYPE_MAP.items():
        if domain in url:
            return cloud_type
    # 模糊匹配：123网盘有大量子域名变体 (123xxx.com)
    if re.search(r'12[0-9]{3,4}\.com', url):
        return "123"
    # 磁力/ED2K
    if url.startswith("magnet:") or "btih" in url:
        return "magnet"
    if url.startswith("ed2k://"):
        return "ed2k"
    return "other"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def fetch_json(url, timeout=12):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"_error": str(e)}


def extract_password(url):
    """从 URL 或标题中提取密码"""
    # 先 URL 解码
    decoded = urllib.parse.unquote(url)
    # URL 参数: ?password=xxx / ?pwd=xxx / ?pass=xxx
    m = re.search(r'[?&](?:password|pwd|pass)=([^&#]+)', decoded)
    if m:
        return m.group(1).rstrip('#')
    # 中文提取码格式（含全角冒号）: 提取码:XXXX 或 提取码：XXXX
    m = re.search(r'提取码[:：]\s*([A-Za-z0-9]{4,8})', decoded)
    if m:
        return m.group(1)
    # 裸密码格式: ?XXXX（问号后直接跟4-8位字母数字，无等号）
    m = re.search(r'\?([A-Za-z0-9]{4,8})$', decoded)
    if m:
        return m.group(1)
    return ""


def extract_clean_url(url):
    """提取干净的 URL（去掉中文提取码后缀和多余字符）"""
    decoded = urllib.parse.unquote(url)
    # 去掉 提取码:XXXX 后缀（含全角冒号）
    decoded = re.sub(r'提取码[:：]\s*[A-Za-z0-9]+', '', decoded).strip()
    # 去掉末尾粘连的4-8位提取码（如 /s/OXIWhZY4K → /s/OXIWh，排除正常路径hash）
    # 123pan 路径通常是 /s/XXXXX，末尾粘连的是额外的大写字母数字
    decoded = re.sub(r'([a-z0-9]{4,8})([A-Z]{4,8})$', r'\1', decoded)
    # 去掉末尾多余字符
    decoded = decoded.rstrip('?&#, ')
    return decoded


def clean_url(url):
    """去掉 URL 中的密码参数，返回干净链接"""
    return re.sub(r'[?&](?:password|pwd|pass)=[^&]*', '', url).rstrip('?&')


# 默认优先搜索的云盘类型（按优先级排序）
DEFAULT_CLOUD_TYPES = ["aliyun", "quark", "115", "baidu", "pikpak", "123", "uc", "xunlei"]

# 内存缓存（进程级，TTL 30分钟）
_CACHE = {}
_CACHE_TTL = 1800  # 秒


def _cache_get(key):
    if key in _CACHE:
        data, ts = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _CACHE[key]
    return None


def _cache_set(key, data):
    _CACHE[key] = (data, time.time())


def search_2fun(keyword, page=1, page_size=20, types=None):
    """搜索 s.2fun.live 接口"""
    params = {"q": keyword, "page": page, "pageSize": page_size}
    if types:
        params["cloud"] = ",".join(types)
    url = "https://s.2fun.live/api/search?" + urllib.parse.urlencode(params)
    return fetch_json(url)


def search_2fun_multi(keyword, page=1, per_type=5):
    """分类型搜索，每种云盘各取 per_type 条，聚合去重（带缓存）"""
    cache_key = f"multi:{keyword}:{page}:{per_type}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    import threading
    all_results = []
    lock = threading.Lock()
    total_ref = [0]

    def fetch_type(cloud_type):
        data = search_2fun(keyword, page, per_type, [cloud_type])
        if data and "results" in data:
            with lock:
                all_results.extend(data["results"])
                if data.get("total", 0) > total_ref[0]:
                    total_ref[0] = data["total"]

    threads = [threading.Thread(target=fetch_type, args=(t,)) for t in DEFAULT_CLOUD_TYPES]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=12)

    result = {"results": all_results, "total": total_ref[0]}
    _cache_set(cache_key, result)
    return result


def search_hunhepan(keyword, page=1):
    """备用：hunhepan.com"""
    params = {"q": keyword, "page": page}
    url = "https://www.hunhepan.com/api/search?" + urllib.parse.urlencode(params)
    return fetch_json(url)


def normalize(data, source="2fun"):
    """归一化为统一格式列表"""
    items = []

    # s.2fun.live 格式：{results: [...], total: N}
    if "results" in data and isinstance(data["results"], list):
        for r in data["results"]:
            raw_url = r.get("url", "")
            pwd = extract_password(raw_url) or r.get("pwd") or r.get("password", "")
            clean_url = extract_clean_url(raw_url)
            api_type = r.get("netdiskType") or r.get("cloud") or ""
            # API 标记 other 时用域名推断覆盖
            cloud_type = infer_type_from_url(clean_url) if api_type in ("", "other") else api_type
            raw_title = r.get("title", "")
            # 清理冗余前缀
            # 清理常见冗余前缀模式
            clean_title = raw_title
            clean_title = re.sub(r'^[^\u4e00-\u9fa5a-zA-Z0-9]*?(名称|资源名称|资源|标题)[】\]）)]*[：:：]\s*', '', clean_title).strip()
            clean_title = re.sub(r'^【(名称|资源名称|资源|标题)】[：:：]?\s*', '', clean_title).strip()
            # 处理 #标签🗄资源名称: 格式
            clean_title = re.sub(r'^#\S+\s*(资源名称|名称|标题)[：:：]\s*', '', clean_title).strip()
            if not clean_title:
                clean_title = raw_title
            items.append({
                "title": clean_title or raw_title,
                "url": clean_url,
                "type": cloud_type,
                "pwd": pwd,
                "source": r.get("source", source),
            })
        return items, data.get("total", len(items))

    # 通用 data 字段格式
    if "data" in data:
        raw = data["data"]
        if isinstance(raw, list):
            for r in raw:
                raw_url = r.get("url") or r.get("link", "")
                items.append({
                    "title": r.get("title") or r.get("name", ""),
                    "url": raw_url,
                    "type": r.get("netdiskType") or r.get("cloud") or r.get("type", "other"),
                    "pwd": extract_password(raw_url) or r.get("pwd") or r.get("password", ""),
                    "source": source,
                })
        elif isinstance(raw, dict):
            for cloud_type, links in raw.items():
                for link in (links if isinstance(links, list) else []):
                    if isinstance(link, str):
                        items.append({"url": link, "type": cloud_type, "title": "", "pwd": extract_password(link), "source": source})
                    elif isinstance(link, dict):
                        raw_url = link.get("url", "")
                        items.append({
                            "title": link.get("title", ""),
                            "url": raw_url,
                            "type": cloud_type,
                            "pwd": extract_password(raw_url) or link.get("pwd", ""),
                            "source": source,
                        })
        return items, data.get("total", len(items))

    return items, 0


JUNK_PATTERNS = re.compile(
    r'(javdb|jav[^a-z]|\[sis001\]|第一会所|パンスト|エロ|痴女|av女优|无码|有码|fc2|uncensored'
    r'|ギャル|ギャラ|巨乳|美乳|SEX|sex(?!y)|ギャラ飲み|ビッチ|ロリ|露出|盗撮|强奸|强制)',
    re.IGNORECASE
)

# 日文字符检测（大量日文通常是不相关内容）
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]{10,}')


def is_junk(item):
    """过滤垃圾/不相关结果"""
    title = item.get("title", "")
    url = item.get("url", "").lower()
    # 关键词过滤
    if JUNK_PATTERNS.search(title) or JUNK_PATTERNS.search(url):
        return True
    # 大量日文片假名/平假名（非动漫关键词搜索时过滤）
    if JAPANESE_PATTERN.search(title):
        return True
    # 标题过短（无意义）
    if len(title.strip()) < 2:
        return True
    # URL 为空
    if not url or len(url) < 10:
        return True
    return False


# 域名标准化映射（同一网盘的不同域名）
DOMAIN_NORMALIZE = {
    '115cdn.com': '115.com',
    'anxia.com': 'aliyundrive.com',
    'alipan.com': 'aliyundrive.com',
}


def url_key(url):
    """提取 URL 的去重 key：域名+路径最后一段（去掉末尾可能粘连的大写提取码）"""
    path = re.sub(r'[?#].*$', '', url).rstrip('/')
    # 提取域名
    domain_m = re.match(r'https?://([^/]+)', path)
    domain = domain_m.group(1) if domain_m else ''
    # 标准化同一网盘的不同域名
    domain = DOMAIN_NORMALIZE.get(domain, domain)
    # 提取最后一段路径（分享码）
    last_seg = path.split('/')[-1] if '/' in path else path
    # 去掉末尾粘连的4-8位纯大写字母（提取码特征）
    last_seg = re.sub(r'[A-Z0-9]{4,8}$', '', last_seg).rstrip('-_')
    return domain + '/' + last_seg


def deduplicate(items):
    """去重：同路径 URL 保留有密码的那条"""
    seen = {}
    for item in items:
        key = url_key(item["url"])
        if key not in seen:
            seen[key] = item
        elif item["pwd"] and not seen[key]["pwd"]:
            seen[key] = item  # 有密码的优先
    return list(seen.values())


# 云盘优先级（数字越小越优先）
CLOUD_PRIORITY = {
    "aliyun": 1, "alipan": 1,
    "quark": 2,
    "115": 3,
    "pikpak": 4,
    "uc": 5,
    "baidu": 6,
    "123": 7,
    "xunlei": 8,
    "tianyi": 9,
    "magnet": 10,
    "other": 99,
}

QUALITY_SCORE = re.compile(
    r'(4k|2160p|uhd|remux|原盘|杜比|dolby|hdr|dovi)',
    re.IGNORECASE
)


def item_score(item):
    """计算结果质量分（越高越好）"""
    title = item.get("title", "").lower()
    score = 0
    if item.get("pwd"):
        score += 10  # 有密码加分
    quality_hits = len(QUALITY_SCORE.findall(title))
    score += quality_hits * 5  # 质量关键词
    return score


def group_by_type(items):
    groups = {}
    clean = deduplicate([r for r in items if not is_junk(r)])
    for r in clean:
        t = r.get("type", "other").lower()
        groups.setdefault(t, []).append(r)
    # 每组内按质量分排序
    for t in groups:
        groups[t].sort(key=item_score, reverse=True)
    return groups


def sorted_groups(groups):
    """按云盘优先级排序分组"""
    return sorted(groups.items(), key=lambda x: (CLOUD_PRIORITY.get(x[0], 50), -len(x[1])))


def format_output(keyword, items, total, elapsed, max_per_type=3):
    lines = []
    elapsed_str = f" ({int(elapsed*1000)}ms)"
    lines.append(f"🔍 {keyword} — 共 {total} 条结果{elapsed_str}")
    lines.append("")

    if not items:
        lines.append("😔 未找到相关资源，建议尝试：")
        lines.append("  • 使用英文名搜索")
        lines.append("  • 减少关键词（如去掉年份）")
        lines.append(f"  • 直接访问: https://www.2fun.live/pan?kw={urllib.parse.quote(keyword)}")
        return "\n".join(lines)

    groups = group_by_type(items)
    for cloud_type, group_items in sorted_groups(groups):
        icon = CLOUD_ICONS.get(cloud_type, f"📦 {cloud_type}")
        lines.append(f"{icon} ({len(group_items)} 个)")
        for item in group_items[:max_per_type]:
            url = item["url"]
            pwd = item["pwd"]
            title = item["title"]
            if title:
                # 清理 HTML 标签和 emoji 前缀
                title = re.sub(r'<[^>]+>', '', title)
                title = re.sub(r'^[\U00010000-\U0010ffff\u2600-\u27BF]+\s*', '', title)
                lines.append(f"  📌 {title[:60]}")
            pwd_str = f"  🔑 密码: `{pwd}`" if pwd else ""
            lines.append(f"  🔗 `{url}`{pwd_str}")
        lines.append("")

    lines.append(f"🌐 更多结果: https://www.2fun.live/pan?kw={urllib.parse.quote(keyword)}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="网盘资源聚合搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--types", nargs="+", help="限定云盘类型")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--max", type=int, default=5, help="每类最多显示数量")
    parser.add_argument("--fallback", action="store_true", help="主接口失败时尝试备用")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    start = time.time()
    if args.types:
        # 用户指定类型：单次搜索
        data = search_2fun(args.keyword, args.page, args.page_size, args.types)
    else:
        # 默认：多类型并发搜索，每类取5条，结果更全面
        data = search_2fun_multi(args.keyword, args.page, per_type=5)
    elapsed = time.time() - start

    if (not data or "_error" in data) and args.fallback:
        sys.stderr.write("[warn] 主接口失败，切换备用...\n")
        data = search_hunhepan(args.keyword, args.page)

    if not data or "_error" in data:
        print(f"❌ 搜索失败", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    items, total = normalize(data)
    print(format_output(args.keyword, items, total, elapsed, max_per_type=args.max))


if __name__ == "__main__":
    main()
