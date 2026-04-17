from __future__ import annotations

from collections.abc import Iterable

KEYWORD_WEIGHTS: dict[str, dict[str, int]] = {
    "apology_look_up": {
        "미안": 5,
        "잘못": 4,
        "사과": 4,
        "sorry": 5,
        "forgive": 3,
    },
    "pleading_look_up": {
        "버리지": 5,
        "가지마": 5,
        "제발": 5,
        "부탁": 4,
        "날 떠나": 5,
        "don't leave": 5,
        "잘가": 4,
        "잘 가": 4,
        "갈게": 4,
        "나갈게": 4,
        "가야": 4,
        "자야": 4,
        "잘자": 4,
        "잘 자": 4,
        "안녕히": 4,
        "bye": 4,
        "see you": 4,
        "goodnight": 4,
        "good night": 4,
    },
    "worried": {
        "힘들어": 5,
        "지쳐": 5,
        "피곤": 5,
        "못하겠": 5,
        "tired": 5,
        "exhausted": 5,
        "걱정": 4,
        "불안": 4,
        "worried": 4,
        "anxious": 4,
        "괜찮": 2,
    },
    "crying_closed_eyes": {
        "엉엉": 5,
        "으앙": 5,
        "너무 슬퍼": 5,
        "울어": 4,
        "울면서": 4,
        "crying": 4,
        "sobbing": 5,
        "sob": 3,
    },
    "teary": {
        "눈물": 4,
        "슬퍼": 4,
        "우울": 3,
        "울것": 4,
        "울 것": 4,
        "teary": 4,
        "sad": 3,
    },
    "surprised_wide": {
        "깜짝": 4,
        "헉": 4,
        "놀라": 4,
        "진짜?": 4,
        "정말?": 4,
        "surprise": 4,
        "shock": 4,
        "no way": 4,
        "wait": 3,
    },
    "pouty": {
        "삐": 4,
        "흥": 4,
        "토라": 4,
        "질투": 4,
        "안왔": 3,
        "바빠": 3,
        "jealous": 4,
        "pout": 4,
    },
    "bashful_blush": {
        "예뻐": 4,
        "예쁘": 4,
        "귀엽": 4,
        "귀여워": 4,
        "보고싶": 4,
        "보고 싶": 4,
        "안아": 4,
        "뽀뽀": 5,
        "수줍": 4,
        "부끄": 4,
        "쑥스": 4,
        "blush": 4,
        "shy": 4,
        "cute": 4,
        "pretty": 4,
        "beautiful": 4,
    },
    "playful_behind_back": {
        "사랑해": 5,
        "좋아해": 5,
        "최고": 4,
        "대박": 4,
        "짱": 4,
        "완벽": 4,
        "야호": 5,
        "와아": 4,
        "와우": 4,
        "love": 5,
        "awesome": 4,
        "amazing": 4,
        "고마워": 4,
        "thanks": 4,
        "thank you": 4,
        "헤헤": 3,
        "히히": 3,
        "후후": 3,
        "두근": 3,
        "설레": 3,
        "데이트": 4,
    },
    "playful_tease": {
        "장난": 4,
        "놀려": 4,
        "약올": 4,
        "바보": 3,
        "tease": 4,
        "playful": 3,
        "silly": 3,
    },
    "curious_tilt": {
        "왜": 2,
        "어째서": 4,
        "궁금": 4,
        "뭐야": 3,
        "question": 3,
        "curious": 4,
        "what": 2,
        "why": 2,
    },
    "cheerful_bright": {
        "좋아": 3,
        "오케이": 3,
        "해보자": 3,
        "기뻐": 3,
        "신나": 3,
        "happy": 3,
        "yay": 3,
        "nice": 3,
        "good": 2,
        "ok": 2,
        "okay": 2,
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

