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
	return apiFetch<AdminRecord[]>(q ? `/admin/data/${table}/?${q}` : `/admin/data/${table}/`);
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

export type AiStatus = {
	mode: string;
	health: string;
	using_remote: boolean;
	using_mock: boolean;
	configured_provider?: string;
};

export type AiTestResult = {
	response?: string;
	ai_mode?: string;
	ai_health?: string;
	success: boolean;
	error?: string;
};

export function getAiStatus() {
	return apiFetch<AiStatus>('/ai/status/');
}

export function testAi() {
	return apiFetch<AiTestResult>('/ai/test/', { method: 'POST' });
}