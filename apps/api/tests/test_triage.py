from app.services.triage import rule_based_triage


def test_critical_signal():
    r = rule_based_triage("possible data breach in production", 0.9)
    assert r is not None
    assert r.severity == "critical"
    assert r.needs_human is True


def test_low_evidence():
    r = rule_based_triage("printer not working", 0.1)
    assert r is not None
    assert r.label == "low_evidence"
