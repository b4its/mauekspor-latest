import { error } from '@sveltejs/kit';
import { catalogs as seedCatalogs, products as seedProducts, projects as seedProjects } from '$lib/data/trade';
import { getCatalog } from '$lib/api/catalogs';
import { getProduct } from '$lib/api/products';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const catalog = await loadById(getCatalog, seedCatalogs, params.id);
	if (!catalog) error(404, 'Catalog not found');
	return {
		catalog,
		product: catalog.productId ? await loadById(getProduct, seedProducts, catalog.productId).catch(() => undefined) : undefined,
		project: catalog.projectId ? await loadById(getTradeProject, seedProjects, catalog.projectId).catch(() => undefined) : undefined
	};
};