import { error } from '@sveltejs/kit';
import { products as seedProducts, suppliers as seedSuppliers } from '$lib/data/trade';
import { getSupplier } from '$lib/api/suppliers';
import { getProduct } from '$lib/api/products';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const supplier = await loadById(getSupplier, seedSuppliers, params.id);
	if (!supplier) error(404, 'Supplier not found');
	const linkedProducts = await Promise.all(
		(supplier.productIds ?? []).map((id) => loadById(getProduct, seedProducts, id).catch(() => undefined))
	);
	return {
		supplier,
		linkedProducts: linkedProducts.filter((product): product is NonNullable<typeof product> => !!product)
	};
};