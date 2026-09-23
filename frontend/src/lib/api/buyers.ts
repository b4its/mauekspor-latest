import { apiFetch } from '$lib/api/client';
import type { Buyer, Catalog } from '$lib/data/trade';

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

// ---------- Buyer export portal (katalog per negara asal pembeli) ----------
export type BuyerPortalItem = Catalog & {
	productName?: string;
	productOrigin?: string;
	relevanceScore?: number;
	matchedCountry?: string;
};

export type BuyerPortalMeta = {
	countries?: string[];
	detectedCountry?: string;
	total?: number;
	publishedTotal?: number;
};

export type BuyerPortalResult = {
	data: BuyerPortalItem[];
	meta: BuyerPortalMeta;
};

export function listBuyerPortal(params: { country?: string; search?: string; buyerId?: string } = {}): Promise<BuyerPortalResult> {
	const q = new URLSearchParams();
	if (params.country) q.set('country', params.country);
	if (params.search) q.set('search', params.search);
	if (params.buyerId) q.set('buyer_id', params.buyerId);
	const qs = q.toString();
	return apiFetch<BuyerPortalItem[]>(`/buyers/portal/${qs ? `?${qs}` : ''}`).then((res) => ({
		data: Array.isArray(res.data) ? res.data : [],
		meta: (res.meta ?? {}) as BuyerPortalMeta
	}));
}

