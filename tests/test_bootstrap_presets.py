from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from my_agent_girlfriend.bootstrap import sync_manifest_images, write_default_manifest, write_prompt_pack
from my_agent_girlfriend.manifest import DEFAULT_MANIFEST_PATH, live_presets, load_manifest


class BootstrapPresetTests(unittest.TestCase):
    def test_bootstrap_writes_manifest_and_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_path = root / "manifest.json"
            prompt_path = root / "preset-prompts.json"

            write_default_manifest(manifest_path)
            write_prompt_pack(prompt_path)

            canonical_manifest = load_manifest()
            manifest = load_manifest(manifest_path)
            prompt_pack = json.loads(prompt_path.read_text(encoding="utf-8"))

            self.assertEqual(
                [preset["id"] for preset in manifest["presets"]],
                [preset["id"] for preset in canonical_manifest["presets"]],
            )
            self.assertEqual(
                [preset["id"] for preset in prompt_pack["presets"]],
                [preset["id"] for preset in live_presets(canonical_manifest)],
            )

    def test_live_preset_assets_match_manifest(self) -> None:
        manifest = load_manifest()
        live_ids = {preset["id"] for preset in live_presets(manifest)}
        root_asset_ids = {path.stem for path in DEFAULT_MANIFEST_PATH.parent.glob("*.png")}

        self.assertSetEqual(root_asset_ids, live_ids)

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

    def test_sync_manifest_images_marks_v2_assets_from_variant_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_path = root / "manifest.json"
            write_default_manifest(manifest_path)
            manifest = load_manifest(manifest_path)

            preset_dir = root / "assets" / "presets"
            v2_dir = preset_dir / "v2"
            v2_dir.mkdir(parents=True)
            Image.new("RGBA", (768, 1024), (255, 255, 255, 255)).save(v2_dir / "pleading_look_up.png")

            synced = sync_manifest_images(manifest, preset_dir)
            pleading_v2 = next(preset for preset in synced["presets"] if preset["id"] == "pleading_look_up_v2")
            self.assertEqual(pleading_v2["status"], "ready")
            self.assertEqual(
                pleading_v2["image_path"],
                str((v2_dir / "pleading_look_up.png").resolve()),
            )


if __name__ == "__main__":
    unittest.main()
