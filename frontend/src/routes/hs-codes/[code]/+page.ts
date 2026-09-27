import type { PageLoad } from './$types';

// Konsisten dengan loader detail lain: halaman ini memuat data di klien karena
// bergantung pada token/cookie auth. Tanpa ini, SSR dapat merender tanpa data.
export const ssr = false;

export const load: PageLoad = async ({ params }) => {
	return { code: params.code };
};
