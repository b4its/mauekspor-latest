import { error } from '@sveltejs/kit';
import { buyerRequests as seedRequests, buyers as seedBuyers, products as seedProducts } from '$lib/data/trade';
import { getBuyerRequest } from '$lib/api/buyer-requests';
import { getBuyer } from '$lib/api/buyers';
import { getProduct } from '$lib/api/products';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const request = await loadById(getBuyerRequest, seedRequests, params.id);
	if (!request) error(404, 'Buyer request not found');
	return {
		request,
		buyer: await loadById(getBuyer, seedBuyers, request.buyerId).catch(() => undefined),
		product: await loadById(getProduct, seedProducts, request.productId).catch(() => undefined)
	};
};