import { apiFetch } from '$lib/api/client';
import type { Buyer } from '$lib/data/trade';

export type CreateBuyerPayload = {
	name: string;
	country: string;
	segment: string;
	interestedProducts: string[];
};

export function listBuyers() {
	return apiFetch<Buyer[]>('/buyers/');
}

export function getBuyer(id: string) {
	return apiFetch<Buyer>(`/buyers/${id}/`);
}

export function createBuyer(payload: CreateBuyerPayload) {
	return apiFetch<Buyer>('/buyers/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function qualifyBuyer(id: string) {
	return apiFetch<Buyer>(`/buyers/${id}/qualify/`, { method: 'POST' });
}

export function logBuyerContact(id: string, note: string) {
	return apiFetch<Buyer>(`/buyers/${id}/contacts/`, {
		method: 'POST',
		body: JSON.stringify({ note })
	});
}
