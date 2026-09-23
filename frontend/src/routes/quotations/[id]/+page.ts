import { error } from '@sveltejs/kit';
import { projects as seedProjects, quotations as seedQuotations, rfqs as seedRFQs } from '$lib/data/trade';
import { getQuotation } from '$lib/api/quotations';
import { getTradeProject } from '$lib/api/trade-projects';
import { getRFQ } from '$lib/api/rfq';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const quotation = await loadById(getQuotation, seedQuotations, params.id);
	if (!quotation) error(404, 'Quotation not found');
	return {
		quotation,
		project: await loadById(getTradeProject, seedProjects, quotation.projectId).catch(() => undefined),
		rfq: quotation.rfqId ? await loadById(getRFQ, seedRFQs, quotation.rfqId).catch(() => undefined) : undefined
	};
};