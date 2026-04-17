from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from .rendering import render_reply
from .routing import choose_preset


def _say(reply: str) -> None:
    print(f"\n💬 {reply}\n", flush=True, file=sys.stdout)

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_OUTPUT_DIR = ROOT_DIR / "output" / "app"
SESSION_FILE = ROOT_DIR / "output" / "session.json"

OVERLAY_MAX_CHARS = 60


def _truncate_for_overlay(text: str, limit: int = OVERLAY_MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _load_persisted_names() -> tuple[str | None, str | None]:
    if not SESSION_FILE.exists():
        return None, None
    try:
        data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, None
    return data.get("user_name"), data.get("assistant_name")


def _persist_names(user_name: str | None, assistant_name: str | None) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"user_name": user_name, "assistant_name": assistant_name}
    SESSION_FILE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class DisplayRequest(BaseModel):
    message: str = ""
    reply: str
    preset_id: str | None = None
    user_name: str | None = None
    assistant_name: str | None = None


class ActivationResponse(BaseModel):
    onboarding_step: str
    reply: str
    image_path: str | None
    assistant_name: str | None
    user_name: str | None
    muted: bool = False


class ChatResponse(BaseModel):
    onboarding_step: str
    reply: str
    preset_id: str | None
    image_path: str | None
    assistant_name: str | None
    user_name: str | None
    muted: bool = False


class MuteRequest(BaseModel):
    muted: bool


@dataclass
class SessionState:
    mode_on: bool = False
    onboarding_step: Literal["ask_user_name", "ask_assistant_name", "ready"] = "ask_user_name"
    user_name: str | None = None
    assistant_name: str | None = None
    latest_image_path: str | None = None
    current_reply: str = ""
    transcript: list[dict[str, str]] = field(default_factory=list)
    muted: bool = False


def _clean_name(value: str) -> str:
    return value.strip().strip("\"'")[:40] or "???"


def _render_line(
    message: str,
    reply: str,
    preset_id: str | None = None,
    name_tag: str | None = None,
) -> str:
    APP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("reply-%Y%m%d-%H%M%S-%f.png")
    out_path = APP_OUTPUT_DIR / filename
    result = render_reply(
        message=message,
        reply=reply,
        out_path=out_path,
        preset_id=preset_id,
        name_tag=name_tag,
    )
    return result["out_path"]


def create_app() -> FastAPI:
    app = FastAPI(title="My Agent Girlfriend Bridge")
    state = SessionState()
    persisted_user, persisted_assistant = _load_persisted_names()
    if persisted_user and persisted_user != "???":
        state.user_name = persisted_user
    if persisted_assistant and persisted_assistant != "???":
        state.assistant_name = persisted_assistant
    if state.user_name and state.assistant_name:
        state.onboarding_step = "ready"

    def _maybe_persist() -> None:
        if (
            state.user_name and state.user_name != "???"
            and state.assistant_name and state.assistant_name != "???"
        ):
            _persist_names(state.user_name, state.assistant_name)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/activate", response_model=ActivationResponse)
    def activate() -> ActivationResponse:
        state.mode_on = True
        if state.user_name and state.assistant_name:
            state.onboarding_step = "ready"
        elif state.user_name:
            state.onboarding_step = "ask_assistant_name"
        else:
            state.onboarding_step = "ask_user_name"
        return ActivationResponse(
            onboarding_step=state.onboarding_step,
            reply=state.current_reply,
            image_path=state.latest_image_path,
            assistant_name=state.assistant_name,
            user_name=state.user_name,
            muted=state.muted,
        )

    @app.get("/v1/session", response_model=ActivationResponse)
    def session() -> ActivationResponse:
        return ActivationResponse(
            onboarding_step=state.onboarding_step,
            reply=state.current_reply,
            image_path=state.latest_image_path,
            assistant_name=state.assistant_name,
            user_name=state.user_name,
            muted=state.muted,
        )

    @app.post("/v1/display", response_model=ChatResponse)
    def display(payload: DisplayRequest) -> ChatResponse:
        state.mode_on = True
        if payload.user_name:
            state.user_name = _clean_name(payload.user_name)
        if payload.assistant_name:
            state.assistant_name = _clean_name(payload.assistant_name)
        if state.user_name and state.assistant_name:
            state.onboarding_step = "ready"
        elif state.user_name:
            state.onboarding_step = "ask_assistant_name"
        else:
            state.onboarding_step = "ask_user_name"
        _maybe_persist()
        preset_id = payload.preset_id or choose_preset(payload.message or payload.reply)
        overlay_reply = _truncate_for_overlay(payload.reply)
        state.latest_image_path = _render_line(
            payload.message or overlay_reply,
            overlay_reply,
            preset_id,
            name_tag=state.assistant_name,
        )
        state.current_reply = overlay_reply
        state.transcript.append({"role": "assistant", "text": overlay_reply})
        _say(overlay_reply)
        return ChatResponse(
            onboarding_step=state.onboarding_step,
            reply=overlay_reply,
            preset_id=preset_id,
            image_path=state.latest_image_path,
            assistant_name=state.assistant_name,
            user_name=state.user_name,
        )

    @app.post("/v1/mute")
    def set_mute(payload: MuteRequest) -> dict[str, bool]:
        state.muted = payload.muted
        return {"muted": state.muted}

    return app
