import { apiFetch } from '$lib/api/client';
import type { Integration } from '$lib/data/trade';

export function listIntegrations() {
	return apiFetch<Integration[]>('/integrations/');
}

export function connectIntegration(id: string) {
	return apiFetch<Integration>(`/integrations/${id}/connect/`, { method: 'POST' });
}

export function syncIntegration(id: string) {
	return apiFetch<Integration>(`/integrations/${id}/sync/`, { method: 'POST' });
}
