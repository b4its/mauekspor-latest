<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { buyers, exportAnalyses, forwarders, products } from '$lib/data/trade';
	import { currency, statusTone } from '$lib/utils/format';

	function demandTone(demand: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (demand === 'High') return 'default';
		if (demand === 'Medium') return 'outline';
		return 'secondary';
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	let exportedValue = $derived(products.length * 12500);
	let leadCount = $derived(buyers.filter((buyer) => ['Lead', 'Qualified'].includes(buyer.status)).length);
	let readyCount = $derived(products.filter((product) => product.status !== 'Needs HS Review').length);
	let analysisReady = $derived(exportAnalyses.filter((item) => item.status === 'Ready').length);
	let verifiedForwarders = $derived(forwarders.filter((item) => item.status === 'Verified').length);
</script>

<svelte:head>
	<title>Marketing | MauEkspor</title>
</svelte:head>

<AppShell title="Marketing" eyebrow="Export demand generation">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">Demand funnel</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Turn product readiness into buyer pipeline.
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					Track catalog exposure, lead quality, and market analysis coverage for each export target.
				</CardDescription>
			</div>
			<Button href="/catalogs">Manage catalogs</Button>
		</div>
	</Card>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
		<div class="rounded-xl border bg-card p-4">
			<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Catalog-ready products</span>
			<strong class="mt-1 block text-3xl font-bold tracking-tight">{readyCount}</strong>
			<small class="text-xs font-semibold text-muted-foreground">of {products.length} products</small>
		</div>
		<div class="rounded-xl border bg-card p-4">
			<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Active leads</span>
			<strong class="mt-1 block text-3xl font-bold tracking-tight">{leadCount}</strong>
			<small class="text-xs font-semibold text-muted-foreground">across buyers</small>
		</div>
		<div class="rounded-xl border bg-card p-4">
			<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Market analyses</span>
			<strong class="mt-1 block text-3xl font-bold tracking-tight">{analysisReady}</strong>
			<small class="text-xs font-semibold text-muted-foreground">ready for buyer outreach</small>
		</div>
		<div class="rounded-xl border bg-card p-4">
			<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Estimated pipeline</span>
			<strong class="mt-1 block text-3xl font-bold tracking-tight">{currency.format(exportedValue)}</strong>
			<small class="text-xs font-semibold text-muted-foreground">demo estimate</small>
		</div>
		<div class="rounded-xl border bg-card p-4">
			<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Verified forwarders</span>
			<strong class="mt-1 block text-3xl font-bold tracking-tight">{verifiedForwarders}</strong>
			<small class="text-xs font-semibold text-muted-foreground">ready to quote</small>
		</div>
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>Buyer funnel</CardTitle>
				<Button variant="outline" size="sm" href="/buyers">Open CRM</Button>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each buyers as buyer}
					<a class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5 no-underline transition-colors hover:bg-muted/60" href={`/buyers/${buyer.id}`}>
						<div>
							<strong class="block text-sm font-bold">{buyer.name}</strong>
							<span class="mt-1 block text-xs font-semibold text-muted-foreground">{buyer.segment} - {buyer.country}</span>
						</div>
						<div class="grid justify-items-end gap-1.5">
							<Badge variant={toneVariant(statusTone(buyer.status))}>{buyer.status}</Badge>
							<b class="text-lg font-bold tracking-tight">{currency.format(buyer.estimatedAnnualValue)}</b>
						</div>
					</a>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>Target market exposure</CardTitle>
				<Button variant="outline" size="sm" href="/export-analysis">Analyze market</Button>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each exportAnalyses as analysis}
					<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5">
						<div>
							<strong class="block text-sm font-bold">{analysis.destination}</strong>
							<span class="mt-1 block text-xs font-semibold text-muted-foreground">{analysis.productName}</span>
						</div>
						<div class="grid justify-items-end gap-1.5">
							<Badge variant={demandTone(analysis.marketDemand)}>{analysis.marketDemand} demand</Badge>
							<b class="text-lg font-bold tracking-tight">{analysis.score}</b>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>
	</div>
</AppShell>