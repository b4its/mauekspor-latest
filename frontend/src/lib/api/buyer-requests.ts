import { apiFetch } from '$lib/api/client';
import type { BuyerRequest } from '$lib/data/trade';

export type CreateBuyerRequestPayload = {
	subject: string;
	destination: string;
	quantity: string;
	buyerId?: string;
	productId?: string;
	deadline?: string;
	requirements?: string[];
	product_category?: string;
	hs_code_target?: string;
	spec_requirements?: string;
	target_volume?: number;
	keyword_tags?: string[];
	min_rank_required?: number;
};

export type MatchedItem = {
	catalogId?: string;
	productId?: string;
	product?: string;
	match_score: number;
	match_reasons: string[];
	umkm_id?: string;
	umkm_name?: string;
	catalogTitle?: string;
	contactInfo?: { phone?: string; email?: string };
};

export function listBuyerRequests() {
	return apiFetch<BuyerRequest[]>('/buyer-requests/');
}

export function getBuyerRequest(id: string) {
	return apiFetch<BuyerRequest>(`/buyer-requests/${id}/`);
}

export function createBuyerRequest(payload: CreateBuyerRequestPayload) {
	return apiFetch<BuyerRequest>('/buyer-requests/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateBuyerRequest(id: string, payload: Partial<CreateBuyerRequestPayload>) {
	return apiFetch<BuyerRequest>(`/buyer-requests/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteBuyerRequest(id: string) {
	return apiFetch<{ status: string }>(`/buyer-requests/${id}/`, { method: 'DELETE' });
}

export function matchBuyerRequest(id: string) {
	return apiFetch<BuyerRequest>(`/buyer-requests/${id}/match/`, { method: 'POST' });
}

export function updateBuyerRequestStatus(
	id: string,
	payload: { status: string; selected_catalog?: string; umkm?: string }
) {
	return apiFetch<BuyerRequest>(`/buyer-requests/${id}/status/`, {
		method: 'PATCH',
		body: JSON.stringify(payload)
	});
}

export function getMatchedCatalogs(id: string) {
	return apiFetch<MatchedItem[]>(`/buyer-requests/${id}/matched-catalogs/`);
}

export function getMatchedUmkm(id: string) {
	return apiFetch<MatchedItem[]>(`/buyer-requests/${id}/matched-umkm/`);
}
