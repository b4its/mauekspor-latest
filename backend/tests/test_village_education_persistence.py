"""Materi desa tidak boleh menghapus modul dan revisi yang dibuat pengguna."""

from fastapi.testclient import TestClient

from app import db
from app.main import app
from app.seed_village_commodities import VILLAGE_EDU_MODULES, seed_village_education


def test_reseed_education_preserves_custom_modules_and_edits():
    with TestClient(app):
        village_id = VILLAGE_EDU_MODULES[0]["id"]
        custom = db.insert("educational_modules", {
            "id": "EDU-CUSTOM-PERSIST", "title": "Pelatihan rantai pasok desa"
        })
        module = db.get("educational_modules", village_id)
        module["title"] = "Judul yang sudah disunting"
        db.save(module)
        before_count = len(db.all("educational_modules"))

        seed_village_education()
        seed_village_education()

        assert db.get("educational_modules", custom["id"])["title"] == custom["title"]
        assert db.get("educational_modules", village_id)["title"] == "Judul yang sudah disunting"
        assert len(db.all("educational_modules")) == before_count


def test_authored_quiz_is_used_and_scoped_to_learner():
    with TestClient(app) as client:
        module_id = "EDU-CUSTOM-QUIZ"
        db.insert("educational_modules", {"id": module_id, "title": "Pengiriman desa"})
        db.insert("educational_lessons", {
            "id": "LSN-CUSTOM-QUIZ", "moduleId": module_id, "kind": "Quiz",
            "quizQuestions": [{
                "id": "Q-1", "question": "Dokumen apa yang mencatat isi kemasan?",
                "options": ["Faktur", "Daftar kemasan"], "correct_index": 1,
                "explanation": "Daftar kemasan mencatat isi setiap koli.",
            }],
        })
        assert db.find("educational_lessons", moduleId=module_id)[0]["quizQuestions"][0]["correct_index"] == 1
        response = client.get(f"/api/v1/educational/modules/{module_id}/quiz/")
        assert response.status_code == 401
        client.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        assert db.find("educational_lessons", moduleId=module_id)[0]["quizQuestions"][0]["correct_index"] == 1
        quiz = client.get(f"/api/v1/educational/modules/{module_id}/quiz/").json()["data"]
        assert quiz["questionCount"] == 1
        assert "answer" not in quiz["questions"][0]
        result = client.post(f"/api/v1/educational/modules/{module_id}/quiz/submit/", json={
            "answers": {"Q-1": 1},
        }).json()["data"]
        assert result["passed"] is True
        progress = client.get(f"/api/v1/educational/modules/{module_id}/progress/").json()["data"]
        assert "LSN-CUSTOM-QUIZ" in progress["completedLessonIds"]
