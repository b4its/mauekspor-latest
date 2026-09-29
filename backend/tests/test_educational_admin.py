"""Test manajemen modul edukasi, materi, dan kuis interaktif."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient, email: str = "admin@mauekspor.example", password: str = "admin123") -> str:
    res = c.post("/api/v1/auth/login/", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_seeded_modules_not_empty():
    """Memastikan seluruh modul dari seeder memiliki materi dan kuis (tidak boleh kosong)."""
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/educational/modules/", headers=_auth(token))
        assert res.status_code == 200, res.text
        all_modules = res.json()["data"]
        modules = [m for m in all_modules if not (str(m["id"]).startswith("EDU-0") or str(m["id"]).startswith("EDU-1"))]
        assert len(modules) >= 8, f"Harus ada minimal 8 modul resmi, ditemukan {len(modules)}"

        for m in modules:
            detail = c.get(f"/api/v1/educational/modules/{m['id']}/", headers=_auth(token))
            assert detail.status_code == 200, detail.text
            d_data = detail.json()["data"]
            lessons = d_data.get("lessonsList") or (d_data.get("lessons") if isinstance(d_data.get("lessons"), list) else [])
            assert len(lessons) >= 2, f"Modul {m['id']} minimal punya 2 materi/kuis, ditemukan {len(lessons)}"
            
            # Pastikan terdapat lesson bertipe Quiz atau memiliki quizQuestions
            has_quiz = any(
                lsn.get("kind") == "Quiz" or bool(lsn.get("quizQuestions")) or bool(lsn.get("quiz_questions"))
                for lsn in lessons
            )
            assert has_quiz, f"Modul {m['id']} wajib memiliki kuis interaktif"

            # Pastikan jika ada materi bertipe Video, memiliki videoUrl YouTube yang valid
            video_lessons = [l for l in lessons if l.get("kind") == "Video"]
            if video_lessons:
                for vl in video_lessons:
                    v_url = vl.get("videoUrl") or vl.get("video_url") or ""
                    assert "youtube.com" in v_url or "youtu.be" in v_url, f"Materi video {vl.get('title')} harus memiliki URL YouTube resmi, dapat: {v_url}"


def test_create_module_with_materials_and_quiz():
    """Menguji pembuatan modul lengkap beserta materi dan kuis oleh admin."""
    with TestClient(app) as c:
        token = _login(c)
        payload = {
            "title": "Modul Uji Kepatuhan Barantin & Kemasan Kayu ISPM 15",
            "description": "Pengujian modul terintegrasi materi dan kuis",
            "summary": "Ringkasan pengujian modul ekspor",
            "level": "Intermediate",
            "status": "Published",
            "order_index": 99,
            "lessons": [
                {
                    "title": "Materi 1: Regulasi Karantina Hewan dan Tumbuhan UU 21/2019",
                    "kind": "Reading",
                    "duration": "6 min",
                    "content": "Pemeriksaan fisik dan uji lab oleh Badan Karantina Indonesia.",
                    "key_points": ["UU No. 21/2019", "Phytosanitary Certificate"]
                },
                {
                    "title": "Materi 2: Standar Palet Kayu ISPM 15",
                    "kind": "Reading",
                    "duration": "5 min",
                    "content": "Perlakuan panas dan fumigasi metil bromida berstempel resmi.",
                    "key_points": ["ISPM 15", "Heat Treatment HT"]
                },
                {
                    "title": "Materi 3: Video Panduan Karantina Tumbuhan",
                    "kind": "Video",
                    "duration": "8 min",
                    "content": "Video alur karantina resmi Barantin.",
                    "video_url": "https://www.youtube.com/watch?v=JnMtuZTjV6Q",
                    "key_points": ["Inspeksi lapangan", "Sertifikasi online"]
                }
            ],
            "quiz_questions": [
                {
                    "question": "Lembaga penerbit Phytosanitary Certificate di Indonesia adalah...",
                    "options": [
                        "Badan Karantina Indonesia (Barantin)",
                        "Kementerian Keuangan",
                        "Bank Indonesia",
                        "Dinas Perhubungan"
                    ],
                    "correct_index": 0,
                    "explanation": "Barantin adalah otoritas karantina tunggal sesuai UU 21/2019."
                },
                {
                    "question": "Standar internasional untuk perlakuan kemasan kayu adalah...",
                    "options": [
                        "ISO 9001",
                        "ISPM 15",
                        "HACCP",
                        "Incoterms 2020"
                    ],
                    "correct_index": 1,
                    "explanation": "ISPM 15 mengatur standar perlakuan panas dan fumigasi palet kayu."
                }
            ]
        }

        create_res = c.post("/api/v1/educational/modules/", json=payload, headers=_auth(token))
        assert create_res.status_code == 200, create_res.text
        mod_data = create_res.json()["data"]
        mod_id = mod_data["id"]
        assert mod_data["title"] == payload["title"]
        # Lesson count harus 4: 3 materi (termasuk video) + 1 kuis lesson otomatis
        assert mod_data["lessonCount"] == 4
        assert mod_data["quizCount"] == 1

        # Verifikasi via get detail endpoint
        get_res = c.get(f"/api/v1/educational/modules/{mod_id}/", headers=_auth(token))
        assert get_res.status_code == 200, get_res.text
        detail = get_res.json()["data"]
        lessons_list = detail.get("lessonsList") if isinstance(detail.get("lessonsList"), list) else detail.get("lessons")
        assert len(lessons_list) == 4

        # Pastikan materi video tersimpan dengan videoUrl YouTube
        created_vid = [l for l in lessons_list if l.get("kind") == "Video"][0]
        assert created_vid.get("videoUrl") == "https://www.youtube.com/watch?v=JnMtuZTjV6Q"

        quiz_lsn = [l for l in lessons_list if l.get("kind") == "Quiz"][0]
        assert len(quiz_lsn["quizQuestions"]) == 2
        assert quiz_lsn["quizQuestions"][0]["question"] == "Lembaga penerbit Phytosanitary Certificate di Indonesia adalah..."

        # Update modul
        update_payload = {
            "title": "Modul Uji Kepatuhan Barantin (Updated)",
            "quiz_questions": [
                {
                    "question": "Pertanyaan Kuis Baru?",
                    "options": ["A", "B", "C", "D"],
                    "correct_index": 2,
                    "explanation": "Penjelasan baru"
                }
            ]
        }
        update_res = c.put(f"/api/v1/educational/modules/{mod_id}/", json=update_payload, headers=_auth(token))
        assert update_res.status_code == 200, update_res.text
        assert update_res.json()["data"]["title"] == "Modul Uji Kepatuhan Barantin (Updated)"

        # Hapus modul uji
        del_res = c.delete(f"/api/v1/educational/modules/{mod_id}/", headers=_auth(token))
        assert del_res.status_code == 200, del_res.text
