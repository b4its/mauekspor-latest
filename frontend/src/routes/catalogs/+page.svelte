<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { catalogs as seedCatalogs, products as seedProducts } from '$lib/data/trade';
	import { listCatalogs, deleteCatalog } from '$lib/api/catalogs';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	const filters = ['All', 'Published', 'Draft', 'Needs Review'];
	let activeFilter = $state('All');
	let query = $state('');
	let deleting = $state('');
	let error = $state('');

	let catalogs = createRemoteList(listCatalogs, seedCatalogs);
	let products = createRemoteList(listProducts, seedProducts);
	$effect(() => {
		catalogs.load();
		products.load();
	});

	async function removeCatalog(id: string, title: string) {
		if (!confirm(`Hapus katalog "${title}"?`)) return;
		error = '';
		deleting = id;
		try {
			await deleteCatalog(id);
			const idx = catalogs.items.findIndex((c) => c.id === id);
			if (idx >= 0) catalogs.items.splice(idx, 1);
		} catch {
			error = 'Gagal menghapus katalog.';
		} finally {
			deleting = '';
		}
	}

	let filteredCatalogs = $derived(
		catalogs.items.filter((catalog) => {
			const product = products.items.find((item) => item.id === catalog.productId)?.name ?? '';
			const matchesFilter = activeFilter === 'All' || catalog.status === activeFilter;
			const matchesQuery = [catalog.id, catalog.title, catalog.targetMarket, catalog.status, product]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let publishedCount = $derived(catalogs.items.filter((catalog) => catalog.status === 'Published').length);
	let avgReadiness = $derived(Math.round(catalogs.items.reduce((sum, catalog) => sum + catalog.readiness, 0) / (catalogs.items.length || 1)));

	function productName(productId: string) {
		return products.items.find((product) => product.id === productId)?.name ?? productId;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Catalogs | MauEkspor</title>
</svelte:head>

<AppShell title="Catalogs" eyebrow="Buyer-facing export catalog">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Commercial presentation</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Turn verified product data into buyer-ready export catalogs.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Package product specifications, MOQ, lead time, Incoterms, certificates, images, and AI-assisted B2B descriptions for buyer discovery and RFQ conversion.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/catalogs/create">Create catalog</Button>
			<Badge variant="secondary">Published {publishedCount}</Badge>
		</CardContent>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button
					variant={activeFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (activeFilter = filter)}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search catalog, market, product..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Catalogs</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{catalogs.items.length}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Published</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{publishedCount}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Readiness</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{avgReadiness}%</strong>
			</CardContent>
		</Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredCatalogs as catalog}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/catalogs/${catalog.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(catalog.status))}>{catalog.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{catalog.readiness}%</strong>
					</div>
					<h3 class="mt-4 text-2xl font-bold tracking-tight">{catalog.title}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{productName(catalog.productId)}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Market <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.targetMarket}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							MOQ <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.moq}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Lead time <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.leadTime}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Images <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.images}</strong>
						</div>
					</div>
					<div class="mt-3 flex items-center justify-end gap-2">
						<Button size="sm" variant="outline" href={`/catalogs/${catalog.id}/edit`}>Edit</Button>
						<Button size="sm" variant="destructive" disabled={deleting === catalog.id} onclick={(e) => { e.preventDefault(); removeCatalog(catalog.id, catalog.title); }}>
							{deleting === catalog.id ? '...' : 'Hapus'}
						</Button>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
				No catalog matched your search.
			</div>
		{/each}
	</div>
	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
</AppShell>