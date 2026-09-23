<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { catalogs, forwarders } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';

	const forwarder = forwarders[0];
	let query = $state('');

	let filteredCatalogs = $derived(
		catalogs.filter((catalog) => {
			const matchesQuery = [catalog.title, catalog.targetMarket, catalog.status]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return catalog.status === 'Published' && matchesQuery;
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
	<title>Forwarder Catalogs | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarder Catalogs" eyebrow="Freight quote inventory">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(forwarder.status))}>{forwarder.name}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Active export catalogs available for quotes.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Published catalogs represent the ready-to-quote inventory this forwarder can service across
				its covered lanes.
			</CardDescription>
		</CardHeader>
	</Card>

	<div class="flex flex-wrap items-center justify-end gap-3">
		<Input bind:value={query} type="search" placeholder="Search published catalog..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredCatalogs as catalog}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/catalogs/${catalog.id}`} class="grid h-full gap-3 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(catalog.status))}>{catalog.status}</Badge>
						<Badge variant="outline">{forwarder.lanes.length} lanes</Badge>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{catalog.title}</h3>
					<p class="text-sm text-muted-foreground">{catalog.targetMarket}</p>
					<div class="grid gap-2 sm:grid-cols-3">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">MOQ<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.moq}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Lead time<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.leadTime}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Price<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.priceRange}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No published catalog matched.</div>
		{/each}
	</div>
</AppShell>
