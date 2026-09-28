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

export function updateSupportTicket(id: string, payload: Partial<SupportTicket>) {
	return apiFetch<SupportTicket>(`/support/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteSupportTicket(id: string) {
	return apiFetch<{ status: string; id: string }>(`/support/${id}/`, { method: 'DELETE' });
}


export function batchDeleteSupportTickets(ids: string[]) {
	return apiFetch<{ deleted: string[]; deletedCount: number }>('/support/batch/delete/', {
		method: 'POST',
		body: JSON.stringify({ ids })
	});
}
