import { error } from '@sveltejs/kit';
import { projects as seedProjects, rfqs as seedRFQs } from '$lib/data/trade';
import { getRFQ } from '$lib/api/rfq';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const rfq = await loadById(getRFQ, seedRFQs, params.id);
	if (!rfq) error(404, 'RFQ not found');
	return {
		rfq,
		project: await loadById(getTradeProject, seedProjects, rfq.projectId).catch(() => undefined)
	};
};