import { error } from '@sveltejs/kit';
import { buyers as seedBuyers, projects as seedProjects } from '$lib/data/trade';
import { getBuyer } from '$lib/api/buyers';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const buyer = await loadById(getBuyer, seedBuyers, params.id);
	if (!buyer) error(404, 'Buyer not found');
	const linkedProjects = await Promise.all(
		(buyer.projectIds ?? []).map((id) => loadById(getTradeProject, seedProjects, id).catch(() => undefined))
	);
	return {
		buyer,
		linkedProjects: linkedProjects.filter((project): project is NonNullable<typeof project> => !!project)
	};
};