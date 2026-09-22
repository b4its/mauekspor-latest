import { apiFetch } from '$lib/api/client';
import type { Integration } from '$lib/data/trade';

export type IntegrationPayload = {
	name: string;
	category?: string;
	description?: string;
	status?: string;
	scopes?: string[];
};

export function listIntegrations() {
	return apiFetch<Integration[]>('/integrations/');
}

export function getIntegration(id: string) {
	return apiFetch<Integration>(`/integrations/${id}/`);
}

export function createIntegration(payload: IntegrationPayload) {
	return apiFetch<Integration>('/integrations/', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateIntegration(id: string, payload: Partial<IntegrationPayload>) {
	return apiFetch<Integration>(`/integrations/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteIntegration(id: string) {
	return apiFetch<{ status: string; id: string }>(`/integrations/${id}/`, { method: 'DELETE' });
}

export function connectIntegration(id: string) {
	return apiFetch<Integration>(`/integrations/${id}/connect/`, { method: 'POST' });
}

export function disconnectIntegration(id: string) {
	return apiFetch<Integration>(`/integrations/${id}/disconnect/`, { method: 'POST' });
}

export function syncIntegration(id: string) {
	return apiFetch<Integration>(`/integrations/${id}/sync/`, { method: 'POST' });
}
