import { error } from '@sveltejs/kit';
import { educationalLessons, educationalModules as seedModules } from '$lib/data/trade';
import { listEducationalModules } from '$lib/api/educational';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

const getEducationalModule = async (id: string) => {
	const res = await listEducationalModules();
	const module = res.data.find((item) => item.id === id);
	if (!module) throw new Error('not found');
	return { data: module };
};

export const load: PageLoad = async ({ params }) => {
	const module = await loadById(getEducationalModule, seedModules, params.id);
	if (!module) error(404, 'Module not found');

	const lessons = educationalLessons.filter((lesson) => lesson.moduleId === module.id);
	return { module, lessons };
};