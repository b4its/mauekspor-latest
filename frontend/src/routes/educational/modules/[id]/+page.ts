import { error } from '@sveltejs/kit';
import { educationalLessons, educationalModules as seedModules, type EducationalLesson } from '$lib/data/trade';
import { getEducationalModule } from '$lib/api/educational';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

// SSR dimatikan: loader butuh token/cookie auth yang hanya ada di klien.
export const ssr = false;

export const load: PageLoad = async ({ params }) => {
	const module = await loadById(getEducationalModule, seedModules, params.id);
	if (!module) error(404, 'Module not found');

	// Prioritas pelajaran: (1) educational_lessons dari backend (punya kind
	// Video/Reading/Quiz + materi), (2) pelajaran seed lokal, (3) artikel modul.
	const backendLessons = module.lessonsList;
	let lessons: EducationalLesson[];
	if (Array.isArray(backendLessons) && backendLessons.length > 0) {
		lessons = backendLessons.map((lesson) => ({
			id: String(lesson.id),
			moduleId: module.id,
			title: String(lesson.title ?? ''),
			kind: (lesson.kind as 'Video' | 'Reading' | 'Quiz') ?? 'Reading',
			duration: String(lesson.duration ?? '5 min'),
			content: String(lesson.content ?? ''),
			keyPoints: (lesson.keyPoints as string[]) ?? [],
			completed: false
		}));
	} else {
		const articles = (module.articles ?? []) as { id: string; title: string; content?: string }[];
		const seeded = educationalLessons.filter((lesson) => lesson.moduleId === module.id);
		if (seeded.length > 0) {
			lessons = seeded;
		} else if (articles.length > 0) {
			lessons = articles.map((article) => ({
				id: article.id,
				moduleId: module.id,
				title: article.title,
				kind: 'Reading' as const,
				duration: '5 min',
				content: article.content ?? '',
				keyPoints: [],
				completed: false
			}));
		} else {
			lessons = [];
		}
	}

	return { module, lessons };
};
