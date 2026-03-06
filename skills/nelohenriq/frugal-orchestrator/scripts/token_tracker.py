#!/usr/bin/env python3
"""
Frugal Orchestrator - Token Efficiency Tracker
Measures and reports token savings from delegated tasks.
"""
import json
import time
from pathlib import Path
from datetime import datetime

class TokenTracker:
    """Track and analyze token usage across orchestrator operations."""
    
    def __init__(self):
        self.log_file = Path("/a0/usr/projects/frugal_orchestrator/logs/tokens.json")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record_operation(self, profile: str, tokens_before: int, tokens_after: int):
        """Record a delegation operation's token metrics."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        saving = tokens_before - tokens_after
        percent_saved = (saving / tokens_before * 100) if tokens_before else 0
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "profile": profile,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_saved": saving,
            "percent_savings": round(percent_saved, 2)
        }
        
        # Append to log
        logs = []
        if self.log_file.exists():
            try:
                logs = json.loads(self.log_file.read_text())
            except:
                logs = []
        
        logs.append(entry)
        self.log_file.write_text(json.dumps(logs, indent=2))
        return entry
    
    def generate_report(self, last_n=5):
        """Generate summary report of recent operations."""
        if not self.log_file.exists():
            return "No token tracking data yet."
        
        logs = json.loads(self.log_file.read_text())
        recent = logs[-last_n:] if len(logs) >= last_n else logs
        
        total_saved = sum(r["tokens_saved"] for r in recent)
        avg_percent = sum(r["percent_savings"] for r in recent) / len(recent) if recent else 0
        
        table = "| Profile | Before | After | Saved | % Savings |\n"
        table += "|---------|--------|-------|-------|-----------|\n"
        for r in recent:
            table += f"| {r['profile']} | {r['tokens_before']:,} | {r['tokens_after']:,} | {r['tokens_saved']:,} | {r['percent_savings']}% |\n"
        
        report = f"## Recent Operations (Last {len(recent)})\n\n{table}\n\n"
        report += f"**Total Saved:** {total_saved:,} tokens\n"
        report += f"**Average Savings:** {avg_percent:.1f}%\n"
        
        return report

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 4:
        profile, before, after = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
        tracker = TokenTracker()
        entry = tracker.record_operation(profile, before, after)
        print(f"✓ Recorded: {entry['tokens_saved']:,} tokens saved ({entry['percent_savings']}%)")
    else:
        tracker = TokenTracker()
        print(tracker.generate_report())
