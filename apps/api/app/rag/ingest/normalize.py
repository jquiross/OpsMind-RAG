import re
import unicodedata


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_control_chars(text: str) -> str:
    return "".join(ch for ch in text if ch == "\n" or ch == "\t" or unicodedata.category(ch) != "Cc")
