import { apiFetch } from '$lib/api/client';
import type { SupportTicket } from '$lib/data/trade';

export function listSupportTickets() {
	return apiFetch<SupportTicket[]>('/support/');
}

export function createSupportTicket(payload: Pick<SupportTicket, 'subject' | 'category' | 'description'>) {
	return apiFetch<SupportTicket>('/support/', { method: 'POST', body: JSON.stringify(payload) });
}

export function resolveSupportTicket(id: string) {
	return apiFetch<SupportTicket>(`/support/${id}/resolve/`, { method: 'POST' });
}
