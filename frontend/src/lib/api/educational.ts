import { apiFetch } from '$lib/api/client';
import type { EducationalModule } from '$lib/data/trade';

export type EducationalModulePayload = {
	title: string;
	description?: string;
	order_index?: number;
};

export function listEducationalModules() {
	return apiFetch<EducationalModule[]>('/educational/');
}

export function listEducationalModulesV2() {
	return apiFetch<EducationalModule[]>('/educational/modules/');
}

export function getEducationalModule(id: string) {
	return apiFetch<EducationalModule>(`/educational/modules/${id}/`);
}

export function createEducationalModule(payload: EducationalModulePayload) {
	return apiFetch<EducationalModule>('/educational/modules/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateEducationalModule(id: string, payload: EducationalModulePayload) {
	return apiFetch<EducationalModule>(`/educational/modules/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteEducationalModule(id: string) {
	return apiFetch<{ status: string }>(`/educational/modules/${id}/`, { method: 'DELETE' });
}

export function publishEducationalModule(id: string) {
	return apiFetch<EducationalModule>(`/educational/${id}/publish/`, { method: 'POST' });
}
