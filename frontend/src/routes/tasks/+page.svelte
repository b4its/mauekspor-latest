<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { projects as seedProjects, workTasks as seedTasks } from '$lib/data/trade';
	import { listTasks } from '$lib/api/tasks';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { assignTask } from '$lib/api/tasks';

	const filters = ['All', 'Open', 'In Progress', 'Blocked', 'Done'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let workTasks = createRemoteList(listTasks, seedTasks);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		workTasks.load();
		projects.load();
	});

	let filteredTasks = $derived(
		workTasks.items.filter(
			(task) =>
				(activeFilter === 'All' || task.status === activeFilter) &&
				[task.title, task.module, task.owner, task.priority, task.status].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let blocked = $derived(workTasks.items.filter((task) => task.status === 'Blocked').length);
	let critical = $derived(workTasks.items.filter((task) => task.priority === 'Critical').length);
	function projectName(id: string) {
		return projects.items.find((project) => project.id === id)?.name ?? id;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			const target = workTasks.items.find((task) => task.status === 'Open') ?? workTasks.items[0];
			if (target) await assignTask(target.id, target.owner ?? 'ops');
			created = true;
		} catch {
			error = 'Gagal membuat tugas.';
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>Tasks | MauEkspor</title>
</svelte:head>

<AppShell title="Tasks" eyebrow="Operational work queue">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Next actions</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Prioritize the work that unblocks export execution.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Convert compliance gaps, supplier evidence, payments, documents, and shipment exceptions into accountable operational tasks.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? 'Task created' : creating ? 'Creating...' : 'Create task'}</Button>
			<Badge variant="destructive">Blocked {blocked}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4"><strong class="block">Task created.</strong><span class="block text-sm text-muted-foreground">Tugas dibuat di backend.</span></div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search task, module, owner..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Total tasks</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{workTasks.items.length}</strong></CardContent>
		</Card>
		<Card>
			<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Critical</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{critical}</strong></CardContent>
		</Card>
		<Card>
			<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Blocked</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{blocked}</strong></CardContent>
		</Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredTasks as task}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/tasks/${task.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3"><Badge variant={toneVariant(statusTone(task.status))}>{task.status}</Badge><strong class="text-sm font-bold">{task.priority}</strong></div>
					<h3 class="mt-4 text-2xl font-bold tracking-tight">{task.title}</h3>
					<p class="mt-2 text-sm text-muted-foreground">{task.module} · {projectName(task.projectId)}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Owner <strong class="mt-1 block text-sm font-bold text-foreground">{task.owner}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Due <strong class="mt-1 block text-sm font-bold text-foreground">{task.due}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Checklist <strong class="mt-1 block text-sm font-bold text-foreground">{task.checklist.filter((item) => item.done).length}/{task.checklist.length}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Priority <strong class="mt-1 block text-sm font-bold text-foreground">{task.priority}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No task matched your search.</div>
		{/each}
	</div>
</AppShell>