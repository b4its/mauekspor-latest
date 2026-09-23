<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { statusTone } from '$lib/utils/format';
	import type { Product } from '$lib/data/trade';

	let filter = $state('All');
	let query = $state('');
	const filters = ['All', 'Ready', 'Enriched', 'Needs HS Review'];
	let products = $state<Product[]>([]);
	let loaded = $state(false);

	$effect(() => {
		listProducts()
			.then((res) => {
				products = res.data;
			})
			.catch(() => {
				products = seedProducts;
			})
			.finally(() => (loaded = true));
	});

	let filteredProducts = $derived(
		products.filter((product) => {
			const matchesFilter = filter === 'All' || product.status === filter;
			const matchesQuery = [product.name, product.category, product.origin, product.hs]
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
	<title>Products | MauEkspor</title>
</svelte:head>

<AppShell title="Products" eyebrow="Export product master data">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">Product intelligence</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Structured product data for export readiness.
				</CardTitle>
				<CardDescription class="mt-2 max-w-xl leading-relaxed">
					Capture specifications, packaging, HS candidates, certificates, origin details, and product
					revisions before compliance analysis or quotation.
				</CardDescription>
			</div>
			<Button href="/products/new">Add product</Button>
		</div>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as item}
				<Button
					variant={filter === item ? 'default' : 'outline'}
					size="sm"
					onclick={() => (filter = item)}
				>
					{item}
				</Button>
			{/each}
		</div>
		<Input
			bind:value={query}
			type="search"
			placeholder="Search product, origin, HS..."
			class="max-w-xs"
		/>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredProducts as product}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/products/${product.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(product.status))}>{product.status}</Badge>
						<strong class="text-3xl font-bold tracking-tight">{product.readiness}%</strong>
					</div>
					<h3 class="mt-4 text-xl font-bold tracking-tight">{product.name}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{product.category} - {product.origin}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							HS <strong class="mt-1 block text-sm font-bold text-foreground">{product.hs}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							MOQ <strong class="mt-1 block text-sm font-bold text-foreground">{product.moq}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Lead time <strong class="mt-1 block text-sm font-bold text-foreground">{product.leadTime}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Packaging <strong class="mt-1 block text-sm font-bold text-foreground">{product.packaging}</strong>
						</div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No product matched your filter.</div>
		{/each}
	</div>
</AppShell>