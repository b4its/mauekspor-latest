import { error } from '@sveltejs/kit';
import { educationalArticles as seedArticles } from '$lib/data/trade';
import { listEducationalArticles } from '$lib/api/educational-articles';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

const getEducationalArticle = async (id: string) => {
	const res = await listEducationalArticles();
	const article = res.data.find((item) => item.id === id);
	if (!article) throw new Error('not found');
	return { data: article };
};

export const load: PageLoad = async ({ params }) => {
	const article = await loadById(getEducationalArticle, seedArticles, params.id);
	if (!article) error(404, 'Article not found');
	return { article };
};