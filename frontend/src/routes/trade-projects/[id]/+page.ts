import { error } from '@sveltejs/kit';
import { projects as seedProjects } from '$lib/data/trade';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const project = await loadById(getTradeProject, seedProjects, params.id);
	if (!project) error(404, 'Trade project not found');
	return { project };
};