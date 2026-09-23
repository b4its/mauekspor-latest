import { error } from '@sveltejs/kit';
import { products as seedProducts } from '$lib/data/trade';
import { getProduct } from '$lib/api/products';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const product = await loadById(getProduct, seedProducts, params.id);
	if (!product) error(404, 'Product not found');
	return { product };
};