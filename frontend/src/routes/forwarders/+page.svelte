<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { forwarders as seedForwarders } from '$lib/data/trade';
	import { listForwarders } from '$lib/api/forwarders';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	const modeFilters = ['All', 'Ocean', 'Air', 'Multimodal'];
	let activeFilter = $state('All');
	let query = $state('');

	let forwarders = createRemoteList(listForwarders, seedForwarders);
	$effect(() => {
		forwarders.load();
	});

	let filteredForwarders = $derived(
		forwarders.items.filter((forwarder) => {
			const matchesFilter = activeFilter === 'All' || forwarder.mode === activeFilter;
			const matchesQuery = [forwarder.name, forwarder.coverage, forwarder.mode, ...forwarder.lanes]
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
	<title>Forwarders | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarders" eyebrow="Freight partner network">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Logistics network</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Verified freight partners for your export lanes.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Compare on-time rates, quote speed, and covered lanes, then request a quote for active shipments.</CardDescription>
		</CardHeader>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each modeFilters as filter}
				<Button
					variant={activeFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (activeFilter = filter)}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search forwarder, lane, coverage..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredForwarders as forwarder}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/forwarders/${forwarder.id}`} class="grid h-full gap-3 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(forwarder.status))}>{forwarder.status}</Badge>
						<span class="text-sm text-muted-foreground">{forwarder.mode}</span>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{forwarder.name}</h3>
					<p class="text-sm text-muted-foreground">{forwarder.coverage}</p>
					<div class="grid gap-2 sm:grid-cols-3">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">On-time<strong class="mt-1 block text-sm font-bold text-foreground">{forwarder.onTimeRate}%</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Quote speed<strong class="mt-1 block text-sm font-bold text-foreground">{forwarder.quoteSpeed}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Lanes<strong class="mt-1 block text-sm font-bold text-foreground">{forwarder.lanes.length}</strong></div>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each forwarder.lanes as lane}<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{lane}</span>{/each}
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No forwarder matched your filter.</div>
		{/each}
	</div>
</AppShell>
