#!/usr/bin/env python3
"""
Fetch OpenRouter Rankings via Browser Automation

This script uses agent-browser CLI to fetch JavaScript-rendered content
from OpenRouter rankings page.

Requirements:
- agent-browser CLI installed
- Run after loading browser-automation skill

Usage:
    python3 fetch_rankings.py              # Get top models ranking
    python3 fetch_rankings.py --apps       # Get apps ranking
    python3 fetch_rankings.py --market     # Get market share

Security Note:
- Uses subprocess.run() with shell=False for security
- All commands are hardcoded, no user input passed to shell
"""

import subprocess
import json
import re
import sys
from datetime import datetime


def run_browser_command(args: list) -> str:
    """
    Run agent-browser command and return output.
    
    Security: Uses shell=False (default) to prevent command injection.
    All arguments are passed as a list, not as a shell command string.
    """
    # agent-browser is the CLI tool, args is a list of arguments
    # Example: ['open', 'https://example.com']
    cmd = ['agent-browser'] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return ""
    return result.stdout


def fetch_rankings():
    """Fetch OpenRouter rankings page via browser"""
    print("Fetching OpenRouter rankings via browser...")
    
    # Open page and get content
    # Using shell=False by passing args as a list
    run_browser_command(['open', 'https://openrouter.ai/rankings'])
    run_browser_command(['wait', '--load', 'networkidle'])
    output = run_browser_command(['eval', 'document.body.innerText'])
    
    return output


def parse_top_models(text: str) -> list:
    """Parse top models from page text"""
    models = []
    
    # Pattern: "1.\nMiniMax M2.5\nby\nminimax\n1.75T tokens\n6%"
    pattern = r'(\d+)\.\n([^\n]+)\nby\n([^\n]+)\n([\d.]+[TB]) tokens\n([+-]?\d+%)?(new)?'
    
    matches = re.findall(pattern, text)
    for match in matches:
        rank, model, provider, tokens, change, is_new = match
        models.append({
            "rank": int(rank),
            "model": model.strip(),
            "provider": provider.strip(),
            "tokens": tokens,
            "change": change if change else ("new" if is_new else "N/A")
        })
    
    return models


def parse_top_apps(text: str) -> list:
    """Parse top apps from page text"""
    apps = []
    
    # Find the Top Apps section
    apps_section = text.split("Top Apps")[-1] if "Top Apps" in text else text
    
    # Pattern for apps: "1.\nOpenClaw \nThe AI that actually does things\n552Btokens"
    pattern = r'(\d+)\.\n([^\n]+)\n([^\n]+)\n([\d.]+[TB])tokens'
    
    matches = re.findall(pattern, apps_section)
    for match in matches:
        rank, name, description, tokens = match
        apps.append({
            "rank": int(rank),
            "name": name.strip(),
            "description": description.strip(),
            "tokens": tokens
        })
    
    return apps


def format_models_table(models: list) -> str:
    """Format models as markdown table"""
    lines = [
        "=" * 70,
        "    OpenRouter Top Models (Weekly Usage)",
        "=" * 70,
        "",
        f"{'Rank':<6} {'Model':<30} {'Provider':<15} {'Tokens':<12} {'Change'}",
        "-" * 70
    ]
    
    for m in models:
        lines.append(f"{m['rank']:<6} {m['model']:<30} {m['provider']:<15} {m['tokens']:<12} {m['change']}")
    
    lines.extend([
        "-" * 70,
        f"Total: {len(models)} models",
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ])
    
    return "\n".join(lines)


def format_apps_table(apps: list) -> str:
    """Format apps as markdown table"""
    lines = [
        "=" * 70,
        "    OpenRouter Top Apps (Daily Usage)",
        "=" * 70,
        "",
        f"{'Rank':<6} {'App Name':<25} {'Tokens':<12}",
        "-" * 70
    ]
    
    for a in apps:
        lines.append(f"{a['rank']:<6} {a['name']:<25} {a['tokens']:<12}")
    
    lines.extend([
        "-" * 70,
        f"Total: {len(apps)} apps",
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ])
    
    return "\n".join(lines)


def main():
    """Main function"""
    mode = "models"
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--apps":
            mode = "apps"
        elif arg == "--market":
            mode = "market"
        elif arg in ["-h", "--help"]:
            print(__doc__)
            return
    
    # Fetch page content
    text = fetch_rankings()
    
    if not text:
        print("Failed to fetch rankings", file=sys.stderr)
        sys.exit(1)
    
    # Clean up JSON string if needed
    if text.startswith('"') and text.endswith('"'):
        text = json.loads(text)
    
    # Parse and display
    if mode == "models":
        models = parse_top_models(text)
        if models:
            print(format_models_table(models))
        else:
            print("No models found in page content")
            print("\n--- Raw Content (first 2000 chars) ---")
            print(text[:2000])
    elif mode == "apps":
        apps = parse_top_apps(text)
        if apps:
            print(format_apps_table(apps))
        else:
            print("No apps found in page content")
    elif mode == "market":
        # Market share parsing would go here
        print("Market share data not yet implemented")
        print("\n--- Raw Content (first 2000 chars) ---")
        print(text[:2000])
    
    # Close browser
    run_browser_command(['close'])


if __name__ == "__main__":
    main()
