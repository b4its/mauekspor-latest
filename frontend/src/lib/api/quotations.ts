import { apiFetch } from '$lib/api/client';
import type { Quotation } from '$lib/data/trade';

export type CreateQuotationPayload = {
	rfqId: string;
	incoterm: string;
	value: number;
	currency: 'USD' | 'IDR';
	validUntil: string;
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
