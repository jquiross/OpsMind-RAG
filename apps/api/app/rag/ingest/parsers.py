import json
from pathlib import Path

from pypdf import PdfReader

from app.rag.ingest.normalize import normalize_text, strip_control_chars


def parse_txt(path: Path) -> tuple[str, dict]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = normalize_text(strip_control_chars(raw))
    return text, {"format": "txt", "filename": path.name}


def parse_md(path: Path) -> tuple[str, dict]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = normalize_text(strip_control_chars(raw))
    headings = [line.strip("# ").strip() for line in text.split("\n") if line.startswith("# ")]
    return text, {"format": "markdown", "filename": path.name, "headings_preview": headings[:10]}


def parse_pdf(path: Path) -> tuple[str, dict]:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for i, page in enumerate(reader.pages):
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    raw = "\n\n".join(pages)
    text = normalize_text(strip_control_chars(raw))
    return text, {"format": "pdf", "filename": path.name, "page_count": len(reader.pages)}


def parse_ticket_json(path: Path) -> tuple[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, dict):
                title = item.get("title", "")
                body = item.get("body", item.get("description", ""))
                sev = item.get("severity", "")
                lines.append(f"Title: {title}\nSeverity: {sev}\n{body}\n---\n")
        text = normalize_text("\n".join(lines))
        return text, {"format": "ticket_json", "count": len(data)}
    if isinstance(data, dict):
        text = normalize_text(json.dumps(data, ensure_ascii=False, indent=2))
        return text, {"format": "ticket_json", "keys": list(data.keys())}
    text = normalize_text(str(data))
    return text, {"format": "ticket_json"}
