<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { enrichProduct, deleteProduct } from '$lib/api/products';

	let { data } = $props();
	let enriching = $state(false);
	let enriched = $state(false);
	let deleting = $state(false);

	async function runEnrichment() {
		enriching = true;
		try {
			data.product = (await enrichProduct(data.product.id)).data;
		} catch {
			await new Promise((resolve) => setTimeout(resolve, 300));
		} finally {
			enriching = false;
			enriched = true;
		}
	}

	async function handleDelete() {
		if (!confirm('Hapus produk ini?')) return;
		deleting = true;
		try {
			await deleteProduct(data.product.id);
			window.location.href = '/products';
		} catch {
			deleting = false;
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.product.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.product.id} eyebrow={data.product.name}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.product.status))}>{data.product.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.product.name}
				</CardTitle>
				<CardDescription class="mt-2">{data.product.category} from {data.product.origin}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Product readiness</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{data.product.readiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Export Data Sheet</CardTitle>
					<CardDescription>Core information used for HS classification, compliance analysis, catalog, and quotation.</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/products/${data.product.id}/edit`}>Edit product</Button>
					<Button variant="outline" href={`/products/${data.product.id}/enrich`}>Override AI enrichment</Button>
					<Button disabled={enriching} onclick={runEnrichment}>
						{enriching ? 'Generating...' : enriched ? 'AI enrichment updated' : 'Run AI enrichment'}
					</Button>
					<Button variant="destructive" disabled={deleting} onclick={handleDelete}>Delete</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					HS Code <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.hs}{data.product.hsConfidence ? ` (${data.product.hsConfidence}% conf)` : ''}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					SKU <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.sku ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Packaging <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.packaging}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Net weight <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.netWeight}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Gross weight <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.grossWeight}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					MOQ <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.moq}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Lead time <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.leadTime}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>Certificates</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5 p-0 pt-4">
				{#each data.product.certificates ?? [] as certificate}
					<Badge variant="outline">{certificate}</Badge>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>AI Marketing</CardTitle></CardHeader>
			<CardContent class="grid gap-2 p-0 pt-4">
				<Button variant="outline" href="/marketing" class="w-fit">Market Intelligence & Pricing</Button>
				{#if data.product.status === 'Enriched'}
					<span class="text-xs font-semibold text-muted-foreground">Produk siap dianalisis pasar (HS & SKU tersedia).</span>
				{:else}
					<span class="text-xs font-semibold text-muted-foreground">Jalankan enrichment dulu sebelum analisis pasar.</span>
				{/if}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">AI guardrail</Badge>
				<CardTitle>Classification note</CardTitle>
			</CardHeader>
			<CardContent class="p-0 pt-4">
				<p class="leading-relaxed text-muted-foreground">
					HS recommendation must be confirmed by a human reviewer before it is used on commercial
					invoice, packing list, or certificate of origin.
				</p>
				{#if enriched}
					<p class="mt-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">
						Enrichment diproses di backend.
					</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>