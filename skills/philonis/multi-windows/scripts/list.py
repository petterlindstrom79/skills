#!/usr/bin/env python3
"""列出所有任务"""
import json
import os
import sys
from datetime import datetime

TASKS_DIR = os.path.expanduser("~/.openclaw/workspace/memory/tasks")
INDEX_FILE = os.path.join(TASKS_DIR, "tasks.json")
ARCHIVED_FILE = os.path.join(TASKS_DIR, "archived.json")

def list_tasks(show_archived=False):
    if show_archived:
        if not os.path.exists(ARCHIVED_FILE):
            return "暂无归档任务"
        
        with open(ARCHIVED_FILE, "r") as f:
            tasks = json.load(f)
        
        if not tasks:
            return "暂无归档任务"
        
        title = "📁 归档窗口列表："
    else:
        if not os.path.exists(INDEX_FILE):
            return "暂无任务"
        
        with open(INDEX_FILE, "r") as f:
            tasks = json.load(f)
        
        # 只显示非归档任务
        tasks = {k: v for k, v in tasks.items() if not v.get("archived_at")}
        
        if not tasks:
            return "暂无进行中的任务"
        
        title = "📋 窗口列表："
    
    # 按创建时间排序
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1].get("created", ""), reverse=True)
    
    lines = [title, "", "| ID | 名称 | 状态 | 创建时间 |", "|---|---|---|---|"]
    for task_id, info in sorted_tasks:
        created = info.get("created", "")
        if created:
            try:
                dt = datetime.fromisoformat(created)
                created = dt.strftime("%m-%d %H:%M")
            except:
                pass
        status = info.get("status", "-")
        if info.get("archived_at"):
            status = "📁 已归档"
        lines.append(f"| {task_id} | {info.get('name', '-')} | {status} | {created} |")
    
    return "\n".join(lines)

if __name__ == "__main__":
    show_archived = "--archived" in sys.argv or "-a" in sys.argv
    print(list_tasks(show_archived))
