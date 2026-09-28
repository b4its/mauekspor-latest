<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { projects as seedProjects, workTasks as seedTasks, type WorkTask } from '$lib/data/trade';
	import { listTasks, createTask, completeTask, deleteTask } from '$lib/api/tasks';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { page } from '$app/state';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';
import Pagination from '$lib/components/Pagination.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
import SortSelect from '$lib/components/SortSelect.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { sortBy, type SortDir } from '$lib/utils/sort';
import { syncFiltersToUrl } from '$lib/utils/urlFilters';
import { formatDate } from '$lib/utils/date';

	const filters = ['All', 'Open', 'In Progress', 'Blocked', 'Done'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'title', label: t('Judul') },
		{ value: 'priority', label: t('Prioritas') },
		{ value: 'status', label: t('Status') },
		{ value: 'owner', label: t('Pemilik') },
		{ value: 'due', label: t('Tenggat') },
		{ value: 'id', label: 'ID' }
	];
	let message = $state('');
	let showForm = $state(false);
	let creating = $state(false);
	let formError = $state('');
	let fTitle = $state('');
	let fModule = $state('');
	let fOwner = $state('');
	let fPriority = $state('Medium');
	let fDueDate = $state('');
	let error = $state('');

	let workTasks = createRemoteList(listTasks, seedTasks);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	let paramProcessed = $state(false);

	$effect(() => {
		workTasks.load();
		projects.load();
	});

	$effect(() => {
		if (paramProcessed) return;
		const queryTitle = page.url.searchParams.get('title');
		const queryModule = page.url.searchParams.get('module');
		const queryPriority = page.url.searchParams.get('priority');
		const queryOwner = page.url.searchParams.get('owner');
		const querySearch = page.url.searchParams.get('search');

		if (querySearch && !query) {
			query = querySearch;
		}
		if (queryTitle || queryModule) {
			if (queryTitle) fTitle = queryTitle;
			if (queryModule) fModule = queryModule;
			if (queryPriority) fPriority = queryPriority;
			if (queryOwner) fOwner = queryOwner;
			showForm = true;
			paramProcessed = true;
		}
	});

	let filteredTasks = $derived(
		sortBy(
			workTasks.items.filter(
				(task) =>
					(activeFilter === 'All' || task.status === activeFilter) &&
					[task.title, task.module, task.owner, task.priority, task.status].join(' ').toLowerCase().includes(query.trim().toLowerCase())
			),
			sortKey,
			sortDir
		)
	);
	let blocked = $derived(workTasks.items.filter((task) => task.status === 'Blocked').length);
	let critical = $derived(workTasks.items.filter((task) => task.priority === 'Critical').length);
	function projectName(id: string) {
		return projects.items.find((project) => project.id === id)?.name ?? id;
	}


	function openCreate() {
		fTitle = '';
		fModule = '';
		fOwner = '';
		fPriority = 'Medium';
		fDueDate = '';
		formError = '';
		showForm = true;
	}

	let busyId = $state('');

	// Konfirmasi terpusat: satu dialog melayani hapus tugas agar tidak lagi
	// memakai window.confirm() yang memblokir dan tidak aksesibel.
	const confirm = createConfirmController();

	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter, sort: sortKey, dir: sortKey ? sortDir : '' };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '', sort: '', dir: '' }, ['query', 'status', 'sort', 'dir']), 250);
		return () => clearTimeout(syncTimer);
	});

	async function handleCreate() {
		formError = '';
		if (!fTitle.trim()) {
			formError = t('Judul wajib diisi.');
			return;
		}
		creating = true;
		try {
			const res = await createTask({
				title: fTitle.trim(),
				module: fModule.trim() || 'General',
				owner: fOwner.trim() || 'Operations',
				priority: fPriority,
				dueDate: fDueDate.trim() || new Date().toISOString().slice(0, 10)
			});
			if (res.data) workTasks.upsert(res.data);
			else await workTasks.load();
			message = `Tugas "${fTitle.trim()}" dibuat.`;
			showForm = false;
		} catch {
			formError = t('Gagal membuat tugas.');
		} finally {
			creating = false;
		}
	}

	async function handleCompleteTask(task: WorkTask) {
		error = '';
		busyId = task.id;
		try {
			const res = await completeTask(task.id);
			if (res.data) workTasks.upsert(res.data);
			else workTasks.upsert({ ...task, status: 'Done' });
			message = `Tugas "${task.title}" ditandai selesai.`;
		} catch {
			error = t('Gagal menyelesaikan tugas.');
		} finally {
			busyId = '';
		}
	}

	async function handleDeleteTask(task: WorkTask) {
		error = '';
		busyId = task.id;
		try {
			await deleteTask(task.id);
			workTasks.remove(task.id);
			message = `Tugas "${task.title}" dihapus.`;
		} catch {
			error = 'Gagal menghapus tugas.';
		} finally {
			busyId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredTasks ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredTasks?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		sortKey;
		sortDir;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Tugas')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Tasks')} eyebrow={t('Operational work queue')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Next actions')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Prioritize the work that unblocks export execution.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Convert compliance gaps, supplier evidence, payments, documents, and shipment exceptions into accountable operational tasks.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create task')}</Button>
			<Badge variant="destructive">{t('Blocked')} {blocked}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={fTitle} placeholder={t('Siapkan dokumen ekspor')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Modul')}
						<Input bind:value={fModule} placeholder={t('Dokumen')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Owner')}
						<Input bind:value={fOwner} placeholder="ops" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Prioritas')}
						<select bind:value={fPriority} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['Low', 'Medium', 'High', 'Critical'] as priority}
								<option value={priority}>{priority}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Due date')}
						<Input bind:value={fDueDate} type="date" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : t('Simpan tugas')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if workTasks.error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{workTasks.error}</p>
	{/if}

	{#if message}
		<p role="status" class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Input bind:value={query} type="search"
				aria-label={t('Search task, module, owner...')} placeholder={t('Search task, module, owner...')} class="w-[min(390px,100%)]" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
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
				<Card class="flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/tasks/${task.id}`} class="block p-5 no-underline">
						<div class="flex items-center justify-between gap-3"><Badge variant={toneVariant(statusTone(task.status))}>{label(task.status)}</Badge><strong class="text-sm font-bold">{label(task.priority)}</strong></div>
						<h3 class="mt-4 text-2xl font-bold tracking-tight">{task.title}</h3>
						<p class="mt-2 text-sm text-muted-foreground">{task.module} · {projectName(task.projectId)}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{task.owner}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Due')} <strong class="mt-1 block text-sm font-bold text-foreground">{formatDate(task.due)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Checklist')} <strong class="mt-1 block text-sm font-bold text-foreground">{(task.checklist ?? []).filter((item) => item.done).length}/{task.checklist?.length ?? 0}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Priority')} <strong class="mt-1 block text-sm font-bold text-foreground">{label(task.priority)}</strong></div>
						</div>
					</a>
					<div class="px-5 pb-4 pt-1 flex items-center justify-end gap-2 border-t">
						{#if task.status !== 'Done'}
							<Button
								variant="outline"
								size="sm"
								disabled={busyId === task.id}
								onclick={() => handleCompleteTask(task)}
							>
								{busyId === task.id ? t('Menyimpan...') : t('Mark done')}
							</Button>
						{/if}
						<Button
							variant="ghost"
							size="sm"
							class="text-destructive hover:bg-destructive/10"
							disabled={busyId === task.id}
							onclick={() =>
								confirm.ask({
									title: t('Hapus tugas'),
									description: t('Tugas ini akan dihapus permanen dari workspace.'),
									detail: task.title,
									action: () => handleDeleteTask(task)
								})}
						>
							{t('Hapus')}
						</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No task matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredTasks?.length ?? 0} />

	<ConfirmDialog
		bind:open={confirm.open}
		title={confirm.title}
		description={confirm.description}
		detail={confirm.detail}
		confirmLabel={confirm.label}
		loading={confirm.loading}
		onconfirm={confirm.run}
	/>
</AppShell>