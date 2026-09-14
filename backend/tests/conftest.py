import os

import pytest

os.environ.setdefault("MAUEKSPOR_DISABLE_PERSISTENCE", "1")
os.environ.setdefault("MAUEKSPOR_ADMIN_CODE", "admin-bootstrap-2026")


@pytest.fixture(autouse=True)
def clean_store():
    from app import db

    db.reset_store()
    yield
