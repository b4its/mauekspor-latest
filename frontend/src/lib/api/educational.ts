import { apiFetch } from '$lib/api/client';
import type { EducationalModule } from '$lib/data/trade';

export type EducationalModulePayload = {
	title: string;
	description?: string;
	order_index?: number;
};

export function listEducationalModules() {
	return apiFetch<EducationalModule[]>('/educational/');
}

export function listEducationalModulesV2() {
	return apiFetch<EducationalModule[]>('/educational/modules/');
}

export function getEducationalModule(id: string) {
	return apiFetch<EducationalModule>(`/educational/modules/${id}/`);
}

export function createEducationalModule(payload: EducationalModulePayload) {
	return apiFetch<EducationalModule>('/educational/modules/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateEducationalModule(id: string, payload: EducationalModulePayload) {
	return apiFetch<EducationalModule>(`/educational/modules/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteEducationalModule(id: string) {
	return apiFetch<{ status: string }>(`/educational/modules/${id}/`, { method: 'DELETE' });
}

export function publishEducationalModule(id: string) {
	return apiFetch<EducationalModule>(`/educational/modules/${id}/publish/`, { method: 'POST' });
}

export type LessonProgress = {
	moduleId: string;
	completedLessonIds: string[];
};

export function getLessonProgress(moduleId: string) {
	return apiFetch<LessonProgress>(`/educational/modules/${moduleId}/progress/`);
}

export function setLessonComplete(moduleId: string, lessonId: string, completed: boolean) {
	return apiFetch<{ id: string }>(`/educational/modules/${moduleId}/lessons/${lessonId}/complete/`, {
		method: 'POST',
		body: JSON.stringify({ completed })
	});
}

// ---------- Kuis modul ----------
export type QuizQuestion = {
	id: string;
	question: string;
	options: string[];
};

export type QuizAttemptSummary = {
	bestScore: number;
	lastScore: number;
	passed: boolean;
	attemptCount: number;
};

export type ModuleQuiz = {
	moduleId: string;
	title: string;
	questions: QuizQuestion[];
	questionCount: number;
	lastAttempt: QuizAttemptSummary | null;
};

export type QuizResultDetail = {
	id: string;
	question: string;
	options: string[];
	chosen: number | null;
	answer: number;
	correct: boolean;
	explanation: string;
};

export type QuizResult = {
	moduleId: string;
	attemptId: string;
	score: number;
	correctCount: number;
	total: number;
	passed: boolean;
	details: QuizResultDetail[];
};

/** Ambil soal kuis modul (topik menyesuaikan materi modul). */
export function getModuleQuiz(moduleId: string) {
	return apiFetch<ModuleQuiz>(`/educational/modules/${moduleId}/quiz/`);
}

/** Kirim jawaban kuis (map questionId → indeks opsi) dan dapatkan penilaian. */
export function submitModuleQuiz(moduleId: string, answers: Record<string, number>) {
	return apiFetch<QuizResult>(`/educational/modules/${moduleId}/quiz/submit/`, {
		method: 'POST',
		body: JSON.stringify({ answers })
	});
}
