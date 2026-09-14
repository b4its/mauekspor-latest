import { error } from '@sveltejs/kit';
import { educationalArticles as seedArticles } from '$lib/data/trade';
import { getEducationalArticle } from '$lib/api/educational-articles';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const article = await loadById(getEducationalArticle, seedArticles, params.id);
	if (!article) error(404, 'Article not found');
	return { article };
};