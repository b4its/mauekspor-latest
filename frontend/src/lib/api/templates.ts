import { apiFetch } from '$lib/api/client';
import type { Template } from '$lib/data/trade';

export type TemplatePayload = {
	title: string;
	category?: string;
	description?: string;
	status?: string;
	fields?: string[];
};

export function listTemplates() {
	return apiFetch<Template[]>('/templates/');
}

export function getTemplate(id: string) {
	return apiFetch<Template>(`/templates/${id}/`);
}

export function createTemplate(payload: TemplatePayload) {
	return apiFetch<Template>('/templates/', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateTemplate(id: string, payload: Partial<TemplatePayload>) {
	return apiFetch<Template>(`/templates/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteTemplate(id: string) {
	return apiFetch<{ status: string; id: string }>(`/templates/${id}/`, { method: 'DELETE' });
}

export function useTemplate(id: string) {
	return apiFetch<Template>(`/templates/${id}/use/`, { method: 'POST' });
}
