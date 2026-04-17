from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from my_agent_girlfriend.bootstrap import sync_manifest_images, write_default_manifest, write_prompt_pack
from my_agent_girlfriend.manifest import load_manifest


class BootstrapPresetTests(unittest.TestCase):
    def test_bootstrap_writes_manifest_and_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_path = root / "manifest.json"
            prompt_path = root / "preset-prompts.json"

            write_default_manifest(manifest_path)
            write_prompt_pack(prompt_path)

            manifest = load_manifest(manifest_path)
            prompt_pack = json.loads(prompt_path.read_text(encoding="utf-8"))

            self.assertEqual(len(manifest["presets"]), 12)
            self.assertEqual(len(prompt_pack["presets"]), 12)

    def test_sync_manifest_images_marks_ready_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_path = root / "manifest.json"
            write_default_manifest(manifest_path)
            manifest = load_manifest(manifest_path)

            preset_dir = root / "assets" / "presets"
            preset_dir.mkdir(parents=True)
            Image.new("RGBA", (768, 1024), (255, 255, 255, 255)).save(preset_dir / "neutral_smile.png")

            synced = sync_manifest_images(manifest, preset_dir)
            neutral = next(preset for preset in synced["presets"] if preset["id"] == "neutral_smile")
            self.assertEqual(neutral["status"], "ready")
            self.assertTrue(neutral["image_path"])


if __name__ == "__main__":
    unittest.main()
