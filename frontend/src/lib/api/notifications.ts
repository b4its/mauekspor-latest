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
