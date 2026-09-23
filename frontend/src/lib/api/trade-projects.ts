import { apiFetch } from '$lib/api/client';
import type { TradeProject } from '$lib/data/trade';

export type CreateTradeProjectPayload = {
	name: string;
	projectType: string;
	product: string;
	buyer: string;
	country: string;
	incoterm: string;
	targetValue?: number;
	eta?: string;
};

export function listTradeProjects() {
	return apiFetch<TradeProject[]>('/trade-projects/');
}

export function getTradeProject(id: string) {
	return apiFetch<TradeProject>(`/trade-projects/${id}/`);
}

export function createTradeProject(payload: CreateTradeProjectPayload) {
	return apiFetch<TradeProject>('/trade-projects/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}
