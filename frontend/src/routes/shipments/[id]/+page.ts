import { error } from '@sveltejs/kit';
import { projects as seedProjects, shipments as seedShipments } from '$lib/data/trade';
import { getShipment } from '$lib/api/shipments';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const shipment = await loadById(getShipment, seedShipments, params.id);
	if (!shipment) error(404, 'Shipment not found');
	return {
		shipment,
		project: await loadById(getTradeProject, seedProjects, shipment.projectId).catch(() => undefined)
	};
};