import { apiFetch } from '$lib/api/client';
import type { MarketInsight } from '$lib/data/trade';

export type CreateMarketInsightPayload = {
	country: string;
	productId?: string;
	projectId?: string;
	entryStrategy?: string;
};

export function listMarketInsights() {
	return apiFetch<MarketInsight[]>('/markets/');
}

export function getMarketInsight(id: string) {
	return apiFetch<MarketInsight>(`/markets/${id}/`);
}

export function createMarketInsight(payload: CreateMarketInsightPayload) {
	return apiFetch<MarketInsight>('/markets/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function refreshMarketInsight(id: string) {
	return apiFetch<MarketInsight>(`/markets/${id}/refresh/`, { method: 'POST' });
}

export function updateMarketInsight(id: string, payload: Partial<MarketInsight>) {
	return apiFetch<MarketInsight>(`/markets/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteMarketInsight(id: string) {
	return apiFetch<{ status: string; id: string }>(`/markets/${id}/`, { method: 'DELETE' });
}
