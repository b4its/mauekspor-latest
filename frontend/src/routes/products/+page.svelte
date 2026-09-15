<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts, deleteProduct, batchEnrichProducts, batchDeleteProducts } from '$lib/api/products';
	import { csvExportUrl } from '$lib/api/client';
	import { statusTone } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import type { Product } from '$lib/data/trade';

	let filter = $state('All');
	let query = $state('');
	const filters = ['All', 'Ready', 'Enriched', 'Needs HS Review'];
	let products = $state<Product[]>([]);
	let loaded = $state(false);
	let deleting = $state('');
	let error = $state('');
	let batching = $state('');
	let batchMessage = $state('');
	let selected = $state<Set<string>>(new Set());
	let batchDeleting = $state(false);

	let pendingCount = $derived(products.filter((p) => p.status !== 'Enriched').length);

	async function runBatchEnrich() {
		if (!confirm(`Enrich ${pendingCount} produk yang belum lengkap? (AI HS code + SKU otomatis)`)) return;
		error = '';
		batchMessage = '';
		batching = 'enrich';
		try {
			const res = await batchEnrichProducts();
			batchMessage = `Enrich selesai: ${res.data.enrichedCount} produk di-enrich.`;
			const reload = await listProducts();
			products = reload.data;
		} catch {
			error = 'Gagal menjalankan batch enrich.';
		} finally {
			batching = '';
		}
	}

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

	async function removeProduct(id: string, name: string) {
		if (!confirm(`Hapus produk "${name}"?`)) return;
		error = '';
		deleting = id;
		try {
			await deleteProduct(id);
			products = products.filter((p) => p.id !== id);
		} catch {
			error = 'Gagal menghapus produk.';
		} finally {
			deleting = '';
		}
	}

	function toggleSelected(id: string) {
		const next = new Set(selected);
		if (next.has(id)) next.delete(id);
		else next.add(id);
		selected = next;
	}

	function toggleAll() {
		const visible = filteredProducts.map((p) => p.id);
		const allSelected = visible.every((id) => selected.has(id));
		const next = new Set(selected);
		for (const id of visible) {
			if (allSelected) next.delete(id);
			else next.add(id);
		}
		selected = next;
	}

	async function removeSelected() {
		if (selected.size === 0) return;
		if (!confirm(`Hapus ${selected.size} produk terpilih?`)) return;
		error = '';
		batchMessage = '';
		batchDeleting = true;
		try {
			const res = await batchDeleteProducts([...selected]);
			batchMessage = `Hapus selesai: ${res.data.deletedCount} produk dihapus.`;
			selected = new Set();
			const reload = await listProducts();
			products = reload.data;
		} catch {
			error = 'Gagal menghapus produk terpilih.';
		} finally {
			batchDeleting = false;
		}
	}

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
	<title>{t('Produk')} | MauEkspor</title>
</svelte:head>

<AppShell title="Products" eyebrow="Export product master data">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">{t('Product intelligence')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Structured product data for export readiness.
				</CardTitle>
				<CardDescription class="mt-2 max-w-xl leading-relaxed">
					Capture specifications, packaging, HS candidates, certificates, origin details, and product
					revisions before compliance analysis or quotation.
				</CardDescription>
			</div>
		<Button href="/products/new">{t('Add product')}</Button>
		<div class="flex gap-2">
			<Button variant="outline" href={csvExportUrl('/products/export.csv')}>{t('Export CSV')}</Button>
			<Button variant="outline" href={csvExportUrl('/products/export.xlsx')}>{t('Excel (.xlsx)')}</Button>
		</div>
	</div>
	{#if pendingCount > 0}
		<div class="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-dashed p-4">
			<div class="text-sm font-semibold text-muted-foreground">
				{pendingCount} {t('produk masih butuh AI enrichment')}.
			</div>
			<Button size="sm" variant="secondary" disabled={batching === 'enrich'} onclick={runBatchEnrich}>
				{batching === 'enrich' ? t('Enriching...') : `Enrich semua (${pendingCount})`}
			</Button>
		</div>
	{/if}
	{#if batchMessage}
		<p class="mt-3 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{batchMessage}</p>
	{/if}
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
		<div class="flex flex-wrap items-center gap-2">
			<label class="flex cursor-pointer items-center gap-1.5 text-sm font-semibold text-muted-foreground">
				<input type="checkbox" class="size-4" checked={filteredProducts.length > 0 && filteredProducts.every((p) => selected.has(p.id))} onchange={toggleAll} />
				{t('Pilih semua')}
			</label>
			{#if selected.size > 0}
				<Button size="sm" variant="destructive" disabled={batchDeleting} onclick={removeSelected}>
					{batchDeleting ? t('Menghapus...') : `${t('Hapus terpilih')} (${selected.size})`}
				</Button>
			{/if}
			<Input
				bind:value={query}
				type="search"
				placeholder="Search product, origin, HS..."
				class="max-w-xs"
			/>
		</div>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#if !loaded}
			{#each [1,2,3,4,5,6] as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-8 w-12" />
					</div>
					<Skeleton class="mt-4 h-6 w-40" />
					<Skeleton class="mt-1 h-4 w-32" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3">
							<Skeleton class="h-3 w-8" />
							<Skeleton class="mt-1 h-4 w-16" />
						</div>
						<div class="rounded-lg border bg-muted/40 p-3">
							<Skeleton class="h-3 w-8" />
							<Skeleton class="mt-1 h-4 w-16" />
						</div>
						<div class="rounded-lg border bg-muted/40 p-3">
							<Skeleton class="h-3 w-12" />
							<Skeleton class="mt-1 h-4 w-12" />
						</div>
						<div class="rounded-lg border bg-muted/40 p-3">
							<Skeleton class="h-3 w-12" />
							<Skeleton class="mt-1 h-4 w-16" />
						</div>
					</div>
				</Card>
			{/each}
		{:else if filteredProducts.length === 0}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No product matched your filter.')}</div>
		{:else}
			{#each filteredProducts as product}
			<Card class={`relative transition-all hover:border-ring/40 hover:shadow-md ${selected.has(product.id) ? 'border-primary ring-2 ring-primary/30' : ''}`}>
				<div class="absolute top-3 right-3 z-10">
					<input
						type="checkbox"
						class="size-4"
						checked={selected.has(product.id)}
						onchange={() => toggleSelected(product.id)}
						onclick={(e) => e.stopPropagation()}
					/>
				</div>
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
					<div class="mt-3 flex items-center justify-end gap-2">
						<Button size="sm" variant="outline" href={`/products/${product.id}/edit`}>{t('Edit')}</Button>
						<Button size="sm" variant="destructive" disabled={deleting === product.id} onclick={(e) => { e.preventDefault(); removeProduct(product.id, product.name); }}>
							{deleting === product.id ? '...' : 'Hapus'}
						</Button>
					</div>
				</a>
			</Card>
		{/each}
		{/if}
	</div>
	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
</AppShell>