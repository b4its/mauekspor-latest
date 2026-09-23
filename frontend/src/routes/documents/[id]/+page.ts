import { error } from '@sveltejs/kit';
import { projects as seedProjects, tradeDocuments as seedDocuments } from '$lib/data/trade';
import { getTradeDocument } from '$lib/api/documents';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const document = await loadById(getTradeDocument, seedDocuments, params.id);
	if (!document) error(404, 'Trade document not found');
	return {
		document,
		project: await loadById(getTradeProject, seedProjects, document.projectId).catch(() => undefined)
	};
};