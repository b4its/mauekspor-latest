import { apiFetch, ApiError, type ApiErrorBody } from '$lib/api/client';
import type { FileAsset } from '$lib/data/trade';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8015/api/v1';

export function listFiles() {
	return apiFetch<FileAsset[]>('/files/');
}

export function uploadFileAsset(payload: Pick<FileAsset, 'name' | 'type' | 'projectId'>) {
	return apiFetch<FileAsset>('/files/', { method: 'POST', body: JSON.stringify(payload) });
}

export function verifyFileAsset(id: string) {
	return apiFetch<FileAsset>(`/files/${id}/verify/`, { method: 'POST' });
}

export async function uploadFileBinary(file: File, type: string, projectId: string, tags: string[]) {
	const form = new FormData();
	form.append('file', file);
	form.append('type_', type);
	form.append('project_id', projectId);
	form.append('tags', tags.join(','));
	const response = await fetch(`${API_BASE_URL}/files/upload/`, { method: 'POST', body: form, credentials: 'include' });
	const body = response.headers.get('content-type')?.includes('application/json')
		? await response.json()
		: null;
	if (!response.ok) {
		throw new ApiError(response.status, body as ApiErrorBody | null);
	}
	return body as { data: FileAsset; meta?: Record<string, unknown> };
}

export function fileDownloadUrl(id: string) {
	return `${API_BASE_URL}/files/${id}/download/`;
}