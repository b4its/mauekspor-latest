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

// ---------- Buyer profiles (role Buyer) ----------
export type BuyerProfile = {
	id?: string;
	companyName: string;
	companyDescription?: string;
	contactInfo?: Record<string, string>;
	preferredProductCategories?: string[];
	preferredProductCategoriesDescription?: string;
	sourceCountries?: string[];
	sourceCountriesDescription?: string;
	businessType?: string;
	businessTypeDescription?: string;
	annualImportVolume?: string;
	annualImportVolumeDescription?: string;
};

export function createBuyerProfile(payload: Partial<BuyerProfile>) {
	return apiFetch<BuyerProfile>('/buyers/profile/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function getMyBuyerProfile() {
	return apiFetch<BuyerProfile>('/buyers/profile/me/');
}

export function updateBuyerProfile(id: string, payload: Partial<BuyerProfile>) {
	return apiFetch<BuyerProfile>(`/buyers/profile/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}
