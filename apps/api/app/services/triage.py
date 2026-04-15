from __future__ import annotations

import re
from dataclasses import dataclass

from openai import OpenAI

from app.core.config import Settings, get_settings


@dataclass
class TriageResult:
    severity: str
    needs_human: bool
    confidence: float
    reasoning_summary: str
    suggested_next_steps: list[str]
    label: str


CRITICAL_PATTERNS = [
    r"\bdata breach\b",
    r"\bransomware\b",
    r"\bsecurity incident\b",
    r"\bpci\b",
    r"\bpayment\b.*\b(fraud|stolen)\b",
]
HIGH_PATTERNS = [
    r"\b(production|prod)\b.*\b(down|outage)\b",
    r"\ball users\b",
    r"\bsso\b",
    r"\b401\b",
    r"\blo(g)?in\b.*\b(fail|broken)\b",
]


def rule_based_triage(question: str, retrieved_confidence: float) -> TriageResult | None:
    q = question.lower()
    for pat in CRITICAL_PATTERNS:
        if re.search(pat, q):
            return TriageResult(
                severity="critical",
                needs_human=True,
                confidence=min(0.95, max(retrieved_confidence, 0.5)),
                reasoning_summary="Critical signal detected in the question text.",
                suggested_next_steps=["Page on-call security", "Open incident channel", "Preserve logs"],
                label="critical_signal",
            )
    for pat in HIGH_PATTERNS:
        if re.search(pat, q):
            return TriageResult(
                severity="high",
                needs_human=True,
                confidence=min(0.9, max(retrieved_confidence, 0.45)),
                reasoning_summary="High-impact pattern detected (auth or widespread outage).",
                suggested_next_steps=["Verify scope", "Check recent changes", "Escalate to owning team"],
                label="high_signal",
            )
    if retrieved_confidence < 0.35:
        return TriageResult(
            severity="medium",
            needs_human=True,
            confidence=retrieved_confidence,
            reasoning_summary="Retrieved evidence is weak; more data is needed.",
            suggested_next_steps=["Ask for timestamps", "Request error messages", "Confirm environment"],
            label="low_evidence",
        )
    return None


def llm_triage(question: str, answer_summary: str, settings: Settings | None = None) -> TriageResult:
    settings = settings or get_settings()
    if not settings.openai_api_key:
        return TriageResult(
            severity="medium",
            needs_human=False,
            confidence=0.5,
            reasoning_summary="LLM triage skipped (no API key).",
            suggested_next_steps=[],
            label="fallback",
        )
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""Classify support triage for the incident.
Question: {question}
Draft answer summary: {answer_summary}

Return JSON: severity (low|medium|high|critical), needs_human (bool), confidence (0-1), reasoning_summary (string), suggested_next_steps (string array), label (short snake_case).
"""
    resp = client.chat.completions.create(
        model=settings.chat_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw = resp.choices[0].message.content or "{}"
    import json

    data = json.loads(raw)
    return TriageResult(
        severity=str(data.get("severity", "medium")),
        needs_human=bool(data.get("needs_human", False)),
        confidence=float(data.get("confidence", 0.5)),
        reasoning_summary=str(data.get("reasoning_summary", "")),
        suggested_next_steps=list(data.get("suggested_next_steps") or []),
        label=str(data.get("label", "llm")),
    )


def run_triage(
    question: str,
    answer_summary: str,
    retrieved_confidence: float,
    settings: Settings | None = None,
) -> TriageResult:
    settings = settings or get_settings()
    rb = rule_based_triage(question, retrieved_confidence)
    if rb:
        return rb
    return llm_triage(question, answer_summary, settings)
