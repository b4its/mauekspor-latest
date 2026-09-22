import { apiFetch } from '$lib/api/client';
import type { SalesOrder } from '$lib/data/trade';

export type CreateOrderPayload = {
	quotationId?: string;
	buyer?: string;
	supplier?: string;
	value?: number;
	incoterm?: string;
	currency?: string;
	paymentTerms?: string;
	deliveryWindow?: string;
	projectId?: string;
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

export function updateOrder(id: string, payload: Partial<SalesOrder>) {
	return apiFetch<SalesOrder>(`/orders/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteOrder(id: string) {
	return apiFetch<{ status: string; id: string }>(`/orders/${id}/`, { method: 'DELETE' });
}
