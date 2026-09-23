import { apiFetch } from '$lib/api/client';
import type { MessageThread } from '$lib/data/trade';

export function listMessages() {
	return apiFetch<MessageThread[]>('/messages/');
}

export function sendMessage(threadId: string, body: string) {
	return apiFetch<MessageThread>(`/messages/${threadId}/send/`, { method: 'POST', body: JSON.stringify({ body }) });
}

export function resolveMessageThread(threadId: string) {
	return apiFetch<MessageThread>(`/messages/${threadId}/resolve/`, { method: 'POST' });
}
