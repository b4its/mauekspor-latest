import { apiFetch } from '$lib/api/client';
import type { EducationalModule, EducationalArticle } from '$lib/data/trade';

export type EducationalModulePayload = {
	title: string;
	description?: string;
	order_index?: number;
};

export type EducationalArticlePayload = {
	module_id?: string;
	title: string;
	content?: string;
	video_url?: string;
	file_url?: string;
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
	return apiFetch<EducationalModule>(`/educational/${id}/publish/`, { method: 'POST' });
}

// ---------- Articles ----------
export function listEducationalArticles() {
	return apiFetch<EducationalArticle[]>('/educational/articles/');
}

export function getEducationalArticle(id: string) {
	return apiFetch<EducationalArticle>(`/educational/articles/${id}/`);
}

export function createEducationalArticle(payload: EducationalArticlePayload) {
	return apiFetch<EducationalArticle>('/educational/articles/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateEducationalArticle(id: string, payload: EducationalArticlePayload) {
	return apiFetch<EducationalArticle>(`/educational/articles/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteEducationalArticle(id: string) {
	return apiFetch<{ status: string }>(`/educational/articles/${id}/`, { method: 'DELETE' });
}

export function publishEducationalArticle(id: string) {
	return apiFetch<EducationalArticle>(`/educational/articles/${id}/publish/`, { method: 'POST' });
}

export function uploadEducationalFile(id: string, file: File) {
	const form = new FormData();
	form.append('file', file);
	return apiFetch<EducationalArticle>(`/educational/articles/${id}/upload-file/`, {
		method: 'POST',
		body: form,
		headers: {}
	});
}
