import { error } from '@sveltejs/kit';
import { costingScenarios as seedScenarios, products as seedProducts, projects as seedProjects } from '$lib/data/trade';
import { getCostingScenario } from '$lib/api/costing';
import { getProduct } from '$lib/api/products';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const scenario = await loadById(getCostingScenario, seedScenarios, params.id);
	if (!scenario) error(404, 'Costing scenario not found');
	return {
		scenario,
		project: await loadById(getTradeProject, seedProjects, scenario.projectId).catch(() => undefined),
		product: scenario.productId ? await loadById(getProduct, seedProducts, scenario.productId).catch(() => undefined) : undefined
	};
};