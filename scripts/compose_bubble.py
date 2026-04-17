#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from my_agent_girlfriend.rendering import render_reply


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose a speech-bubble dialogue image from a preset.")
    parser.add_argument("--preset", required=True, help="Preset id from assets/presets/manifest.json")
    parser.add_argument("--text", required=True, help="Dialogue text to render in the speech bubble")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--manifest", default=str(ROOT / "assets" / "presets" / "manifest.json"))
    args = parser.parse_args()

    result = render_reply(
        message=args.text,
        reply=args.text,
        out_path=Path(args.out),
        preset_id=args.preset,
        manifest_path=Path(args.manifest),
    )
    print(result["out_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

