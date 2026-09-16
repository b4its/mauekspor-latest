import os

import pytest

os.environ.setdefault("MAUEKSPOR_DISABLE_PERSISTENCE", "1")
os.environ.setdefault("MAUEKSPOR_ADMIN_CODE", "admin-bootstrap-2026")
# Paksa AI mode mock selama test agar deterministik & tanpa network,
# meski .env lokal mungkin menyetel mode remote.
os.environ.setdefault("MAUEKSPOR_AI_MODE", "mock")
os.environ.pop("MAUEKSPOR_AI_API_KEY", None)


@pytest.fixture(autouse=True)
def clean_store():
    from app import db

    db.reset_store()
    yield
