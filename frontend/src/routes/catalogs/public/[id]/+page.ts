import { error } from '@sveltejs/kit';
import { getPublicCatalog } from '$lib/api/catalogs';
import type { PageLoad } from './$types';

// SSR dimatikan: loader memakai apiFetch relatif (butuh origin klien).
export const ssr = false;

export const load: PageLoad = async ({ params }) => {
	try {
		const res = await getPublicCatalog(params.id);
		return { catalog: res.data, forbidden: false };
	} catch {
		// Endpoint publik: 404 berarti tidak ada / belum Published.
		error(404, 'Published catalog not found');
	}
};
