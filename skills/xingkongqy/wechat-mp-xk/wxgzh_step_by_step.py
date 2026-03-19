#!/usr/bin/env python3
"""
微信公众号文章发布工具 - 分步流程版
参考：https://github.com/lyhue1991/wxgzh

支持分步执行：
1. md2html - Markdown 转 HTML（应用 Knowledge-Base 主题）
2. fix - 修复 HTML（处理图片、移除不适合结构）
3. cover - 生成/上传封面图
4. publish - 发布到草稿箱

也可一键执行：article - 完成全部流程
"""

import sys
import requests
import json
import time
import os
import argparse
import tempfile
import re
from datetime import datetime

# 配置
APPID = os.environ.get('WX_APPID')
SECRET = os.environ.get('WX_SECRET')
TOKEN_FILE = '/tmp/wechat_token.json'
DEFAULT_OUTPUT_DIR = './.wxgzh'

# ==================== 工具函数 ====================

def get_access_token():
    """获取 stable_access_token"""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if time.time() < data.get('expires_at', 0):
                    return data['access_token']
        except:
            pass
    
    url = 'https://api.weixin.qq.com/cgi-bin/stable_token'
    data = {
        'grant_type': 'client_credential',
        'appid': APPID,
        'secret': SECRET,
        'force_refresh': False
    }
    # 使用 ensure_ascii=False 防止中文转义
    resp = requests.post(
        url,
        data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
        timeout=10,
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    result = resp.json()
    
    if 'access_token' in result:
        result['expires_at'] = time.time() + 7000
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
        return result['access_token']
    else:
        raise Exception(f"Token 获取失败：{result}")

def extract_front_matter(md_content):
    """提取 Front Matter 元数据"""
    front_matter = {}
    content = md_content
    
    if md_content.startswith('---'):
        parts = md_content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            content = parts[2].strip()
            
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    front_matter[key.strip()] = value.strip().strip('"\'')
    
    return front_matter, content

def markdown_to_kb_html(md_content):
    """Markdown 转 Knowledge-Base 风格 HTML"""
    
    # 提取 Front Matter
    front_matter, content = extract_front_matter(md_content)
    
    lines = content.split('\n')
    html_parts = []
    
    # 容器开始
    html_parts.append('<section id="wemd" style="padding: 30px 24px; max-width: 677px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', \'Helvetica Neue\', \'PingFang SC\', sans-serif; color: #37352F; word-break: break-word;">')
    
    in_code_block = False
    in_table = False
    table_rows = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # 代码块
        if line_stripped.startswith('```'):
            if in_code_block:
                html_parts.append('</code></pre>')
                in_code_block = False
            else:
                html_parts.append('<pre style="background: #F7F6F3; padding: 20px; border-radius: 4px; overflow-x: auto;"><code style="color: #EB5757; font-family: \'SFMono-Regular\', Consolas, monospace; font-size: 13px; line-height: 1.6;">')
                in_code_block = True
            continue
        
        if in_code_block:
            html_parts.append(line_stripped)
            continue
        
        # 空行
        if not line_stripped:
            if in_table:
                html_parts.append('</table></section></section>')
                in_table = False
            continue
        
        # 一级标题
        if line_stripped.startswith('# '):
            title_text = line_stripped[2:]
            html_parts.append(f'<h1 style="margin-top: 50px; margin-bottom: 40px; text-align: left; border-bottom: 1px solid #E3E2E0; padding-bottom: 20px;"><span class="content" style="font-size: 28px; font-weight: 700; color: #37352F; display: inline-block; line-height: 1.2;">{title_text}</span></h1>')
            continue
        
        # 二级标题
        if line_stripped.startswith('## '):
            title_text = line_stripped[3:]
            html_parts.append(f'<h2 style="margin-top: 40px; margin-bottom: 20px; text-align: left;"><span class="content" style="display: block; font-size: 22px; font-weight: 600; color: #37352F; padding: 8px 12px; background-color: #F7F6F3; border-radius: 4px; line-height: 1.3;">{title_text}</span></h2>')
            continue
        
        # 三级标题
        if line_stripped.startswith('### '):
            title_text = line_stripped[4:]
            html_parts.append(f'<h3 style="margin-top: 30px; margin-bottom: 12px;"><span class="content" style="font-size: 18px; font-weight: 600; color: #37352F; display: inline-block; border-bottom: 3px solid #FDECC8; padding-bottom: 2px;">{title_text}</span></h3>')
            continue
        
        # 引用块
        if line_stripped.startswith('> '):
            quote_text = line_stripped[2:]
            html_parts.append(f'<div class="multiquote-1" style="margin: 24px 0; padding: 16px 16px 16px 20px; background-color: #F1F1EF; border: none; border-radius: 4px; border-left: 4px solid #37352F; overflow: visible !important;"><p style="margin: 0; color: #37352F; font-size: 15px; line-height: 1.6;">{quote_text}</p></div>')
            continue
        
        # 表格
        if line_stripped.startswith('|'):
            if not line_stripped.startswith('|---'):
                if not in_table:
                    html_parts.append('<section><section><table style="width: 100%; border-collapse: collapse; margin: 30px 0; font-size: 14px; border: 1px solid #E3E2E0; border-radius: 0;">')
                    in_table = True
                cells = [c.strip() for c in line_stripped.split('|') if c.strip()]
                if cells:
                    is_header = any(word in cells[0] for word in ['角色', '指标', '任务', '时间', '使用', '检查', '步骤', '文件', '项目', '状态', '版本'])
                    row_tag = 'th' if is_header else 'td'
                    row_style = 'background: #F7F6F3; color: #37352F; font-weight: 600;' if is_header else 'color: #37352F; background: #fff;'
                    cell_style = row_style + ' border: 1px solid #E3E2E0; padding: 10px 12px; text-align: left;'
                    cells_html = ''.join(f'<{row_tag} style="{cell_style}">{c}</{row_tag}>' for c in cells)
                    row = f'<tr>{cells_html}</tr>'
                    html_parts.append(row)
            continue
        elif in_table:
            html_parts.append('</table></section></section>')
            in_table = False
        
        # 列表
        if line_stripped.startswith('- ') or line_stripped.startswith('* '):
            list_text = line_stripped[2:]
            # 处理加粗
            list_text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #37352F; font-weight: 600; background-color: #FDECC8; padding: 2px 4px; margin: 0 2px; border-radius: 3px;">\1</strong>', list_text)
            html_parts.append(f'<ul style="list-style-type: disc; padding-left: 24px; margin: 16px 0; color: #37352F;"><li style="margin-bottom: 8px; line-height: 1.7;"><section style="color: #37352F; font-size: 16px;">{list_text}</section></li></ul>')
            continue
        
        # 普通段落
        paragraph = line_stripped
        # 处理加粗
        paragraph = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #37352F; font-weight: 600; background-color: #FDECC8; padding: 2px 4px; margin: 0 2px; border-radius: 3px;">\1</strong>', paragraph)
        html_parts.append(f'<section><section><p style="margin-top: 16px; margin-bottom: 16px; line-height: 1.75; letter-spacing: 0.2px; text-align: justify; color: #37352F; font-size: 16px;">{paragraph}</p></section></section>')
    
    # 关闭未闭合标签
    if in_code_block:
        html_parts.append('</code></pre>')
    if in_table:
        html_parts.append('</table></section></section>')
    
    # 容器结束
    html_parts.append('</section>')
    
    html_content = '\n'.join(html_parts)
    
    return html_content, front_matter

def upload_image(image_path, token=None):
    """上传图片获取 media_id"""
    if token is None:
        token = get_access_token()
    
    if not os.path.exists(image_path):
        return None
    
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    with open(image_path, 'rb') as f:
        files = {'media': f}
        resp = requests.post(url, files=files, timeout=30)
    
    # 图片上传返回的是 JSON 字符串，需要正确解析
    result = json.loads(resp.text, strict=False)
    return result.get('media_id')

def fix_html(html_content, upload_images=True):
    """修复 HTML（移除不适合结构，处理图片）"""
    # 移除 script 标签
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # 移除 iframe
    html_content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html_content, flags=re.DOTALL)
    
    # 移除 style 标签
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    
    # 处理图片（如果需要上传）
    if upload_images:
        # 这里可以添加图片上传逻辑
        pass
    
    return html_content

def create_draft(title, content, summary, thumb_media_id, author='黑白'):
    """创建草稿"""
    token = get_access_token()
    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
    
    data = {
        'articles': [{
            'title': title,
            'author': author,
            'digest': summary,
            'content': content,
            'thumb_media_id': thumb_media_id,
            'show_cover_pic': 1
        }]
    }
    
    # 关键修复：使用 ensure_ascii=False 防止中文转义
    resp = requests.post(
        url, 
        data=json.dumps(data, ensure_ascii=False).encode('utf-8'), 
        timeout=30, 
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    result = resp.json()
    
    if result.get('errcode', 0) == 0:
        return result.get('media_id'), result
    else:
        raise Exception(f"发布失败：{result.get('errmsg', '未知错误')}")

# ==================== 分步命令 ====================

def cmd_md2html(args):
    """Step 1: Markdown 转 HTML"""
    print("=" * 60)
    print("Step 1: Markdown 转 HTML（Knowledge-Base 主题）")
    print("=" * 60)
    
    if not os.path.exists(args.input):
        print(f"❌ 文件不存在：{args.input}")
        sys.exit(1)
    
    with open(args.input, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content, front_matter = markdown_to_kb_html(md_content)
    
    # 确定输出文件
    output_file = args.output
    if not output_file:
        output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        output_file = os.path.join(output_dir, f'{base_name}.html')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 已生成：{output_file}")
    print(f"   内容长度：{len(html_content)}")
    
    # 提取元数据
    if front_matter:
        print(f"   元数据：{front_matter}")
    
    return output_file, front_matter

def cmd_fix(args):
    """Step 2: 修复 HTML"""
    print("=" * 60)
    print("Step 2: 修复 HTML")
    print("=" * 60)
    
    if not os.path.exists(args.input):
        print(f"❌ 文件不存在：{args.input}")
        sys.exit(1)
    
    with open(args.input, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = fix_html(html_content, upload_images=not args.no_upload)
    
    # 输出文件
    output_file = args.output or args.input
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 已修复：{output_file}")
    print(f"   内容长度：{len(html_content)}")
    
    return output_file

def cmd_cover(args):
    """Step 3: 上传封面图"""
    print("=" * 60)
    print("Step 3: 上传封面图")
    print("=" * 60)
    
    if not args.cover:
        print("❌ 请指定封面图路径：--cover <path>")
        sys.exit(1)
    
    media_id = upload_image(args.cover)
    
    if media_id:
        print(f"✅ 封面图上传成功")
        print(f"   media_id: {media_id}")
        
        # 保存到文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({'media_id': media_id}, f, ensure_ascii=False)
            print(f"   已保存：{args.output}")
        
        return media_id
    else:
        print("❌ 封面图上传失败")
        sys.exit(1)

def cmd_publish(args):
    """Step 4: 发布到草稿箱"""
    print("=" * 60)
    print("Step 4: 发布到草稿箱")
    print("=" * 60)
    
    # 读取 HTML
    if not os.path.exists(args.article):
        print(f"❌ 文章文件不存在：{args.article}")
        sys.exit(1)
    
    with open(args.article, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 读取封面
    thumb_media_id = None
    if args.cover:
        if os.path.exists(args.cover):
            thumb_media_id = upload_image(args.cover)
        else:
            # 可能是 media_id
            thumb_media_id = args.cover
    
    if not thumb_media_id:
        print("❌ 请指定封面图：--cover <path>")
        sys.exit(1)
    
    # 发布
    title = args.title or os.path.basename(args.article)
    author = args.author or '黑白'
    summary = args.summary or ''
    
    try:
        media_id, result = create_draft(title, content, summary, thumb_media_id, author)
        print(f"✅ 发布成功！")
        print(f"   草稿 ID: {media_id}")
        print(f"   标题：{title}")
        print(f"   作者：{author}")
        print(f"   请前往公众号后台查看：https://mp.weixin.qq.com")
        return media_id
    except Exception as e:
        print(f"❌ 发布失败：{e}")
        sys.exit(1)

def cmd_article(args):
    """一键发布：完成全部流程"""
    print("=" * 60)
    print("一键发布：Markdown → 公众号草稿箱")
    print("=" * 60)
    print()
    
    # Step 1: md2html
    html_file, front_matter = cmd_md2html(args)
    print()
    
    # Step 2: fix
    args.input = html_file
    args.output = html_file
    if not hasattr(args, 'no_upload'):
        args.no_upload = False
    cmd_fix(args)
    print()
    
    # Step 3: cover
    if args.cover:
        cover_file = os.path.join(os.path.dirname(html_file), 'cover.json')
        args.output = cover_file
        media_id = cmd_cover(args)
        print()
    else:
        media_id = None
        print("⚠️ 未指定封面图")
        print()
    
    # Step 4: publish
    args.article = html_file
    args.title = args.title or front_matter.get('title')
    args.author = args.author or front_matter.get('author', '黑白')
    args.summary = args.summary or front_matter.get('digest', '')
    args.cover = media_id or args.cover
    cmd_publish(args)

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description='微信公众号文章发布工具 - 分步流程版')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # md2html 命令
    p_md2html = subparsers.add_parser('md2html', help='Markdown 转 HTML')
    p_md2html.add_argument('input', help='输入 Markdown 文件')
    p_md2html.add_argument('-o', '--output', help='输出 HTML 文件')
    p_md2html.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help='输出目录')
    p_md2html.set_defaults(func=cmd_md2html)
    
    # fix 命令
    p_fix = subparsers.add_parser('fix', help='修复 HTML')
    p_fix.add_argument('input', help='输入 HTML 文件')
    p_fix.add_argument('-o', '--output', help='输出 HTML 文件')
    p_fix.add_argument('--no-upload', action='store_true', help='不上传图片')
    p_fix.set_defaults(func=cmd_fix)
    
    # cover 命令
    p_cover = subparsers.add_parser('cover', help='上传封面图')
    p_cover.add_argument('--cover', required=True, help='封面图路径')
    p_cover.add_argument('-o', '--output', help='保存 media_id 的文件')
    p_cover.set_defaults(func=cmd_cover)
    
    # publish 命令
    p_publish = subparsers.add_parser('publish', help='发布到草稿箱')
    p_publish.add_argument('--article', required=True, help='HTML 文章文件')
    p_publish.add_argument('--cover', required=True, help='封面图路径或 media_id')
    p_publish.add_argument('--title', help='文章标题')
    p_publish.add_argument('--author', default='黑白', help='作者名')
    p_publish.add_argument('--summary', default='', help='文章摘要')
    p_publish.set_defaults(func=cmd_publish)
    
    # article 命令（一键发布）
    p_article = subparsers.add_parser('article', help='一键发布')
    p_article.add_argument('input', help='输入 Markdown 文件')
    p_article.add_argument('-o', '--output', help='输出 HTML 文件')
    p_article.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help='输出目录')
    p_article.add_argument('--cover', help='封面图路径')
    p_article.add_argument('--title', help='文章标题')
    p_article.add_argument('--author', default='黑白', help='作者名')
    p_article.add_argument('--summary', default='', help='文章摘要')
    p_article.set_defaults(func=cmd_article)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == '__main__':
    main()
