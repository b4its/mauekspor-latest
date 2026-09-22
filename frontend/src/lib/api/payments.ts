import { apiFetch } from '$lib/api/client';
import type { Payment } from '$lib/data/trade';

export function listPayments() {
	return apiFetch<Payment[]>('/payments/');
}

export function getPayment(id: string) {
	return apiFetch<Payment>(`/payments/${id}/`);
}

export function markPaymentReceived(id: string) {
	return apiFetch<Payment>(`/payments/${id}/mark-received/`, { method: 'POST' });
}

export function sendPaymentReminder(id: string) {
	return apiFetch<Payment>(`/payments/${id}/send-reminder/`, { method: 'POST' });
}

export function updatePayment(id: string, payload: Partial<Payment>) {
	return apiFetch<Payment>(`/payments/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deletePayment(id: string) {
	return apiFetch<{ status: string; id: string }>(`/payments/${id}/`, { method: 'DELETE' });
}
