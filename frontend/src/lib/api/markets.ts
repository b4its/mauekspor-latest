import { apiFetch } from '$lib/api/client';
import type { MarketInsight } from '$lib/data/trade';

export type CreateMarketInsightPayload = {
	productId: string;
	country: string;
	projectId?: string;
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
