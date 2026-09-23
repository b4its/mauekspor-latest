import { error } from '@sveltejs/kit';
import { userAccounts as seedUsers } from '$lib/data/trade';
import { getUser } from '$lib/api/users';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const user = await loadById(getUser, seedUsers, params.id);
	if (!user) error(404, 'User not found');
	return { user };
};