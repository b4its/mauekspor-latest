import { error } from '@sveltejs/kit';
import { exportAnalyses as seedAnalyses, products as seedProducts } from '$lib/data/trade';
import { getExportAnalysis } from '$lib/api/export-analysis';
import { getProduct } from '$lib/api/products';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const analysis = await loadById(getExportAnalysis, seedAnalyses, params.id);
	if (!analysis) error(404, 'Export analysis not found');
	const product = analysis.productId
		? await loadById(getProduct, seedProducts, analysis.productId).catch(() => undefined)
		: undefined;
	return { analysis, product };
};
