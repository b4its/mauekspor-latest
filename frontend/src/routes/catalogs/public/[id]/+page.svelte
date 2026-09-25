<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let catalog = $derived(data.catalog);
	let images = $derived((catalog.images ?? []) as Array<{ image_url?: string; alt_text?: string }>);
</script>

<svelte:head>
	<title>{catalog.title} | MauEkspor</title>
</svelte:head>

<AppShell title={catalog.title} eyebrow={catalog.targetMarket}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<div class="flex flex-wrap items-center gap-2">
				<Badge>{catalog.status}</Badge>
				<Badge variant="outline">{catalog.targetMarket}</Badge>
			</div>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{catalog.title}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{catalog.description}</CardDescription>
		</CardHeader>
	</Card>

	{#if images.length > 0}
		<div class="grid gap-3 sm:grid-cols-3">
			{#each images as img, i (i)}
				{#if img.image_url}
					<img src={img.image_url} alt={img.alt_text ?? catalog.title} class="h-40 w-full rounded-lg border object-cover" />
				{/if}
			{/each}
		</div>
	{/if}

	<Card>
		<CardHeader><CardTitle>{t('Spesifikasi & perdagangan')}</CardTitle></CardHeader>
		<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('MOQ')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.moq}</strong></div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Waktu tunggu')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.leadTime}</strong></div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Rentang harga')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.priceRange || currency.format(0)}</strong></div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{(catalog.incoterms ?? []).join(', ') || '—'}</strong></div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Penjual')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.sellerName || catalog.productName || '—'}</strong></div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Produk')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.productName || catalog.productId}</strong></div>
		</CardContent>
	</Card>

	{#if (catalog.highlights ?? []).length > 0}
		<Card>
			<CardHeader><CardTitle>{t('Sorotan')}</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2">
				{#each catalog.highlights ?? [] as highlight}
					<Badge variant="secondary">{highlight}</Badge>
				{/each}
			</CardContent>
		</Card>
	{/if}

	<div class="flex flex-wrap gap-2">
		<Button href="/catalogs/public" variant="outline">{t('Kembali ke katalog publik')}</Button>
	</div>
</AppShell>
