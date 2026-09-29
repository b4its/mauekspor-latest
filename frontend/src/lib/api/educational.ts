import { apiFetch } from '$lib/api/client';
import type { EducationalLesson, EducationalModule } from '$lib/data/trade';

export type LessonPayload = {
	id?: string;
	title: string;
	duration?: string;
	kind?: 'Video' | 'Reading' | 'Quiz' | string;
	content?: string;
	video_url?: string;
	videoUrl?: string;
	key_points?: string[];
	quiz_questions?: Array<{
		id?: string;
		question: string;
		options: string[];
		correct_index: number;
		explanation?: string;
	}>;
};

export type EducationalModulePayload = {
	title: string;
	description?: string;
	level?: string;
	summary?: string;
	status?: string;
	order_index?: number;
	lessons?: LessonPayload[];
	quiz_questions?: Array<{
		id?: string;
		question: string;
		options: string[];
		correct_index: number;
		explanation?: string;
	}>;
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

export function addLessonToModule(moduleId: string, payload: LessonPayload) {
	return apiFetch<EducationalLesson>(`/educational/modules/${moduleId}/lessons/`, {
		method: 'POST',
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

export type QuizQuestion = { id: string; question: string; options: string[] };
export type ModuleQuiz = {
	moduleId: string;
	title: string;
	questions: QuizQuestion[];
	questionCount: number;
	lastAttempt: { bestScore: number; lastScore: number; passed: boolean; attemptCount: number } | null;
};
export type QuizResult = {
	moduleId: string;
	attemptId: string;
	score: number;
	correctCount: number;
	total: number;
	passed: boolean;
	details: Array<{
		id: string;
		question: string;
		options: string[];
		chosen: number | null;
		answer: number;
		correct: boolean;
		explanation: string;
	}>;
};

export function getModuleQuiz(moduleId: string) {
	return apiFetch<ModuleQuiz>(`/educational/modules/${moduleId}/quiz/`);
}

export function submitModuleQuiz(moduleId: string, answers: Record<string, number>) {
	return apiFetch<QuizResult>(`/educational/modules/${moduleId}/quiz/submit/`, {
		method: 'POST',
		body: JSON.stringify({ answers })
	});
}
