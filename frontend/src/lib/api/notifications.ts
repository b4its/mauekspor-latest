import { apiFetch } from '$lib/api/client';
import type { NotificationItem } from '$lib/data/trade';

export function listNotifications() {
	return apiFetch<NotificationItem[]>('/notifications/');
}

export function markNotificationRead(id: string) {
	return apiFetch<NotificationItem>(`/notifications/${id}/read/`, { method: 'POST' });
}

export function archiveNotification(id: string) {
	return apiFetch<NotificationItem>(`/notifications/${id}/archive/`, { method: 'POST' });
}

export function deleteNotification(id: string) {
	return apiFetch<{ status: string; id: string }>(`/notifications/${id}/`, { method: 'DELETE' });
}

export function batchDeleteNotifications(ids: string[]) {
	return apiFetch<{ deleted: string[]; deletedCount: number }>('/notifications/batch/delete/', {
		method: 'POST',
		body: JSON.stringify({ ids })
	});
}
