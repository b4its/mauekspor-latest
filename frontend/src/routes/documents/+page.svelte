<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { projects as seedProjects, tradeDocuments as seedDocuments } from '$lib/data/trade';
	import type { TradeDocument } from '$lib/data/trade';
	import { listTradeDocuments, generateTradeDocument } from '$lib/api/documents';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Ready', 'Needs Review', 'Approved', 'Missing'];
	let activeFilter = $state('All');
	let query = $state('');
	let generating = $state(false);
	let message = $state('');
	let showForm = $state(false);
	let formError = $state('');
	let fProjectId = $state('');
	let fType = $state('Commercial Invoice');
	let error = $state('');

	let tradeDocuments = createRemoteList(listTradeDocuments, seedDocuments);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		tradeDocuments.load();
		projects.load();
	});

	let filteredDocuments = $derived(
		tradeDocuments.items.filter((document) => {
			const matchesFilter = activeFilter === 'All' || document.status === activeFilter;
			const matchesQuery = [document.id, document.type, document.owner, document.projectId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let averageScore = $derived(
		Math.round(tradeDocuments.items.reduce((sum, document) => sum + document.validationScore, 0) / (tradeDocuments.items.length || 1))
	);
	let needsReviewCount = $derived(tradeDocuments.items.filter((document) => document.status !== 'Ready' && document.status !== 'Approved').length);

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}

	function openCreate() {
		fProjectId = '';
		fType = 'Commercial Invoice';
		formError = '';
		showForm = true;
	}

	async function generateDocument() {
		formError = '';
		if (!fProjectId) {
			formError = t('Project wajib dipilih.');
			return;
		}
		generating = true;
		try {
			await generateTradeDocument({
				projectId: fProjectId,
				type: fType as TradeDocument['type']
			});
			await tradeDocuments.load();
			message = `Dokumen ${fType} dibuat.`;
			showForm = false;
		} catch {
			formError = t('Gagal generate dokumen.');
		} finally {
			generating = false;
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredDocuments ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredDocuments?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Dokumen')} | MauEkspor</title>
</svelte:head>

<AppShell title="Documents" eyebrow="Trade document center">
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Kontrol dokumen')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				Generate, validate, approve, and version trade documents.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Keep invoice, packing list, certificate of origin, lab reports, insurance, and shipment
				documents consistent with product, quotation, and shipment data.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Generate document')}</Button>
			<Badge variant="secondary">Avg validation {averageScore}%</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Project')}
						<select bind:value={fProjectId} class="h-10 rounded-md border bg-background px-3 text-sm">
							<option value="">{t('Pilih project')}</option>
							{#each projects.items as project}
								<option value={project.id}>{project.name}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tipe dokumen')}
						<select bind:value={fType} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['Commercial Invoice', 'Packing List', 'COO', 'Proforma'] as type}
								<option value={type}>{type}</option>
							{/each}
						</select>
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={generating} onclick={generateDocument}>{generating ? t('Generating...') : t('Generate document')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if tradeDocuments.error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{tradeDocuments.error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search document, owner, project..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total documents')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{tradeDocuments.items.length}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Need attention')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{needsReviewCount}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Validation score')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{averageScore}%</strong>
			</CardContent>
		</Card>
	</div>

	{#if tradeDocuments.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-8 w-16" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-1 h-4 w-1/2" />
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
			{#each pagedItems as document}
				<Card class="transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/documents/${document.id}`} class="block h-full p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(document.status))}>{document.status}</Badge>
							<strong class="text-3xl font-bold tracking-tight">{document.validationScore}%</strong>
						</div>
						<h3 class="mt-4 text-xl font-bold tracking-tight">{document.type}</h3>
						<p class="mt-1 text-sm text-muted-foreground">{projectName(document.projectId)}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('ID')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.id}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Version')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.version}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.owner}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Updated')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.updatedAt}</strong>
							</div>
						</div>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No document matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredDocuments?.length ?? 0} />

</AppShell>