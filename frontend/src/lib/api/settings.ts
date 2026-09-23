import { apiFetch } from '$lib/api/client';

export type WorkspaceSettings = {
	companyName: string;
	country: string;
	entityType: string;
	nib: string;
	taxId: string;
	currency: string;
	language: string;
	notifications: boolean;
	security?: { sessionType: string };
	updatedAt?: string;
};

export function getSettings() {
	return apiFetch<WorkspaceSettings>('/settings/');
}

export function updateSettings(payload: Partial<WorkspaceSettings>) {
	return apiFetch<WorkspaceSettings>('/settings/', {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}
