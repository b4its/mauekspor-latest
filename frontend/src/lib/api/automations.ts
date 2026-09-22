import { apiFetch } from '$lib/api/client';
import type { AutomationRule } from '$lib/data/trade';

export type AutomationPayload = {
	name: string;
	trigger?: string;
	action?: string;
	module?: string;
	description?: string;
	status?: string;
};

export function listAutomations() {
	return apiFetch<AutomationRule[]>('/automations/');
}

export function getAutomation(id: string) {
	return apiFetch<AutomationRule>(`/automations/${id}/`);
}

export function createAutomation(payload: AutomationPayload) {
	return apiFetch<AutomationRule>('/automations/', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateAutomation(id: string, payload: Partial<AutomationPayload>) {
	return apiFetch<AutomationRule>(`/automations/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteAutomation(id: string) {
	return apiFetch<{ status: string; id: string }>(`/automations/${id}/`, { method: 'DELETE' });
}

export function activateAutomation(id: string) {
	return apiFetch<AutomationRule>(`/automations/${id}/activate/`, { method: 'POST' });
}

export function pauseAutomation(id: string) {
	return apiFetch<AutomationRule>(`/automations/${id}/pause/`, { method: 'POST' });
}

export function runAutomation(id: string) {
	return apiFetch<AutomationRule>(`/automations/${id}/run/`, { method: 'POST' });
}
