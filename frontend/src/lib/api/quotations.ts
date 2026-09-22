import { apiFetch } from '$lib/api/client';
import type { Quotation } from '$lib/data/trade';

export type CreateQuotationPayload = {
	rfqId?: string;
	buyer?: string;
	supplier?: string;
	productId?: string;
	value?: number;
	currency?: string;
	incoterm?: string;
	validUntil?: string;
	margin?: number;
};

export function listQuotations() {
	return apiFetch<Quotation[]>('/quotations/');
}

export function getQuotation(id: string) {
	return apiFetch<Quotation>(`/quotations/${id}/`);
}

export function createQuotation(payload: CreateQuotationPayload) {
	return apiFetch<Quotation>('/quotations/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function acceptQuotation(id: string) {
	return apiFetch<Quotation>(`/quotations/${id}/accept/`, { method: 'POST' });
}

export function updateQuotation(id: string, payload: Partial<Quotation>) {
	return apiFetch<Quotation>(`/quotations/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteQuotation(id: string) {
	return apiFetch<{ status: string; id: string }>(`/quotations/${id}/`, { method: 'DELETE' });
}
