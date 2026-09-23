<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { exportAnalyses as seedAnalyses } from '$lib/data/trade';
	import { listExportAnalyses } from '$lib/api/export-analysis';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	const filters = ['All', 'Ready', 'In Progress', 'Needs Review'];
	let activeFilter = $state('All');
	let query = $state('');

	let exportAnalyses = createRemoteList(listExportAnalyses, seedAnalyses);
	$effect(() => {
		exportAnalyses.load();
	});

	let filteredAnalyses = $derived(
		exportAnalyses.items.filter((analysis) => {
			const matchesFilter = activeFilter === 'All' || analysis.status === activeFilter;
			const matchesQuery = [analysis.productName, analysis.destination, analysis.hsCode, analysis.status]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Export Analysis | MauEkspor</title>
</svelte:head>

<AppShell title="Export Analysis" eyebrow="Market readiness intelligence">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">AI market intelligence</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Know the destination before you quote.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">HS classification, duties, restrictions, and regulation recommendations for each product-market pair.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/export-analysis/create">New analysis</Button>
			<Button href="/export-analysis/compare" variant="outline">Compare markets</Button>
		</CardContent>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search product, destination, HS..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredAnalyses as analysis}
			<Card class="p-5">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(analysis.status))}>{analysis.status}</Badge>
					<strong class="text-2xl font-bold tracking-tight">{analysis.score}</strong>
				</div>
				<h3 class="mt-3 text-2xl font-bold tracking-tight">{analysis.productName}</h3>
				<p class="mt-1 text-sm text-muted-foreground">{analysis.destination} - HS {analysis.hsCode}</p>
				<div class="mt-4 grid grid-cols-2 gap-2">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Confidence<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.confidence}%</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Demand<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.marketDemand}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Duties<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.duties.split(' ')[0]}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Restrictions<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.restrictions.length}</strong></div>
				</div>
				<div class="mt-4 flex flex-wrap gap-3">
					<Button variant="ghost" size="sm" href={`/export-analysis/${analysis.id}`}>Open analysis</Button>
					<Button variant="outline" size="sm" href={`/export-analysis/${analysis.id}/regulation-recommendations`}>Recommendations</Button>
				</div>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No analysis matched your filter.</div>
		{/each}
	</div>
</AppShell>
