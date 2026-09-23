import { apiFetch } from '$lib/api/client';
import type { BuyerRequest } from '$lib/data/trade';

export function listBuyerRequests() { return apiFetch<BuyerRequest[]>('/buyer-requests/'); }
export function getBuyerRequest(id: string) { return apiFetch<BuyerRequest>(`/buyer-requests/${id}/`); }
export function createBuyerRequest(payload: Partial<BuyerRequest>) { return apiFetch<BuyerRequest>('/buyer-requests/', { method: 'POST', body: JSON.stringify(payload) }); }
export function matchBuyerRequest(id: string) { return apiFetch<BuyerRequest>(`/buyer-requests/${id}/match/`, { method: 'POST' }); }
