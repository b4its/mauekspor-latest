import { apiFetch } from '$lib/api/client';
import type { ApiKey } from '$lib/data/trade';

export function listApiKeys() {
	return apiFetch<ApiKey[]>('/api-keys/');
}

export function createApiKey(name: string, scopes: string[]) {
	return apiFetch<ApiKey>('/api-keys/', { method: 'POST', body: JSON.stringify({ name, scopes }) });
}

export function revokeApiKey(id: string) {
	return apiFetch<ApiKey>(`/api-keys/${id}/revoke/`, { method: 'POST' });
}
