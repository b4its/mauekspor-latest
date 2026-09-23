import { error } from '@sveltejs/kit';
import { complianceRequirements as seedRequirements, products as seedProducts, projects as seedProjects } from '$lib/data/trade';
import { getComplianceRequirement } from '$lib/api/compliance';
import { getProduct } from '$lib/api/products';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const requirement = await loadById(getComplianceRequirement, seedRequirements, params.id);
	if (!requirement) error(404, 'Compliance requirement not found');
	return {
		requirement,
		project: await loadById(getTradeProject, seedProjects, requirement.projectId).catch(() => undefined),
		product: requirement.productId ? await loadById(getProduct, seedProducts, requirement.productId).catch(() => undefined) : undefined
	};
};