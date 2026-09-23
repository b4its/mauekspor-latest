<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { refreshMarketInsight } from '$lib/api/markets';

	let { data } = $props();
	let refreshed = $state(false);
	let refreshing = $state(false);
	let error = $state('');
	let selectedScenario = $state('Base');
	const scenarios = ['Base', 'Optimistic', 'Conservative'];

	let displayScore = $derived(
		selectedScenario === 'Optimistic'
			? Math.min(data.market.marketScore + 6, 100)
			: selectedScenario === 'Conservative'
				? Math.max(data.market.marketScore - 8, 0)
				: refreshed
					? Math.min(data.market.marketScore + 2, 100)
					: data.market.marketScore
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleRefresh() {
		error = '';
		refreshing = true;
		try {
			await refreshMarketInsight(data.market.id);
			refreshed = true;
		} catch {
			error = 'Gagal refresh insight pasar.';
		} finally {
			refreshing = false;
		}
	}
</script>

<svelte:head>
	<title>{data.market.country} Market | MauEkspor</title>
</svelte:head>

<AppShell title={data.market.country} eyebrow="Market insight detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.market.status))}>{data.market.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.product?.name ?? data.market.productId}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.market.projectId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Market score</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayScore}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Market Decision Summary</CardTitle>
					<CardDescription>{data.market.entryStrategy}</CardDescription>
				</div>
				<div class="flex flex-wrap items-center gap-2.5">
					<NativeSelect bind:value={selectedScenario} class="w-40">
						{#each scenarios as scenario}
							<option>{scenario}</option>
						{/each}
					</NativeSelect>
					<Button onclick={handleRefresh} disabled={refreshing}>{refreshed ? 'Refreshed' : refreshing ? 'Refreshing...' : 'Refresh insight'}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Import value <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.importValue}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Growth <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.growth}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Tariff/compliance <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.tariff}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Complexity <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.complianceComplexity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Logistics <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.logisticsFeasibility}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Margin <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.estimatedMargin}%</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>Opportunities</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 p-0 pt-4">
				{#each data.market.opportunities as item}
					<span class="rounded-lg bg-primary/10 px-3 py-3 font-bold leading-relaxed text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>Risks</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 p-0 pt-4">
				{#each data.market.risks as item}
					<span class="rounded-lg bg-orange-500/10 px-3 py-3 font-bold leading-relaxed text-orange-700">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">Evidence provenance</Badge>
				<CardTitle>Sources and retrieval dates</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.market.sources as source}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<strong class="block text-sm font-bold">{source.name}</strong>
							<span class="mt-1 block text-sm text-muted-foreground">{source.date}</span>
						</div>
					{/each}
				</div>
				{#if refreshed}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Insight diperbarui di backend.</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>