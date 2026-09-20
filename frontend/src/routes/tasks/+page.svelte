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
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { assignTask } from '$lib/api/tasks';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

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
			error = t('Gagal membuat tugas.');
		} finally {
			creating = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
	let pagedItems = $derived(paginate(filteredTasks ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredTasks?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Tugas')} | MauEkspor</title>
</svelte:head>

<AppShell title="Tasks" eyebrow={t('Operational work queue')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Next actions')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Prioritize the work that unblocks export execution.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Convert compliance gaps, supplier evidence, payments, documents, and shipment exceptions into accountable operational tasks.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? t('Task created') : creating ? t('Creating...') : t('Create task')}</Button>
			<Badge variant="destructive">{t('Blocked')} {blocked}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if workTasks.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{workTasks.error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4"><strong class="block">{t('Task created.')}</strong><span class="block text-sm text-muted-foreground">{t('Tugas dibuat di backend.')}</span></div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search task, module, owner...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total tasks')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{workTasks.items.length}</strong></CardContent>
		</Card>
		<Card>
			<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Critical')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{critical}</strong></CardContent>
		</Card>
		<Card>
			<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Blocked')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{blocked}</strong></CardContent>
		</Card>
	</div>

	{#if workTasks.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-5 w-14" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as task}
				<Card class="transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/tasks/${task.id}`} class="block h-full p-5 no-underline">
						<div class="flex items-center justify-between gap-3"><Badge variant={toneVariant(statusTone(task.status))}>{task.status}</Badge><strong class="text-sm font-bold">{task.priority}</strong></div>
						<h3 class="mt-4 text-2xl font-bold tracking-tight">{task.title}</h3>
						<p class="mt-2 text-sm text-muted-foreground">{task.module} · {projectName(task.projectId)}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{task.owner}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Due')} <strong class="mt-1 block text-sm font-bold text-foreground">{task.due}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Checklist')} <strong class="mt-1 block text-sm font-bold text-foreground">{(task.checklist ?? []).filter((item) => item.done).length}/{task.checklist?.length ?? 0}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Priority')} <strong class="mt-1 block text-sm font-bold text-foreground">{task.priority}</strong></div>
						</div>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No task matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredTasks?.length ?? 0} />

</AppShell>