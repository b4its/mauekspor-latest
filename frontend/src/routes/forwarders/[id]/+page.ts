import { forwarders as seedForwarders } from '$lib/data/trade';
import type { Forwarder } from '$lib/data/trade';
import { getForwarder } from '$lib/api/forwarders';
import { loadById } from '$lib/api/remote-list.svelte';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }): Promise<{ forwarder: Forwarder }> => {
	const forwarder = await loadById(getForwarder, seedForwarders, params.id);
	if (!forwarder) error(404, 'Forwarder not found');
	return { forwarder };
};