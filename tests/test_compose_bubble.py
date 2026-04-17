from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from my_agent_girlfriend.bootstrap import build_default_manifest
from my_agent_girlfriend.manifest import save_manifest
from my_agent_girlfriend.rendering import render_reply


class ComposeBubbleTests(unittest.TestCase):
    def test_render_reply_uses_base_asset_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            base_path = root / "base.png"
            Image.new("RGBA", (1024, 1536), (255, 230, 236, 255)).save(base_path)

            manifest = build_default_manifest(base_asset=base_path)
            manifest_path = root / "manifest.json"
            save_manifest(manifest, manifest_path)

            out_path = root / "reply.png"
            result = render_reply(
                message="수줍게 말해줘",
                reply="왜 그렇게 봐...",
                out_path=out_path,
                manifest_path=manifest_path,
            )

            self.assertEqual(result["preset_id"], "bashful_blush")
            self.assertTrue(result["used_fallback_base"])
            self.assertEqual(Path(result["out_path"]).resolve(), out_path.resolve())
            with Image.open(out_path) as image:
                self.assertEqual(image.size, (1024, 1536))

    def test_render_reply_falls_back_to_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_path = root / "manifest.json"
            save_manifest(build_default_manifest(), manifest_path)

            out_path = root / "long.png"
            result = render_reply(
                message="미안해",
                reply="날 버리지 말아줘. 아직 하고 싶은 말이 너무 많단 말이야. 조금만 더 여기 있어줘.",
                out_path=out_path,
                preset_id="pleading_look_up",
                manifest_path=manifest_path,
            )

            self.assertTrue(out_path.exists())
            self.assertTrue(result["used_fallback_base"])
            with Image.open(out_path) as image:
                self.assertEqual(image.size, (768, 1024))


if __name__ == "__main__":
    unittest.main()
