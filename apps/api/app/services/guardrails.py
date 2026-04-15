import re

from app.core.config import get_settings


def sanitize_user_text(text: str) -> str:
    settings = get_settings()
    text = text.strip()
    if len(text) > settings.max_question_chars:
        text = text[: settings.max_question_chars]
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def detect_prompt_injection_signals(text: str) -> list[str]:
    lowered = text.lower()
    signals: list[str] = []
    suspicious = [
        "ignore previous",
        "disregard",
        "system prompt",
        "you are now",
        "jailbreak",
        "show me your instructions",
    ]
    for s in suspicious:
        if s in lowered:
            signals.append(s)
    return signals
