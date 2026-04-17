#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/runtime"
BRIDGE_LOG="$RUNTIME_DIR/bridge.log"
APP_LOG="$RUNTIME_DIR/app.log"

mkdir -p "$RUNTIME_DIR"

cd "$ROOT_DIR"
uv sync >/dev/null

if ! curl -sf http://127.0.0.1:44777/health >/dev/null 2>&1; then
  nohup uv run python scripts/run_bridge.py --host 127.0.0.1 --port 44777 >"$BRIDGE_LOG" 2>&1 &
  sleep 1
fi

if ! pgrep -f "GirlfriendDesktop" >/dev/null 2>&1; then
  cd "$ROOT_DIR/mac-app"
  BIN_PATH="$(swift build --show-bin-path)/GirlfriendDesktop"
  nohup "$BIN_PATH" >"$APP_LOG" 2>&1 &
  sleep 1
fi

osascript -e 'tell application "System Events" to tell process "GirlfriendDesktop" to set frontmost to true' >/dev/null 2>&1 || true

printf 'bridge: http://127.0.0.1:44777\n'
printf 'app: GirlfriendDesktop launched\n'
