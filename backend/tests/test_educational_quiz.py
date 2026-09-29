"""Test kuis edukasi per modul (soal menyesuaikan topik & materi modul)."""

import contextlib

from fastapi.testclient import TestClient

from app import db
from app.main import app
from app.services import quiz


@contextlib.contextmanager
def _client(email="admin@mauekspor.example", password="admin123"):
    with TestClient(app) as c:
        c.post("/api/v1/auth/login/", json={"email": email, "password": password})
        yield c


# ── Unit: generator soal ──────────────────────────────────────────────────────
def test_build_quiz_uses_module_topic():
    module = {
        "id": "EDU-COSTING",
        "title": "Incoterms and Landed Costing",
        "summary": "Model EXW, FOB, CIF, and landed cost with margin and FX risk.",
    }
    questions = quiz.build_quiz(module, [])
    texts = " ".join(q["question"].lower() for q in questions)
    assert "incoterm" in texts
    assert "landed cost" in texts
    assert len(questions) >= 4


def test_build_quiz_compliance_topic():
    module = {
        "id": "EDU-COMPLIANCE",
        "title": "Compliance and HS Code Evidence",
        "summary": "Build evidence-backed compliance workflows for target markets.",
    }
    questions = quiz.build_quiz(module, [])
    texts = " ".join(q["question"].lower() for q in questions)
    assert "hs" in texts
    assert "kepatuhan" in texts or "bukti" in texts or "preferensial" in texts


def test_build_quiz_falls_back_to_general():
    module = {"id": "EDU-XYZ", "title": "Unknown", "summary": "nothing here"}
    questions = quiz.build_quiz(module, [])
    assert len(questions) >= 3  # bank umum dipakai


def test_build_quiz_answer_index_is_valid_and_deterministic():
    module = {"id": "EDU-START", "title": "Export Readiness Foundations", "summary": "readiness basics"}
    first = quiz.build_quiz(module, [])
    second = quiz.build_quiz(module, [])
    for q in first:
        assert 0 <= q["answer"] < len(q["options"])
    # deterministik antar pemanggilan (hash stabil, bukan hash() teracak)
    assert [q["answer"] for q in first] == [q["answer"] for q in second]


def test_public_quiz_hides_answer_key():
    module = {"id": "EDU-START", "title": "Export Readiness", "summary": "readiness"}
    questions = quiz.build_quiz(module, [])
    public = quiz.public_quiz(questions)
    assert all("answer" not in q for q in public)
    assert all("explanation" not in q for q in public)


def test_grade_quiz_all_correct_and_all_wrong():
    module = {"id": "EDU-CMP", "title": "Compliance HS", "summary": "compliance hs code"}
    questions = quiz.build_quiz(module, [])
    correct = {q["id"]: q["answer"] for q in questions}
    res = quiz.grade_quiz(questions, correct)
    assert res["score"] == 100 and res["passed"] is True
    assert res["correctCount"] == res["total"]

    wrong = {q["id"]: (q["answer"] + 1) % len(q["options"]) for q in questions}
    res2 = quiz.grade_quiz(questions, wrong)
    assert res2["score"] == 0 and res2["passed"] is False


def test_grade_quiz_partial_and_details():
    module = {"id": "EDU-P", "title": "Export Readiness", "summary": "readiness packaging"}
    questions = quiz.build_quiz(module, [])[:4]
    answers = {questions[0]["id"]: questions[0]["answer"]}
    res = quiz.grade_quiz(questions, answers)
    assert res["correctCount"] == 1
    assert len(res["details"]) == len(questions)
    assert res["details"][0]["correct"] is True
    assert "explanation" in res["details"][0]


# ── API ───────────────────────────────────────────────────────────────────────
def test_get_module_quiz_requires_auth():
    # Tabel kustom: tanpa login → tidak boleh 200.
    with TestClient(app) as c:
        res = c.get("/api/v1/educational/modules/EDU-DES-PANEN-01/quiz/")
        assert res.status_code in (401, 403)


def test_get_module_quiz_returns_questions():
    with _client() as c:
        res = c.get("/api/v1/educational/modules/EDU-DES-KARANTINA-06/quiz/")
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["moduleId"] == "EDU-DES-KARANTINA-06"
        assert data["questionCount"] >= 3
        assert len(data["questions"]) == data["questionCount"]
        # Kunci jawaban tidak boleh bocor ke klien.
        assert all("answer" not in q for q in data["questions"])


def test_get_module_quiz_missing_module_404():
    with _client() as c:
        res = c.get("/api/v1/educational/modules/EDU-TIDAK-ADA/quiz/")
        assert res.status_code == 404


def test_submit_quiz_all_correct_passes_and_records():
    with _client() as c:
        res = c.get("/api/v1/educational/modules/EDU-DES-DOC-05/quiz/")
        questions = res.json()["data"]["questions"]
        # Ambil kunci dari service agar test tidak bergantung posisi opsi.
        module = db.get("educational_modules", "EDU-DES-DOC-05")
        key = {q["id"]: q["answer"] for q in quiz.build_quiz(module, db.find("educational_lessons", moduleId="EDU-DES-DOC-05"))}
        answers = {q["id"]: key[q["id"]] for q in questions}
        sub = c.post("/api/v1/educational/modules/EDU-DES-DOC-05/quiz/submit/", json={"answers": answers})
        assert sub.status_code == 200, sub.text
        data = sub.json()["data"]
        assert data["score"] == 100
        assert data["passed"] is True
        assert data["attemptId"]

        # Hasil tersimpan: percobaan terakhir muncul saat GET ulang.
        again = c.get("/api/v1/educational/modules/EDU-DES-DOC-05/quiz/").json()["data"]
        assert again["lastAttempt"]["bestScore"] == 100
        assert again["lastAttempt"]["attemptCount"] == 1


def test_submit_quiz_passing_marks_quiz_lesson_complete():
    with _client() as c:
        module = db.get("educational_modules", "EDU-DES-PANEN-01")
        lessons = db.find("educational_lessons", moduleId="EDU-DES-PANEN-01")
        key = {q["id"]: q["answer"] for q in quiz.build_quiz(module, lessons)}
        c.post("/api/v1/educational/modules/EDU-DES-PANEN-01/quiz/submit/", json={"answers": key})
        prog = c.get("/api/v1/educational/modules/EDU-DES-PANEN-01/progress/").json()["data"]
        assert "LSN-PAN-04" in prog["completedLessonIds"] or "LSN-DES-PANEN-07" in prog["completedLessonIds"]


def test_submit_quiz_bad_answers_fails():
    with _client() as c:
        questions = c.get("/api/v1/educational/modules/EDU-DES-PANEN-01/quiz/").json()["data"]["questions"]
        answers = {q["id"]: 999 for q in questions}  # opsi tak valid → salah semua
        data = c.post("/api/v1/educational/modules/EDU-DES-PANEN-01/quiz/submit/", json={"answers": answers}).json()["data"]
        assert data["score"] == 0
        assert data["passed"] is False


def test_submit_quiz_rejects_non_object_answers():
    with _client() as c:
        res = c.post("/api/v1/educational/modules/EDU-DES-PANEN-01/quiz/submit/", json={"answers": [1, 2, 3]})
        assert res.status_code == 422


def test_get_module_detail_includes_lessons_list():
    with _client() as c:
        data = c.get("/api/v1/educational/modules/EDU-DES-PANEN-01/").json()["data"]
        assert isinstance(data.get("lessonsList"), list)
        assert any(l.get("kind") == "Quiz" for l in data["lessonsList"])
        # `lessons` (jumlah) tetap numerik, tidak tertimpa array.
        assert isinstance(data.get("lessons"), int)
