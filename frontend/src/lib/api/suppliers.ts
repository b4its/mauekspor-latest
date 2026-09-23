import { apiFetch } from '$lib/api/client';
import type { Supplier } from '$lib/data/trade';

export function listSuppliers() {
	return apiFetch<Supplier[]>('/suppliers/');
}

export function getSupplier(id: string) {
	return apiFetch<Supplier>(`/suppliers/${id}/`);
}

export function verifySupplier(id: string) {
	return apiFetch<Supplier>(`/suppliers/${id}/verify/`, { method: 'POST' });
}

export function requestSupplierEvidence(id: string) {
	return apiFetch<Supplier>(`/suppliers/${id}/request-evidence/`, { method: 'POST' });
}
