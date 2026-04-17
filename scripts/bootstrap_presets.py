#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from my_agent_girlfriend.bootstrap import default_output_prompt_pack_path, sync_manifest_images, write_default_manifest, write_prompt_pack
from my_agent_girlfriend.manifest import load_manifest, save_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap the preset pack manifest and prompt pack.")
    parser.add_argument("--manifest", default=str(ROOT / "assets" / "presets" / "manifest.json"))
    parser.add_argument("--base-image", help="Path to the approved or pending base image")
    parser.add_argument("--sync-existing", action="store_true", help="Sync preset PNGs from assets/presets into the manifest")
    parser.add_argument("--output-prompts", default=str(default_output_prompt_pack_path()))
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    base_image = Path(args.base_image).resolve() if args.base_image else None
    write_default_manifest(manifest_path, base_asset=base_image)
    manifest = load_manifest(manifest_path)

    if args.sync_existing:
        manifest = sync_manifest_images(manifest, ROOT / "assets" / "presets")
        save_manifest(manifest, manifest_path)

    prompts_path = write_prompt_pack(Path(args.output_prompts))
    print(f"manifest={manifest_path}")
    print(f"prompts={prompts_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

