#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "voices" / "manifest.json"
BRIDGE_SESSION_URL = "http://127.0.0.1:44777/v1/session"


def _is_muted() -> bool:
    try:
        with urllib.request.urlopen(BRIDGE_SESSION_URL, timeout=1.5) as response:
            data = json.loads(response.read().decode("utf-8"))
        return bool(data.get("muted", False))
    except Exception:
        return False


def _load_clips() -> dict[str, Path]:
    if not MANIFEST_PATH.exists():
        return {}
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {clip["id"]: ROOT / clip["path"] for clip in data.get("clips", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description="Play a voice clip via afplay.")
    parser.add_argument("--clip", required=True, help="Clip id from voices/manifest.json")
    parser.add_argument("--volume", type=float, default=1.0, help="0.0–1.0")
    parser.add_argument("--background", action="store_true", help="Don't wait for playback")
    parser.add_argument("--ignore-mute", action="store_true", help="Play even if the bridge is muted")
    args = parser.parse_args()

    if not args.ignore_mute and _is_muted():
        print("[muted] skipping playback")
        return 0

    clips = _load_clips()
    if args.clip not in clips:
        print(f"unknown clip '{args.clip}'. available: {', '.join(sorted(clips)) or '(none)'}", file=sys.stderr)
        return 1
    path = clips[args.clip]
    if not path.exists():
        print(f"clip file missing: {path}", file=sys.stderr)
        return 1

    cmd = ["afplay", "-v", f"{max(0.0, min(args.volume, 1.0))}", str(path)]
    if args.background:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
