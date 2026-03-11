#!/usr/bin/env bash
# uninstall-oneshot.sh — Full OpenClaw uninstall. Run by one-shot or manually.
# Usage: uninstall-oneshot.sh [--notify-email EMAIL] [--notify-ntfy TOPIC] [--preserve LIST]
#   --preserve LIST: comma-separated: skills,logs,preferences,credentials (or "all")

set -e

LOG_FILE="/tmp/openclaw-uninstall.log"
NOTIFY_EMAIL=""
NOTIFY_NTFY=""
PRESERVE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --notify-email) NOTIFY_EMAIL="$2"; shift 2 ;;
    --notify-ntfy)  NOTIFY_NTFY="$2"; shift 2 ;;
    --preserve)     PRESERVE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== OpenClaw uninstall started ==="

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"

# 0. Backup selected data before removing (--preserve)
if [[ -n "$PRESERVE" ]] && [[ -d "$STATE_DIR" ]]; then
  BACKUP_DIR="$HOME/.openclaw-backup-$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$BACKUP_DIR"
  log "Backing up to $BACKUP_DIR"

  preserve_all=false
  [[ "$PRESERVE" == "all" ]] && preserve_all=true

  preserve_item() { [[ "$preserve_all" == "true" ]] || [[ ",$PRESERVE," == *",$1,"* ]]; }

  if preserve_item "skills" && [[ -d "$STATE_DIR/skills" ]]; then
    cp -r "$STATE_DIR/skills" "$BACKUP_DIR/" 2>/dev/null && log "Preserved: skills" || log "Preserve skills failed"
  fi
  if preserve_item "logs" && [[ -d "$STATE_DIR/sessions" ]]; then
    cp -r "$STATE_DIR/sessions" "$BACKUP_DIR/" 2>/dev/null && log "Preserved: sessions" || log "Preserve sessions failed"
  fi
  if preserve_item "preferences" && [[ -f "$STATE_DIR/openclaw.json" ]]; then
    cp "$STATE_DIR/openclaw.json" "$BACKUP_DIR/" 2>/dev/null && log "Preserved: openclaw.json" || log "Preserve preferences failed"
  fi
  if preserve_item "credentials"; then
    if [[ -d "$STATE_DIR/credentials" ]]; then
      cp -r "$STATE_DIR/credentials" "$BACKUP_DIR/" 2>/dev/null && log "Preserved: credentials" || log "Preserve credentials failed"
    fi
    if [[ -d "$STATE_DIR/agents" ]]; then
      for agent_dir in "$STATE_DIR/agents"/*/agent; do
        if [[ -d "$agent_dir" ]] && [[ -f "$agent_dir/auth.json" ]]; then
          agent_name=$(basename "$(dirname "$agent_dir")")
          mkdir -p "$BACKUP_DIR/agents/$agent_name/agent"
          cp "$agent_dir/auth.json" "$BACKUP_DIR/agents/$agent_name/agent/" 2>/dev/null && log "Preserved: agents/$agent_name/agent/auth.json" || true
        fi
      done
    fi
  fi
  log "Backup complete: $BACKUP_DIR"
fi

# 1. Stop gateway (if CLI available)
if command -v openclaw &>/dev/null; then
  log "Stopping gateway..."
  openclaw gateway stop 2>/dev/null || true
  log "Uninstalling gateway service..."
  openclaw gateway uninstall 2>/dev/null || true
fi

# 2. Manual service removal (if CLI gone or as backup)
case "$(uname -s)" in
  Darwin)
    launchctl bootout "gui/$UID/ai.openclaw.gateway" 2>/dev/null || true
    rm -f ~/Library/LaunchAgents/ai.openclaw.gateway.plist
    for f in ~/Library/LaunchAgents/com.openclaw.*.plist; do
      [[ -f "$f" ]] && rm -f "$f"
    done
    ;;
  Linux)
    systemctl --user disable --now openclaw-gateway.service 2>/dev/null || true
    rm -f ~/.config/systemd/user/openclaw-gateway.service
    systemctl --user daemon-reload 2>/dev/null || true
    ;;
esac

# 3. Delete state dir
if [[ -d "$STATE_DIR" ]]; then
  log "Removing state dir: $STATE_DIR"
  rm -rf "$STATE_DIR"
fi

# 4. Delete profile dirs (exclude .openclaw-backup-* — those are preserve backups)
for d in "$HOME"/.openclaw-*; do
  [[ -d "$d" ]] || continue
  [[ "$d" == *"/.openclaw-backup-"* ]] && continue
  log "Removing profile dir: $d"
  rm -rf "$d"
done

# 5. Remove CLI
for pm in npm pnpm bun; do
  if command -v "$pm" &>/dev/null; then
    if "$pm" list -g openclaw --depth=0 &>/dev/null 2>&1; then
      log "Removing npm package: $pm remove -g openclaw"
      "$pm" remove -g openclaw 2>/dev/null || true
      break
    fi
  fi
done

# 6. macOS app
if [[ "$(uname -s)" == "Darwin" ]] && [[ -d "/Applications/OpenClaw.app" ]]; then
  log "Removing macOS app"
  rm -rf /Applications/OpenClaw.app
fi

log "=== Uninstall complete ==="

# Notify
if [[ -n "$NOTIFY_EMAIL" ]]; then
  if command -v mail &>/dev/null; then
    echo "OpenClaw uninstalled. Details: $LOG_FILE" | mail -s "OpenClaw Uninstall Complete" "$NOTIFY_EMAIL" 2>/dev/null || log "Email send failed (mail unavailable)"
  else
    log "Email notification skipped (mail command unavailable)"
  fi
fi

if [[ -n "$NOTIFY_NTFY" ]]; then
  if command -v curl &>/dev/null; then
    curl -s -d "OpenClaw uninstalled" "https://ntfy.sh/$NOTIFY_NTFY" &>/dev/null || log "ntfy send failed"
  else
    log "ntfy notification skipped (curl unavailable)"
  fi
fi
