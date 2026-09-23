import os

import pytest

os.environ.setdefault("MAUEKSPOR_DISABLE_PERSISTENCE", "1")


@pytest.fixture(autouse=True)
def clean_store():
    from app import db

    db.reset_store()
    yield
