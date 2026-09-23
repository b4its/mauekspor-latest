import { error } from '@sveltejs/kit';
import { products as seedProducts } from '$lib/data/trade';
import { getProduct } from '$lib/api/products';
import type { PageLoad } from './$types';

// SSR dimatikan: loader butuh token/cookie auth yang hanya ada di klien.
export const ssr = false;

async function findProduct(id: string) {
	try {
		const res = await getProduct(id);
		return res.data;
	} catch {
		return seedProducts.find((item) => item.id === id);
	}
}

export const load: PageLoad = async ({ params }) => {
	const product = await findProduct(params.id);

	if (!product) {
		error(404, 'Product not found');
	}

	return { product };
};