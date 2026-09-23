import { apiFetch } from '$lib/api/client';
import type { RFQ } from '$lib/data/trade';

export type CreateRFQPayload = {
	buyer: string;
	product: string;
	destination: string;
	quantity: string;
	incoterm: string;
	deadline: string;
};

export function listRFQs() {
	return apiFetch<RFQ[]>('/rfqs/');
}

export function getRFQ(id: string) {
	return apiFetch<RFQ>(`/rfqs/${id}/`);
}

export function createRFQ(payload: CreateRFQPayload) {
	return apiFetch<RFQ>('/rfqs/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function shortlistRFQMatch(id: string, supplier: string) {
	return apiFetch<RFQ>(`/rfqs/${id}/shortlist/`, {
		method: 'POST',
		body: JSON.stringify({ supplier })
	});
}
