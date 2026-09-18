import { apiFetch } from '$lib/api/client';

export type AdminTable = {
	name: string;
	count: number;
};

export type AdminRecord = Record<string, unknown> & { id: string };

export function listAdminTables() {
	return apiFetch<AdminTable[]>('/admin/tables/');
}

export function listAdminRecords(table: string, params: { search?: string; limit?: number; offset?: number } = {}) {
	const qs = new URLSearchParams();
	if (params.search) qs.set('search', params.search);
	if (params.limit) qs.set('limit', String(params.limit));
	if (params.offset) qs.set('offset', String(params.offset));
	const q = qs.toString();
	return apiFetch<AdminRecord[]>(`/admin/data/${table}/${q ? `?${q}` : ''}`);
}

export function getAdminRecord(table: string, id: string) {
	return apiFetch<AdminRecord>(`/admin/data/${table}/${id}/`);
}

export function createAdminRecord(table: string, payload: Record<string, unknown>) {
	return apiFetch<AdminRecord>(`/admin/data/${table}/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateAdminRecord(table: string, id: string, payload: Record<string, unknown>) {
	return apiFetch<AdminRecord>(`/admin/data/${table}/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteAdminRecord(table: string, id: string) {
	return apiFetch<{ status: string }>(`/admin/data/${table}/${id}/`, { method: 'DELETE' });
}