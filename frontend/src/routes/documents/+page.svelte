<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { projects as seedProjects, tradeDocuments as seedDocuments } from '$lib/data/trade';
	import { listTradeDocuments, generateTradeDocument } from '$lib/api/documents';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Ready', 'Needs Review', 'Approved', 'Missing'];
	let activeFilter = $state('All');
	let query = $state('');
	let generating = $state(false);
	let generated = $state(false);
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

	async function generateDocument() {
		error = '';
		generating = true;
		try {
			await generateTradeDocument({
				projectId: projects.items[0]?.id ?? seedProjects[0]?.id ?? '',
				type: 'Commercial Invoice'
			});
			generated = true;
		} catch {
			error = 'Gagal generate dokumen.';
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
</script>

<svelte:head>
	<title>Documents | MauEkspor</title>
</svelte:head>

<AppShell title="Documents" eyebrow="Trade document center">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Document control</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Generate, validate, approve, and version trade documents.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Keep invoice, packing list, certificate of origin, lab reports, insurance, and shipment
				documents consistent with product, quotation, and shipment data.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button disabled={generating} onclick={generateDocument}>
				{generating ? 'Generating...' : generated ? 'Document generated' : 'Generate document'}
			</Button>
			<Badge variant="secondary">Avg validation {averageScore}%</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if generated}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Generated draft ready.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Dokumen berhasil dibuat di backend.
			</span>
		</div>
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

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredDocuments as document}
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
</AppShell>