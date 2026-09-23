import { error } from '@sveltejs/kit';
import { exportAnalyses as seedAnalyses } from '$lib/data/trade';
import { getExportAnalysis } from '$lib/api/export-analysis';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const analysis = await loadById(getExportAnalysis, seedAnalyses, params.id);
	if (!analysis) error(404, 'Export analysis not found');
	return { analysis };
};