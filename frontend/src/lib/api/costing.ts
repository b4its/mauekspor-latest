import { apiFetch } from '$lib/api/client';
import type { CostingScenario } from '$lib/data/trade';

export type CreateCostingPayload = {
	title: string;
	projectId: string;
	productId: string;
	incoterm: CostingScenario['incoterm'];
	margin: number;
	destination: string;
	cogs_per_unit_idr?: number;
	packing_cost_idr?: number;
	distance_km?: number;
};

export type UpdateCostingPayload = Partial<CreateCostingPayload> & {
	exchange_rate?: number;
};

export type ExchangeRate = {
	id: string;
	rate: number;
	source: string;
	updatedAt: string;
};

export function listCostingScenarios() {
	return apiFetch<CostingScenario[]>('/costing/');
}

export function getCostingScenario(id: string) {
	return apiFetch<CostingScenario>(`/costing/${id}/`);
}

export function createCostingScenario(payload: CreateCostingPayload) {
	return apiFetch<CostingScenario>('/costing/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateCostingScenario(id: string, payload: UpdateCostingPayload) {
	return apiFetch<CostingScenario>(`/costing/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteCostingScenario(id: string) {
	return apiFetch<{ status: string }>(`/costing/${id}/`, { method: 'DELETE' });
}

export function recalculateCostingScenario(id: string) {
	return apiFetch<CostingScenario>(`/costing/${id}/recalculate/`, { method: 'POST' });
}

export function costingPdfUrl(id: string) {
	const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
	return `${base}/costing/${id}/pdf/`;
}

// ---------- Exchange rate ----------
export function getExchangeRate() {
	return apiFetch<ExchangeRate>('/costing/exchange-rate/');
}

export function updateExchangeRate(rate: number) {
	return apiFetch<ExchangeRate>('/costing/exchange-rate/', {
		method: 'PUT',
		body: JSON.stringify({ rate })
	});
}

export function refreshExchangeRate() {
	return apiFetch<ExchangeRate>('/costing/exchange-rate/refresh/', { method: 'POST' });
}
