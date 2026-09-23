import { apiFetch } from '$lib/api/client';
import type { AutomationRule } from '$lib/data/trade';

export function listAutomations() {
	return apiFetch<AutomationRule[]>('/automations/');
}

export function activateAutomation(id: string) {
	return apiFetch<AutomationRule>(`/automations/${id}/activate/`, { method: 'POST' });
}

export function runAutomation(id: string) {
	return apiFetch<AutomationRule>(`/automations/${id}/run/`, { method: 'POST' });
}
