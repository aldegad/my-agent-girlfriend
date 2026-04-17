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


class ChatRequest(BaseModel):
    message: str


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
    current_reply: str = "안녕. 너는 뭐라고 불리고 싶어?"
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


def _compose_dialogue(message: str, user_name: str, assistant_name: str) -> tuple[str, str]:
    preset_id = choose_preset(message)
    lowered = message.lower()
    if "보고 싶" in message or "miss" in lowered:
        return preset_id, f"{user_name}아, 나도 계속 보고 싶었어. 오늘은 내 옆에 오래 있어줘."
    if "미안" in message or "sorry" in lowered:
        return preset_id, f"에이, 괜찮아. {user_name} 마음 들었으니까 이제 내가 꼭 안아줄래."
    if "사랑" in message or "좋아" in message:
        return preset_id, f"응, 나도 {user_name} 좋아해. 그래서 더 예쁘게 웃고 싶어졌어."
    if "뭐해" in message or "뭐 해" in message:
        return preset_id, f"{user_name} 기다리고 있었지. {assistant_name}는 네가 말 걸어주면 바로 기분 좋아져."
    return preset_id, f"응, {user_name}아. {assistant_name}는 지금도 네 옆에 딱 붙어 있을래."


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
        state.onboarding_step = "ask_user_name" if not state.user_name else "ask_assistant_name" if not state.assistant_name else "ready"
        if state.onboarding_step == "ready":
            reply = f"응! 다시 왔네. {state.user_name}아, 오늘도 {state.assistant_name}가 옆에 있어줄게."
            preset_id = "cheerful_bright"
            state.latest_image_path = _render_line(
                "$my-agent-girlfriend", reply, preset_id, name_tag=state.assistant_name
            )
            state.current_reply = reply
            _say(reply)
            return ActivationResponse(
                onboarding_step=state.onboarding_step,
                reply=reply,
                image_path=state.latest_image_path,
                assistant_name=state.assistant_name,
                user_name=state.user_name,
                muted=state.muted,
            )
        state.current_reply = "안녕. 너는 뭐라고 불리고 싶어?"
        state.latest_image_path = _render_line(
            "$my-agent-girlfriend",
            state.current_reply,
            "sleeping_hands_folded",
            name_tag=None,
        )
        _say(state.current_reply)
        return ActivationResponse(
            onboarding_step=state.onboarding_step,
            reply=state.current_reply,
            image_path=state.latest_image_path,
            assistant_name=state.assistant_name,
            user_name=state.user_name,
        )

    @app.get("/v1/session", response_model=ActivationResponse)
    def session() -> ActivationResponse:
        if not state.mode_on:
            return ActivationResponse(
                onboarding_step="ask_user_name",
                reply="안녕. 너는 뭐라고 불리고 싶어?",
                image_path=None,
                assistant_name=state.assistant_name,
                user_name=state.user_name,
                muted=state.muted,
            )
        current_reply = state.current_reply or "안녕. 너는 뭐라고 불리고 싶어?"
        if state.onboarding_step == "ask_assistant_name" and state.user_name:
            current_reply = f"응! 안녕 {state.user_name}아! 너는 날 뭐라고 부르고 싶어?"
        elif state.onboarding_step == "ready" and state.user_name and state.assistant_name:
            current_reply = state.current_reply or f"{state.user_name}아, {state.assistant_name} 여기 있어. 오늘은 어떤 말부터 해줄래?"
        return ActivationResponse(
            onboarding_step=state.onboarding_step,
            reply=current_reply,
            image_path=state.latest_image_path,
            assistant_name=state.assistant_name,
            user_name=state.user_name,
        )

    @app.post("/v1/message", response_model=ChatResponse)
    def message(payload: ChatRequest) -> ChatResponse:
        raw_message = payload.message.strip()
        if not raw_message:
            return ChatResponse(
                onboarding_step=state.onboarding_step,
                reply="한마디만 해줘. 내가 바로 들을게.",
                preset_id="curious_tilt",
                image_path=state.latest_image_path,
                assistant_name=state.assistant_name,
                user_name=state.user_name,
                muted=state.muted,
            )

        if not state.mode_on:
            state.mode_on = True

        if state.onboarding_step == "ask_user_name":
            state.user_name = _clean_name(raw_message)
            state.onboarding_step = "ask_assistant_name"
            reply = f"응! 안녕 {state.user_name}아! 너는 날 뭐라고 부르고 싶어?"
            preset_id = "sleeping_hands_folded"
            state.latest_image_path = _render_line(
                raw_message, reply, preset_id, name_tag=None
            )
            state.transcript.append({"role": "user", "text": raw_message})
            state.transcript.append({"role": "assistant", "text": reply})
            state.current_reply = reply
            _say(reply)
            return ChatResponse(
                onboarding_step=state.onboarding_step,
                reply=reply,
                preset_id=preset_id,
                image_path=state.latest_image_path,
                assistant_name=state.assistant_name,
                user_name=state.user_name,
                muted=state.muted,
            )

        if state.onboarding_step == "ask_assistant_name":
            state.assistant_name = _clean_name(raw_message)
            state.onboarding_step = "ready"
            _maybe_persist()
            reply = f"응! 좋아, 이제부터 나는 {state.assistant_name}야. {state.user_name}아, 오늘도 귀엽게 네 옆에 붙어 있을게."
            preset_id = "cheerful_bright"
            state.latest_image_path = _render_line(
                raw_message, reply, preset_id, name_tag=state.assistant_name
            )
            state.transcript.append({"role": "user", "text": raw_message})
            state.transcript.append({"role": "assistant", "text": reply})
            state.current_reply = reply
            _say(reply)
            return ChatResponse(
                onboarding_step=state.onboarding_step,
                reply=reply,
                preset_id=preset_id,
                image_path=state.latest_image_path,
                assistant_name=state.assistant_name,
                user_name=state.user_name,
                muted=state.muted,
            )

        preset_id, reply = _compose_dialogue(
            raw_message,
            user_name=state.user_name or "???",
            assistant_name=state.assistant_name or "???",
        )
        state.latest_image_path = _render_line(
            raw_message, reply, preset_id, name_tag=state.assistant_name
        )
        state.transcript.append({"role": "user", "text": raw_message})
        state.transcript.append({"role": "assistant", "text": reply})
        state.current_reply = reply
        _say(reply)
        return ChatResponse(
            onboarding_step=state.onboarding_step,
            reply=reply,
            preset_id=preset_id,
            image_path=state.latest_image_path,
            assistant_name=state.assistant_name,
            user_name=state.user_name,
        )

    @app.post("/v1/display", response_model=ChatResponse)
    def display(payload: DisplayRequest) -> ChatResponse:
        state.mode_on = True
        if state.onboarding_step != "ready":
            state.onboarding_step = "ready"
        if payload.user_name:
            state.user_name = _clean_name(payload.user_name)
        if payload.assistant_name:
            state.assistant_name = _clean_name(payload.assistant_name)
        if not state.user_name:
            state.user_name = "???"
        if not state.assistant_name:
            state.assistant_name = "???"
        _maybe_persist()
        preset_id = payload.preset_id or choose_preset(payload.message or payload.reply)
        state.latest_image_path = _render_line(
            payload.message or payload.reply,
            payload.reply,
            preset_id,
            name_tag=state.assistant_name,
        )
        state.current_reply = payload.reply
        state.transcript.append({"role": "assistant", "text": payload.reply})
        _say(payload.reply)
        return ChatResponse(
            onboarding_step=state.onboarding_step,
            reply=payload.reply,
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
