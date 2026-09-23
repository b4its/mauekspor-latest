import { error } from '@sveltejs/kit';
import { orders as seedOrders, projects as seedProjects, quotations as seedQuotations } from '$lib/data/trade';
import { getOrder } from '$lib/api/orders';
import { getTradeProject } from '$lib/api/trade-projects';
import { getQuotation } from '$lib/api/quotations';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const order = await loadById(getOrder, seedOrders, params.id);
	if (!order) error(404, 'Order not found');
	return {
		order,
		project: await loadById(getTradeProject, seedProjects, order.projectId).catch(() => undefined),
		quotation: order.quotationId ? await loadById(getQuotation, seedQuotations, order.quotationId).catch(() => undefined) : undefined
	};
};