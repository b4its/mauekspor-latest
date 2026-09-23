import { error } from '@sveltejs/kit';
import { marketInsights as seedMarkets, products as seedProducts, projects as seedProjects } from '$lib/data/trade';
import { getMarketInsight } from '$lib/api/markets';
import { getProduct } from '$lib/api/products';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const market = await loadById(getMarketInsight, seedMarkets, params.id);
	if (!market) error(404, 'Market insight not found');
	return {
		market,
		project: market.projectId ? await loadById(getTradeProject, seedProjects, market.projectId).catch(() => undefined) : undefined,
		product: market.productId ? await loadById(getProduct, seedProducts, market.productId).catch(() => undefined) : undefined
	};
};