import { error } from '@sveltejs/kit';
import { educationalLessons, educationalModules as seedModules } from '$lib/data/trade';
import { getEducationalModule } from '$lib/api/educational';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const module = await loadById(getEducationalModule, seedModules, params.id);
	if (!module) error(404, 'Module not found');

	// Pelajaran dari backend (artikel modul) bila tersedia, fallback ke seed lessons
	const articles = (module.articles ?? []) as { id: string; title: string; content?: string }[];
	let lessons;
	if (articles.length > 0) {
		lessons = articles.map((article, index) => ({
			id: article.id,
			moduleId: module.id,
			title: article.title,
			kind: 'Reading',
			duration: '5 min',
			content: article.content ?? '',
			keyPoints: [],
			completed: false
		}));
	} else {
		lessons = educationalLessons.filter((lesson) => lesson.moduleId === module.id);
	}

	return { module, lessons };
};
