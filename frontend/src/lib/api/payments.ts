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
