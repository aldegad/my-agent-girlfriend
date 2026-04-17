from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .manifest import PROJECT_ROOT, relativize_path, save_manifest

PRESET_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "neutral_smile",
        "emotion_tags": ["neutral", "smile", "calm", "warm"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [54, 48, 710, 332],
        "tail_anchor": [506, 374],
        "font_size_range": [34, 54],
        "notes": "Default everyday preset.",
    },
    {
        "id": "cheerful_bright",
        "emotion_tags": ["happy", "bright", "cheerful", "excited"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [42, 42, 720, 318],
        "tail_anchor": [522, 360],
        "font_size_range": [34, 54],
        "notes": "Wider bubble for energetic lines.",
    },
    {
        "id": "bashful_blush",
        "emotion_tags": ["bashful", "shy", "blush", "embarrassed"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [48, 44, 700, 322],
        "tail_anchor": [470, 372],
        "font_size_range": [34, 54],
        "notes": "Shy response preset.",
    },
    {
        "id": "playful_tease",
        "emotion_tags": ["tease", "playful", "mischief", "grin"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [40, 42, 726, 316],
        "tail_anchor": [536, 350],
        "font_size_range": [34, 54],
        "notes": "Mischievous and lightly teasing.",
    },
    {
        "id": "curious_tilt",
        "emotion_tags": ["curious", "wondering", "question", "tilt"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [56, 48, 710, 332],
        "tail_anchor": [450, 370],
        "font_size_range": [34, 54],
        "notes": "Questioning head tilt preset.",
    },
    {
        "id": "surprised_wide",
        "emotion_tags": ["surprised", "shock", "wide", "startled"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [38, 40, 726, 314],
        "tail_anchor": [500, 356],
        "font_size_range": [34, 54],
        "notes": "Startled reaction preset.",
    },
    {
        "id": "pouty",
        "emotion_tags": ["pouty", "sulky", "jealous", "upset"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [52, 46, 706, 326],
        "tail_anchor": [468, 380],
        "font_size_range": [34, 54],
        "notes": "Puffed-cheek pout or mild jealousy.",
    },
    {
        "id": "worried",
        "emotion_tags": ["worried", "anxious", "concerned", "careful"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [56, 46, 702, 330],
        "tail_anchor": [480, 382],
        "font_size_range": [34, 54],
        "notes": "Concerned or uneasy preset.",
    },
    {
        "id": "teary",
        "emotion_tags": ["teary", "sad", "holding_back_tears", "hurt"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [50, 42, 706, 324],
        "tail_anchor": [484, 376],
        "font_size_range": [34, 52],
        "notes": "Watery eyes, not fully crying.",
    },
    {
        "id": "crying_closed_eyes",
        "emotion_tags": ["crying", "sobbing", "closed_eyes", "sad"],
        "framing": "upper_body",
        "camera": "eye_level",
        "bubble_rect": [48, 36, 712, 310],
        "tail_anchor": [498, 358],
        "font_size_range": [32, 50],
        "notes": "Open crying preset.",
    },
    {
        "id": "pleading_look_up",
        "emotion_tags": ["pleading", "look_up", "please", "don't_leave"],
        "framing": "half_body",
        "camera": "slight_high_angle",
        "bubble_rect": [54, 34, 706, 290],
        "tail_anchor": [396, 418],
        "font_size_range": [32, 50],
        "notes": "Viewer looks slightly down while character looks up.",
    },
    {
        "id": "apology_look_up",
        "emotion_tags": ["apology", "sorry", "look_up", "remorse"],
        "framing": "half_body",
        "camera": "slight_high_angle",
        "bubble_rect": [52, 34, 704, 288],
        "tail_anchor": [404, 424],
        "font_size_range": [32, 50],
        "notes": "Apologetic upward-looking preset.",
    },
]


def build_default_manifest(base_asset: Path | None = None) -> dict[str, Any]:
    return {
        "character": {
            "version": "v1",
            "approval_status": "pending",
            "base_asset": relativize_path(base_asset) if base_asset else None,
            "style": {
                "hair": "long red hair",
                "outfit": "plain white short-sleeve shirt",
                "medium": "2D anime illustration",
                "framing": "upper_body",
                "tone": "wholesome",
            },
        },
        "presets": [
            {
                **preset,
                "image_path": None,
                "status": "pending_generation",
            }
            for preset in PRESET_DEFINITIONS
        ],
    }


def write_default_manifest(manifest_path: Path, base_asset: Path | None = None) -> Path:
    manifest = build_default_manifest(base_asset=base_asset)
    return save_manifest(manifest, manifest_path)


def build_prompt_pack() -> list[dict[str, Any]]:
    base_prompt = (
        "Same fixed character identity, long red hair, plain white short-sleeve shirt, "
        "wholesome non-sexualized 2D anime illustration, clean unobtrusive background, "
        "no speech bubble, no text, no watermark."
    )
    prompts: list[dict[str, Any]] = []
    for preset in PRESET_DEFINITIONS:
        prompts.append(
            {
                "id": preset["id"],
                "prompt": (
                    f"{base_prompt} Framing: {preset['framing']}. Camera: {preset['camera']}. "
                    f"Emotion tags: {', '.join(preset['emotion_tags'])}. Notes: {preset['notes']}"
                ),
            }
        )
    return prompts


def write_prompt_pack(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"base_style": build_default_manifest()["character"]["style"], "presets": build_prompt_pack()}
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def sync_manifest_images(manifest: dict[str, Any], preset_dir: Path) -> dict[str, Any]:
    preset_dir = preset_dir.resolve()
    for preset in manifest["presets"]:
        candidate = preset_dir / f"{preset['id']}.png"
        if candidate.exists():
            preset["image_path"] = relativize_path(candidate)
            preset["status"] = "ready"
    return manifest


def default_output_prompt_pack_path() -> Path:
    return PROJECT_ROOT / "output" / "preset-prompts.json"

