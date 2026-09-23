import { error } from '@sveltejs/kit';
import { projects as seedProjects, workTasks as seedTasks } from '$lib/data/trade';
import { getTask } from '$lib/api/tasks';
import { getTradeProject } from '$lib/api/trade-projects';
import { loadById } from '$lib/api/remote-list.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const task = await loadById(getTask, seedTasks, params.id);
	if (!task) error(404, 'Task not found');
	return {
		task,
		project: await loadById(getTradeProject, seedProjects, task.projectId).catch(() => undefined)
	};
};