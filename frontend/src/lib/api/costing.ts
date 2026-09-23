import { apiFetch } from '$lib/api/client';
import type { CostingScenario } from '$lib/data/trade';

export type CreateCostingPayload = {
	title: string;
	projectId: string;
	productId: string;
	incoterm: CostingScenario['incoterm'];
	margin: number;
	destination: string;
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

export function recalculateCostingScenario(id: string) {
	return apiFetch<CostingScenario>(`/costing/${id}/recalculate/`, { method: 'POST' });
}
