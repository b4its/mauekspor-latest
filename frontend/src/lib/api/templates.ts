import { apiFetch } from '$lib/api/client';
import type { Template } from '$lib/data/trade';

export function listTemplates() {
	return apiFetch<Template[]>('/templates/');
}

export function createTemplate(payload: Pick<Template, 'title' | 'category' | 'description'>) {
	return apiFetch<Template>('/templates/', { method: 'POST', body: JSON.stringify(payload) });
}

export function useTemplate(id: string) {
	return apiFetch<Template>(`/templates/${id}/use/`, { method: 'POST' });
}
