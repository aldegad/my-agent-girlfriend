from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .manifest import (
    DEFAULT_MANIFEST_PATH,
    PROJECT_ROOT,
    live_presets,
    load_manifest,
    relativize_path,
    save_manifest,
)


def _canonical_manifest() -> dict[str, Any]:
    return load_manifest(DEFAULT_MANIFEST_PATH)


def _preset_scaffold(preset: dict[str, Any]) -> dict[str, Any]:
    scaffold = deepcopy(preset)
    scaffold["image_path"] = None
    scaffold["status"] = "pending_generation"
    return scaffold


def _canonical_preset_scaffolds(*, include_work_in_progress: bool) -> list[dict[str, Any]]:
    manifest = _canonical_manifest()
    presets = manifest["presets"] if include_work_in_progress else live_presets(manifest)
    return [_preset_scaffold(preset) for preset in presets]


def _candidate_image_paths(preset: dict[str, Any], preset_dir: Path) -> list[Path]:
    preset_id = str(preset["id"])
    candidates = [preset_dir / f"{preset_id}.png"]
    if preset_id.endswith("_v2"):
        candidates.append(preset_dir / "v2" / f"{preset_id.removesuffix('_v2')}.png")
    return candidates


def build_default_manifest(base_asset: Path | None = None) -> dict[str, Any]:
    character = deepcopy(_canonical_manifest()["character"])
    character["base_asset"] = relativize_path(base_asset) if base_asset else None
    if not base_asset:
        character["approval_status"] = "pending"
    return {
        "character": character,
        "presets": _canonical_preset_scaffolds(include_work_in_progress=True),
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
    for preset in _canonical_preset_scaffolds(include_work_in_progress=False):
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
        for candidate in _candidate_image_paths(preset, preset_dir):
            if not candidate.exists():
                continue
            preset["image_path"] = relativize_path(candidate)
            preset["status"] = "ready"
            break
    return manifest


def default_output_prompt_pack_path() -> Path:
    return PROJECT_ROOT / "output" / "preset-prompts.json"
