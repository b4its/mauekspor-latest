<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { marketInsights as seedMarkets, products as seedProducts } from '$lib/data/trade';
	import { listMarketInsights, createMarketInsight } from '$lib/api/markets';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Recommended', 'Watchlist', 'Needs Research'];
	let activeFilter = $state('All');
	let query = $state('');
	let generated = $state(false);
	let generating = $state(false);
	let error = $state('');

	let marketInsights = createRemoteList(listMarketInsights, seedMarkets);
	let products = createRemoteList(listProducts, seedProducts);
	$effect(() => {
		marketInsights.load();
		products.load();
	});

	let filteredMarkets = $derived(
		marketInsights.items.filter((market) => {
			const product = products.items.find((item) => item.id === market.productId)?.name ?? '';
			const matchesFilter = activeFilter === 'All' || market.status === activeFilter;
			const matchesQuery = [market.id, market.country, market.status, market.entryStrategy, product]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let averageScore = $derived(Math.round(marketInsights.items.reduce((sum, market) => sum + market.marketScore, 0) / (marketInsights.items.length || 1)));
	let recommendedCount = $derived(marketInsights.items.filter((market) => market.status === 'Recommended').length);

	function productName(productId: string) {
		return products.items.find((product) => product.id === productId)?.name ?? productId;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleGenerate() {
		error = '';
		generating = true;
		try {
			const seed = seedMarkets[0];
			await createMarketInsight({
				productId: seed?.productId ?? 'prd-001',
				country: seed?.country ?? 'Japan',
				projectId: seed?.projectId
			});
			generated = true;
		} catch {
			error = t('Gagal generate insight pasar.');
		} finally {
			generating = false;
		}
	}
</script>

<svelte:head>
	<title>Markets | MauEkspor</title>
</svelte:head>

<AppShell title="Markets" eyebrow={t('Market intelligence and country selection')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Country opportunity radar')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Prioritize export markets before committing compliance and logistics cost.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Compare market attractiveness, compliance complexity, logistics feasibility, margin potential, and source-backed risks by product.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleGenerate} disabled={generating}>{generated ? t('Insight generated') : generating ? t('Generating...') : t('Generate insight')}</Button>
			<Badge variant="secondary">{t('Avg score')} {averageScore}%</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if generated}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Market insight draft ready.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Insight dibuat di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search country, product, strategy...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Markets tracked')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{marketInsights.items.length}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Recommended')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{recommendedCount}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Average score')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{averageScore}%</strong>
			</CardContent>
		</Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredMarkets as market}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/markets/${market.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(market.status))}>{market.status}</Badge>
						<strong class="text-3xl font-bold tracking-tight">{market.marketScore}%</strong>
					</div>
					<h3 class="mt-4 text-xl font-bold tracking-tight">{market.country}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{productName(market.productId)}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Compliance')} <strong class="mt-1 block text-sm font-bold text-foreground">{market.complianceComplexity}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Logistics')} <strong class="mt-1 block text-sm font-bold text-foreground">{market.logisticsFeasibility}%</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Margin')} <strong class="mt-1 block text-sm font-bold text-foreground">{market.estimatedMargin}%</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Growth')} <strong class="mt-1 block text-sm font-bold text-foreground">{market.growth}</strong>
						</div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No market insight matched your search.')}</div>
		{/each}
	</div>
</AppShell>