from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "assets" / "presets" / "manifest.json"
DEFAULT_FONT_PATH = Path("/System/Library/Fonts/AppleSDGothicNeo.ttc")
LIVE_PRESET_USAGE = "live"
WORK_IN_PROGRESS_PRESET_USAGE = "work_in_progress"


def load_manifest(manifest_path: Path | None = None) -> dict[str, Any]:
    path = Path(manifest_path or DEFAULT_MANIFEST_PATH)
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, Any], manifest_path: Path | None = None) -> Path:
    path = Path(manifest_path or DEFAULT_MANIFEST_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def resolve_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def relativize_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def get_preset(manifest: dict[str, Any], preset_id: str) -> dict[str, Any]:
    for preset in manifest["presets"]:
        if preset["id"] == preset_id:
            return preset
    raise KeyError(f"Unknown preset id: {preset_id}")


def is_live_preset(preset: dict[str, Any]) -> bool:
    return preset.get("usage", LIVE_PRESET_USAGE) == LIVE_PRESET_USAGE


def live_presets(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [preset for preset in manifest["presets"] if is_live_preset(preset)]


def get_base_asset(manifest: dict[str, Any]) -> Path | None:
    return resolve_path(manifest.get("character", {}).get("base_asset"))
