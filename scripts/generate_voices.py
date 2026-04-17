#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import struct
import sys
import urllib.request
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets" / "voices"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"
ENV_PATH = Path(os.path.expanduser("~/.claude/.env.gemini"))

MODEL = "gemini-2.5-flash-preview-tts"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
)
DEFAULT_VOICE = "Leda"
SAMPLE_RATE = 24000

CLIPS = [
    {
        "id": "hi",
        "text": "こんにちは！",
        "context": "cheerful greeting, bright and friendly",
    },
    {
        "id": "dekita",
        "text": "できたよ〜！",
        "context": "satisfied completion, soft and warm",
    },
    {
        "id": "otsukare",
        "text": "お疲れさま！",
        "context": "warm appreciation after work",
    },
    {
        "id": "yatta",
        "text": "やったぁ！",
        "context": "delighted celebration, bouncy",
    },
    {
        "id": "tadaima",
        "text": "ただいま〜！",
        "context": "homecoming, cozy and a bit playful",
    },
    {
        "id": "uun",
        "text": "うーん…",
        "context": "thoughtful, slightly puzzled hum",
    },
    {
        "id": "etto",
        "text": "えっと…",
        "context": "soft hesitation while thinking",
    },
    {
        "id": "a",
        "text": "あっ！",
        "context": "small surprised realization",
    },
    {
        "id": "fufu",
        "text": "ふふっ",
        "context": "soft amused giggle",
    },
]


def _load_api_key() -> str:
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    if not ENV_PATH.exists():
        raise SystemExit(f"GEMINI_API_KEY not set and {ENV_PATH} not found")
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            if key.strip() == "GEMINI_API_KEY":
                return value.strip().strip('"').strip("'")
    raise SystemExit("GEMINI_API_KEY not found in env file")


def _request_tts(api_key: str, text: str, context: str, voice: str, attempts: int = 3) -> bytes:
    style_prompt = (
        f"Say in Japanese with a young cheerful anime girl voice "
        f"({context}): {text}"
    )
    payload = {
        "contents": [{"parts": [{"text": style_prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
            },
        },
    }
    data = json.dumps(payload).encode("utf-8")
    last_body: dict | None = None
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            f"{ENDPOINT}?key={api_key}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
        last_body = body
        candidates = body.get("candidates") or []
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            for part in parts:
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and "data" in inline:
                    return base64.b64decode(inline["data"])
        print(f"       attempt {attempt}/{attempts} returned no audio; retrying", file=sys.stderr)
    raise RuntimeError(f"No audio returned after {attempts} attempts: {json.dumps(last_body)[:500]}")


def _write_wav(pcm: bytes, out_path: Path, sample_rate: int = SAMPLE_RATE) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Japanese voice clips via Gemini TTS.")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Gemini prebuilt voice name")
    parser.add_argument("--only", nargs="*", help="Only generate the given clip ids")
    parser.add_argument("--force", action="store_true", help="Re-generate even if file exists")
    args = parser.parse_args()

    api_key = _load_api_key()
    selected = [c for c in CLIPS if not args.only or c["id"] in args.only]

    manifest_entries: list[dict[str, object]] = []
    for clip in selected:
        out_path = ASSETS_DIR / f"{clip['id']}.wav"
        if out_path.exists() and not args.force:
            print(f"[skip] {clip['id']} already exists")
        else:
            print(f"[gen ] {clip['id']} ({clip['text']})")
            pcm = _request_tts(api_key, clip["text"], clip["context"], args.voice)
            _write_wav(pcm, out_path)
            print(f"       wrote {out_path.relative_to(ROOT)} ({len(pcm)} bytes)")
        manifest_entries.append(
            {
                "id": clip["id"],
                "text": clip["text"],
                "context": clip["context"],
                "voice": args.voice,
                "path": f"assets/voices/{clip['id']}.wav",
            }
        )

    if not args.only:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(
            json.dumps({"voice": args.voice, "clips": manifest_entries}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[ok  ] manifest at {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
