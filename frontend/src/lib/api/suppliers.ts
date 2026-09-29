import { apiFetch } from '$lib/api/client';
import type { Supplier } from '$lib/data/trade';

export function listSuppliers() {
	return apiFetch<Supplier[]>('/suppliers/');
}

export function getSupplier(id: string) {
	return apiFetch<Supplier>(`/suppliers/${id}/`);
}

export type CreateSupplierPayload = {
	name: string;
	location?: string;
	category?: string;
	capacity?: string;
	leadTime?: string;
	contact?: string;
	productIds?: string[];
};

export function createSupplier(payload: CreateSupplierPayload) {
	return apiFetch<Supplier>('/suppliers/', { method: 'POST', body: JSON.stringify(payload) });
}

/** Verifikasi supplier wajib menyertakan bukti berkas (`fileId`). */
export function verifySupplier(id: string, evidence: { fileId: string; note?: string }) {
	return apiFetch<Supplier>(`/suppliers/${id}/verify/`, {
		method: 'POST',
		body: JSON.stringify({ fileId: evidence.fileId, note: evidence.note ?? '' })
	});
}

export function requestSupplierEvidence(id: string) {
	return apiFetch<Supplier>(`/suppliers/${id}/request-evidence/`, { method: 'POST' });
}

export function updateSupplier(id: string, payload: Partial<Supplier>) {
	return apiFetch<Supplier>(`/suppliers/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteSupplier(id: string) {
	return apiFetch<{ status: string; id: string }>(`/suppliers/${id}/`, { method: 'DELETE' });
}


export function batchDeleteSuppliers(ids: string[]) {
	return apiFetch<{ deleted: string[]; deletedCount: number }>('/suppliers/batch/delete/', {
		method: 'POST',
		body: JSON.stringify({ ids })
	});
}
