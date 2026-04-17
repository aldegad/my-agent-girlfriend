from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from .bubble import compose_dialogue_image, layout_from_manifest, make_placeholder_base, scale_layout
from .manifest import get_base_asset, get_preset, load_manifest, resolve_path
from .routing import choose_preset


def _resolve_base_image(manifest: dict[str, Any], preset: dict[str, Any]) -> Image.Image:
    preset_path = resolve_path(preset.get("image_path"))
    if preset_path and preset_path.exists():
        return Image.open(preset_path).convert("RGBA")
    base_path = get_base_asset(manifest)
    if base_path and base_path.exists():
        return Image.open(base_path).convert("RGBA")
    return make_placeholder_base()


def render_reply(
    message: str,
    reply: str,
    out_path: Path,
    preset_id: str | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    selected_preset = preset_id or choose_preset(message)
    preset = get_preset(manifest, selected_preset)
    preset_path = resolve_path(preset.get("image_path"))
    using_preset_image = bool(preset_path and preset_path.exists())
    base_image = _resolve_base_image(manifest, preset)
    layout = scale_layout(layout_from_manifest(preset), base_image.size)
    composed = compose_dialogue_image(base_image, reply, layout)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    composed.save(out_path)
    return {
        "preset_id": selected_preset,
        "out_path": str(out_path),
        "used_fallback_base": not using_preset_image,
    }
