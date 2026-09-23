<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { costingScenarios as seedScenarios, projects as seedProjects } from '$lib/data/trade';
import { listCostingScenarios } from '$lib/api/costing';
import { listTradeProjects } from '$lib/api/trade-projects';
import { csvExportUrl } from '$lib/api/client';
import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';

	const filters = ['All', 'Ready', 'Needs Review', 'Draft'];
	let activeFilter = $state('All');
	let query = $state('');

	let costingScenarios = createRemoteList(listCostingScenarios, seedScenarios);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		costingScenarios.load();
		projects.load();
	});

	let filteredScenarios = $derived(
		costingScenarios.items.filter((scenario) => {
			const matchesFilter = activeFilter === 'All' || scenario.status === activeFilter;
			const matchesQuery = [scenario.id, scenario.title, scenario.destination, scenario.incoterm, scenario.projectId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let totalLanded = $derived(costingScenarios.items.reduce((sum, item) => sum + item.landedCost, 0));
	let averageMargin = $derived(Math.round(costingScenarios.items.reduce((sum, item) => sum + item.margin, 0) / (costingScenarios.items.length || 1)));

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Costing | MauEkspor</title>
</svelte:head>

<AppShell title="Costing" eyebrow="Incoterm pricing and landed cost">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Cost control</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Separate seller price, freight estimate, and buyer landed cost.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Model EXW, FOB, CIF, DAP, freight validity, currency exposure, destination charges, tax reserve, and margin before quotation acceptance.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/costing/create">Create scenario</Button>
<Button href={csvExportUrl('/costing/export.csv')} variant="outline">Export CSV</Button>
			<Badge variant="secondary">Avg margin {averageMargin}%</Badge>
		</CardContent>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search scenario, country, incoterm..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Scenarios</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{costingScenarios.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Total landed estimate</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(totalLanded)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Average margin</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{averageMargin}%</strong></CardContent></Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredScenarios as scenario}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/costing/${scenario.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(scenario.status))}>{scenario.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{scenario.confidence}%</strong>
					</div>
					<h3 class="mt-3 text-2xl font-bold tracking-tight">{scenario.title}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{projectName(scenario.projectId)}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Incoterm<strong class="mt-1 block text-sm font-bold text-foreground">{scenario.incoterm}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Destination<strong class="mt-1 block text-sm font-bold text-foreground">{scenario.destination}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">FOB<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(scenario.fobPrice)}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Landed<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(scenario.landedCost)}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No costing scenario matched your search.</div>
		{/each}
	</div>
</AppShell>
