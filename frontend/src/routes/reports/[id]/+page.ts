import { error } from '@sveltejs/kit';
import { tradeReports as seedReports } from '$lib/data/trade';
import { getReport } from '$lib/api/reports';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const report = await loadById(getReport, seedReports, params.id);
	if (!report) error(404, 'Report not found');
	return { report };
};