"""Load sample markdown docs with stable UUIDs for eval matching."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import UUID

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

for path in (REPO_ROOT / "apps" / "api", REPO_ROOT):
    if (path / "app").is_dir():
        sys.path.insert(0, str(path))
        break

os.environ.setdefault("POSTGRES_HOST", "localhost")

from app.db.session import SessionLocal
from app.services.ingest_service import ingest_text_as_document

DOC_SSO = UUID("11111111-1111-1111-1111-111111111111")
DOC_WEBHOOK = UUID("22222222-2222-2222-2222-222222222222")
DOC_INVOICE = UUID("33333333-3333-3333-3333-333333333333")


def main() -> None:
    samples = REPO_ROOT / "data" / "sample_docs"
    sso = (samples / "sso_runbook.md").read_text(encoding="utf-8")
    wh = (samples / "webhooks.md").read_text(encoding="utf-8")
    inv = (samples / "billing_invoices.md").read_text(encoding="utf-8")

    db = SessionLocal()
    try:
        ingest_text_as_document(db, title="SSO Runbook", text=sso, source_type="md", document_id=DOC_SSO)
        ingest_text_as_document(
            db, title="Webhooks Operations", text=wh, source_type="md", document_id=DOC_WEBHOOK
        )
        ingest_text_as_document(
            db, title="Billing Invoices", text=inv, source_type="md", document_id=DOC_INVOICE
        )
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
