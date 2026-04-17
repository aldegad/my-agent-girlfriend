from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from .bubble import (
    DialogueBoxLayout,
    compose_dialogue_box,
    make_placeholder_base,
)
from .manifest import get_base_asset, get_preset, load_manifest, resolve_path
from .routing import choose_preset


SIDE_PADDING_RATIO = 0.045
BOTTOM_PADDING_RATIO = 0.045
BOX_HEIGHT_RATIO = 0.28


def _bottom_box_layout(canvas_size: tuple[int, int], name_tag: str | None) -> DialogueBoxLayout:
    width, height = canvas_size
    side_pad = int(round(width * SIDE_PADDING_RATIO))
    bottom_pad = int(round(height * BOTTOM_PADDING_RATIO))
    box_height = int(round(height * BOX_HEIGHT_RATIO))

    x1 = side_pad
    x2 = width - side_pad
    y2 = height - bottom_pad
    y1 = y2 - box_height

    max_font = max(38, int(round(box_height * 0.17)))
    min_font = max(24, int(round(box_height * 0.11)))

    return DialogueBoxLayout(
        box_rect=(x1, y1, x2, y2),
        font_size_range=(min_font, max_font),
        name_tag=name_tag,
    )


def render_reply(
    message: str,
    reply: str,
    out_path: Path,
    preset_id: str | None = None,
    manifest_path: Path | None = None,
    name_tag: str | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    selected_preset = preset_id or choose_preset(message)
    preset = get_preset(manifest, selected_preset)

    preset_path = resolve_path(preset.get("image_path"))
    base_path = get_base_asset(manifest)

    used_fallback_base = False
    if preset_path and preset_path.exists():
        source_image = Image.open(preset_path).convert("RGBA")
    elif base_path and base_path.exists():
        source_image = Image.open(base_path).convert("RGBA")
        used_fallback_base = True
    else:
        source_image = make_placeholder_base()
        used_fallback_base = True

    layout = _bottom_box_layout(source_image.size, name_tag=name_tag)
    composed = compose_dialogue_box(source_image, reply, layout)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    composed.save(out_path)

    return {
        "preset_id": selected_preset,
        "out_path": str(out_path),
        "used_fallback_base": used_fallback_base,
    }
