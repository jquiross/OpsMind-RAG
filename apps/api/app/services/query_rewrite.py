import json

from openai import OpenAI

from app.core.config import Settings, get_settings


def rewrite_query_for_search(question: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    if not settings.openai_api_key:
        return question
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""Rewrite the following user question into a concise search query for internal documentation retrieval.
Keep domain terms. Output JSON: {{"rewritten": "..."}}
Question: {question}
"""
    resp = client.chat.completions.create(
        model=settings.chat_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    raw = resp.choices[0].message.content or "{}"
    data = json.loads(raw)
    return str(data.get("rewritten", question)).strip() or question
