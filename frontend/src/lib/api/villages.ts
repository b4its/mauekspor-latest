import { apiFetch } from '$lib/api/client';

export type Village = {
	id: string;
	name: string;
	region: string;
	province: string;
	flagshipCommodity: string;
	commodityGroup: 'pertanian' | 'perikanan' | 'kerajinan' | string;
	production: string;
	organization: string;
	readiness: number;
	status: 'Siap Ekspor' | 'Butuh Pendampingan' | string;
	createdAt?: string;
	products?: Array<Record<string, unknown>>;
};

export function listVillages(params: { search?: string; province?: string; readiness?: string } = {}) {
	const qs = new URLSearchParams();
	if (params.search) qs.set('search', params.search);
	if (params.province) qs.set('province', params.province);
	if (params.readiness) qs.set('readiness', params.readiness);
	const q = qs.toString();
	return apiFetch<Village[]>(q ? `/villages/?${q}` : '/villages/');
}

export function getVillage(villageId: string) {
	return apiFetch<Village>(`/villages/${villageId}/`);
}

export function createVillage(payload: Partial<Village>) {
	return apiFetch<Village>('/villages/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateVillage(villageId: string, payload: Partial<Village>) {
	return apiFetch<Village>(`/villages/${villageId}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteVillage(villageId: string) {
	return apiFetch<{ status: string; id: string }>(`/villages/${villageId}/`, {
		method: 'DELETE'
	});
}
