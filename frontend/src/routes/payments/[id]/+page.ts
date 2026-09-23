import { error } from '@sveltejs/kit';
import { orders as seedOrders, payments as seedPayments } from '$lib/data/trade';
import { getPayment } from '$lib/api/payments';
import { getOrder } from '$lib/api/orders';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const payment = await loadById(getPayment, seedPayments, params.id);
	if (!payment) error(404, 'Payment not found');
	return {
		payment,
		order: payment.orderId ? await loadById(getOrder, seedOrders, payment.orderId).catch(() => undefined) : undefined
	};
};