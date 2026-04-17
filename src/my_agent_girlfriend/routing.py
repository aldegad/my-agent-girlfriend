from __future__ import annotations

from collections.abc import Iterable

KEYWORD_WEIGHTS: dict[str, dict[str, int]] = {
    "bashful_blush": {
        "수줍": 4,
        "부끄": 4,
        "부끄러": 4,
        "쑥스": 4,
        "blush": 4,
        "shy": 4,
    },
    "playful_tease": {
        "장난": 4,
        "놀려": 4,
        "약올": 4,
        "tease": 4,
        "playful": 3,
    },
    "curious_tilt": {
        "왜": 2,
        "어째서": 4,
        "궁금": 4,
        "question": 3,
        "curious": 4,
    },
    "surprised_wide": {
        "깜짝": 4,
        "헉": 4,
        "놀라": 4,
        "surprise": 4,
        "shock": 4,
    },
    "pouty": {
        "삐": 4,
        "흥": 4,
        "토라": 4,
        "질투": 3,
        "jealous": 3,
        "pout": 4,
    },
    "worried": {
        "걱정": 4,
        "불안": 4,
        "괜찮": 2,
        "worried": 4,
        "anxious": 4,
    },
    "teary": {
        "울것": 4,
        "울 것": 4,
        "눈물": 4,
        "teary": 4,
        "sad": 2,
    },
    "crying_closed_eyes": {
        "엉엉": 4,
        "울어": 4,
        "울면서": 4,
        "crying": 4,
        "sob": 4,
    },
    "pleading_look_up": {
        "버리지": 5,
        "가지마": 5,
        "제발": 5,
        "부탁": 4,
        "날 떠나": 5,
        "don't leave": 5,
    },
    "apology_look_up": {
        "미안": 5,
        "잘못": 4,
        "사과": 4,
        "sorry": 5,
        "forgive": 3,
    },
    "cheerful_bright": {
        "좋아": 3,
        "신나": 4,
        "기뻐": 4,
        "happy": 4,
        "yay": 4,
    },
    "neutral_smile": {
        "안녕": 2,
        "hello": 2,
        "hi": 2,
    },
}

DEFAULT_PRESET = "neutral_smile"


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def choose_preset(message: str, extra_keywords: Iterable[str] | None = None) -> str:
    text = _normalize(message)
    scores = {preset_id: 0 for preset_id in KEYWORD_WEIGHTS}
    for preset_id, keywords in KEYWORD_WEIGHTS.items():
        for keyword, weight in keywords.items():
            if keyword in text:
                scores[preset_id] += weight
    if extra_keywords:
        for keyword in extra_keywords:
            normalized = _normalize(keyword)
            for preset_id, keywords in KEYWORD_WEIGHTS.items():
                for known, weight in keywords.items():
                    if known in normalized:
                        scores[preset_id] += weight
    best_preset = max(scores, key=scores.get)
    if scores[best_preset] == 0:
        return DEFAULT_PRESET
    return best_preset

