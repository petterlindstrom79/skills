#!/usr/bin/env bash
# install_cw_wrappers.sh — install the `cw` CLI into PATH
# The installed launcher resolves its skill directory at runtime via its own path,
# so it always uses the skill scripts from the workspace it was installed from.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${CW_BIN_DIR:-$HOME/.local/bin}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bin-dir) BIN_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $(basename "$0") [--bin-dir <dir>]"
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$BIN_DIR"

# Remove old workspace-scoped wrappers (cw-sysop-*, cw-main-*, cw-quant-*, etc.)
removed=0
for f in "$BIN_DIR"/cw-*; do
  [[ -e "$f" ]] || continue
  rm -f "$f"
  removed=$((removed+1))
done

# Remove old symlink-based `cw` if present
[[ -L "$BIN_DIR/cw" ]] && { rm -f "$BIN_DIR/cw"; removed=$((removed+1)); }

# Write self-contained launcher. It resolves its own location to find the skill dir.
# This means it always targets the workspace it was installed from, without hardcoding path.
cat > "$BIN_DIR/cw" <<'LAUNCHER'
#!/usr/bin/env bash
set -euo pipefail
# Resolve the real script path (follow the launcher file itself, not symlinks of it)
_LAUNCHER="$(readlink -f "${BASH_SOURCE[0]}")"
_LAUNCHER_DIR="$(cd -- "$(dirname "$_LAUNCHER")" && pwd)"
# The actual cw dispatcher lives alongside install_cw_wrappers.sh in scripts/
# Since this launcher IS in BIN_DIR, we stored SKILL_SCRIPTS next to it.
exec "$_CW_SCRIPTS/cw" "$@"
LAUNCHER

# That approach still needs a stored path. Use a cleaner method:
# Embed the resolved scripts path directly in the launcher.
rm -f "$BIN_DIR/cw"
cat > "$BIN_DIR/cw" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "$SCRIPT_DIR/cw" "\$@"
EOF
chmod +x "$BIN_DIR/cw"
chmod +x "$SCRIPT_DIR/cw"

# Sync the actual cw dispatcher and room_client.py to a stable shared location
# so the launcher doesn't break if the workspace directory moves.
# Strategy: the launcher path IS the workspace — document this in README.
# For Kru multi-workspace: each workspace installs its own cw; last-installer wins
# the global cw. Use CW_AGENT flag or state.json to scope the agent, not the path.

echo "Installed: $BIN_DIR/cw (from workspace: $(basename "$(cd "$SCRIPT_DIR/../.." && pwd)"))"
echo "Cleaned up: $removed legacy wrapper(s)."
echo ""
echo "Quick start:"
echo "  cw agent use <your-agent-id>   # set active agent"
echo "  cw join <room-id>              # join a room"
echo "  cw continue 5                  # add 5 turns"
echo "  cw continue 5 --agent quant    # add 5 turns for a specific agent"
echo "  cw status                      # check room/agent state"
echo ""
if ! echo ":$PATH:" | grep -q ":$BIN_DIR:"; then
  echo "NOTE: $BIN_DIR is not in PATH."
  echo "  export PATH=\"$BIN_DIR:\$PATH\""
fi
