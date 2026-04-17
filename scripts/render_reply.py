#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from my_agent_girlfriend.rendering import render_reply


def main() -> int:
    parser = argparse.ArgumentParser(description="Route to a preset and render a girlfriend-mode reply image.")
    parser.add_argument("--message", required=True, help="Incoming user message or mood cue")
    parser.add_argument("--reply", required=True, help="Dialogue to place in the bubble")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--preset", help="Optional preset override")
    parser.add_argument("--manifest", default=str(ROOT / "assets" / "presets" / "manifest.json"))
    args = parser.parse_args()

    result = render_reply(
        message=args.message,
        reply=args.reply,
        out_path=Path(args.out),
        preset_id=args.preset,
        manifest_path=Path(args.manifest),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

