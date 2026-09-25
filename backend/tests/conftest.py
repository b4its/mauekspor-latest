import os

import pytest

os.environ.setdefault("MAUEKSPOR_DISABLE_PERSISTENCE", "1")
os.environ.setdefault("MAUEKSPOR_ADMIN_CODE", "admin-bootstrap-2026")
# Turunkan iterasi PBKDF2 selama test: 100_000 iterasi ≈ 3.5s per hash, dan
# hampir setiap test melakukan login → suite membengkak ~10 menit. Nilai 1
# tetap menguji jalur kode yang sama (hash + verify + compare_digest).
os.environ.setdefault("MAUEKSPOR_PBKDF2_ITERATIONS", "1")
# Paksa AI mode mock selama test agar deterministik & tanpa network,
# meski .env lokal mungkin menyetel mode remote.
os.environ["MAUEKSPOR_AI_MODE"] = "mock"
os.environ.pop("MAUEKSPOR_AI_API_KEY", None)

# Matikan rate-limit middleware HTTP selama test. Beberapa "megatest"
# (mis. test_features) melakukan >120 request/60s sehingga diam-diam
# menabrak kuota dan gagal dengan 429 — bukan bug aplikasi. Middleware
# dinonaktifkan di sini, sedangkan logika rate-limit & lockout tetap diuji
# secara langsung (unit) di test_security / test_audit_regressions.
os.environ.setdefault("MAUEKSPOR_DISABLE_RATE_LIMIT", "1")

# Pastikan upload dir menggunakan direktori lokal saat test berjalan di luar container
if os.environ.get("MAUEKSPOR_UPLOAD_DIR", "").startswith("/app"):
    os.environ["MAUEKSPOR_UPLOAD_DIR"] = os.path.join(os.getcwd(), "uploads")


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
