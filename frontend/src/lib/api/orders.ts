import { apiFetch } from '$lib/api/client';
import type { SalesOrder } from '$lib/data/trade';

export type CreateOrderPayload = {
	quotationId: string;
	paymentTerms: string;
	deliveryWindow: string;
};

export function listOrders() {
	return apiFetch<SalesOrder[]>('/orders/');
}

export function getOrder(id: string) {
	return apiFetch<SalesOrder>(`/orders/${id}/`);
}

export function createOrder(payload: CreateOrderPayload) {
	return apiFetch<SalesOrder>('/orders/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function confirmOrder(id: string) {
	return apiFetch<SalesOrder>(`/orders/${id}/confirm/`, { method: 'POST' });
}
