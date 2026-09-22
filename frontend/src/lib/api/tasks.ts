import { apiFetch } from '$lib/api/client';
import type { WorkTask } from '$lib/data/trade';

export function listTasks() {
	return apiFetch<WorkTask[]>('/tasks/');
}

export function getTask(id: string) {
	return apiFetch<WorkTask>(`/tasks/${id}/`);
}

export function completeTask(id: string) {
	return apiFetch<WorkTask>(`/tasks/${id}/complete/`, { method: 'POST' });
}

export function assignTask(id: string, owner: string) {
	return apiFetch<WorkTask>(`/tasks/${id}/assign/`, {
		method: 'POST',
		body: JSON.stringify({ owner })
	});
}

export function updateTask(id: string, payload: Partial<WorkTask>) {
	return apiFetch<WorkTask>(`/tasks/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteTask(id: string) {
	return apiFetch<{ status: string; id: string }>(`/tasks/${id}/`, { method: 'DELETE' });
}
