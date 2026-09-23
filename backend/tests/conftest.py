import os

import pytest

os.environ.setdefault("MAUEKSPOR_DISABLE_PERSISTENCE", "1")
os.environ.setdefault("MAUEKSPOR_ADMIN_CODE", "admin-bootstrap-2026")
# Paksa AI mode mock selama test agar deterministik & tanpa network,
# meski .env lokal mungkin menyetel mode remote.
os.environ.setdefault("MAUEKSPOR_AI_MODE", "mock")
os.environ.pop("MAUEKSPOR_AI_API_KEY", None)

# Matikan rate-limit middleware HTTP selama test. Beberapa "megatest"
# (mis. test_features) melakukan >120 request/60s sehingga diam-diam
# menabrak kuota dan gagal dengan 429 — bukan bug aplikasi. Middleware
# dinonaktifkan di sini, sedangkan logika rate-limit & lockout tetap diuji
# secara langsung (unit) di test_security / test_audit_regressions.
os.environ.setdefault("MAUEKSPOR_DISABLE_RATE_LIMIT", "1")


@pytest.fixture(autouse=True)
def clean_store():
    from app import db
    from app import main as app_main

    db.reset_store()
    # Reset state rate-limiter & lockout agar tes tidak saling tercemar.
    # Tanpa ini, suite penuh >120 request/60s akan memicu 429 di tengah jalan.
    app_main._ratelimit.clear()
    app_main._login_failures.clear()
    yield
    app_main._ratelimit.clear()
    app_main._login_failures.clear()
