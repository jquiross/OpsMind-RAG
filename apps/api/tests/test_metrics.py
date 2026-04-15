from uuid import UUID

from app.rag.eval.metrics import hit_at_k, mean_reciprocal_rank, precision_at_k

A = UUID("11111111-1111-1111-1111-111111111111")
B = UUID("22222222-2222-2222-2222-222222222222")


def test_hit_at_k():
    assert hit_at_k([A], [B, A], k=3) is True
    assert hit_at_k([A], [B], k=1) is False


def test_precision_at_k():
    assert precision_at_k([A], [A, B, B], k=3) == 1 / 3


def test_mrr():
    assert mean_reciprocal_rank([A], [B, A]) == 0.5
