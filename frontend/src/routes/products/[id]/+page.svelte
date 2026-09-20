<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { enrichProduct, deleteProduct, generateCatalogDescription, type CatalogDescription } from '$lib/api/products';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let enriching = $state(false);
	let enriched = $state(false);
	let enrichError = $state('');
	let deleting = $state(false);
	let catalogDesc = $state<CatalogDescription | null>(null);
	let catalogLoading = $state(false);
	let catalogError = $state('');

	async function runEnrichment() {
		enriching = true;
		enrichError = '';
		try {
			data.product = (await enrichProduct(data.product.id)).data;
			enriched = true;
		} catch {
			enrichError = 'Gagal menjalankan enrichment.';
		} finally {
			enriching = false;
		}
	}

	async function handleDelete() {
		if (!confirm(t('Hapus produk ini?'))) return;
		deleting = true;
		try {
			await deleteProduct(data.product.id);
			window.location.href = '/products';
		} catch {
			deleting = false;
		}
	}

	async function handleGenerateCatalog() {
		catalogLoading = true;
		catalogError = '';
		catalogDesc = null;
		try {
			const res = await generateCatalogDescription(data.product.id);
			catalogDesc = res.data;
		} catch {
			catalogError = t('Gagal menghasilkan deskripsi katalog.');
		} finally {
			catalogLoading = false;
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
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.product.status))}>{data.product.status}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.product.name}
				</CardTitle>
				<CardDescription class="mt-2">{data.product.category} from {data.product.origin}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Product readiness')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{data.product.readiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Lembar Data Ekspor')}</CardTitle>
					<CardDescription>{t('Informasi inti yang digunakan untuk klasifikasi HS, analisis kepatuhan, katalog, dan kutipan harga.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/products/${data.product.id}/edit`}>{t('Edit produk')}</Button>
					<Button variant="outline" href={`/products/${data.product.id}/enrich`}>{t('Timpa enrichment AI')}</Button>
					<Button disabled={enriching} onclick={runEnrichment}>
						{enriching ? t('Memproses...') : enriched ? t('Enrichment AI diperbarui') : t('Jalankan enrichment AI')}
					</Button>
					<Button variant="destructive" disabled={deleting} onclick={handleDelete}>{t('Hapus')}</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kode HS')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.hs}{data.product.hsConfidence ? ` (${data.product.hsConfidence}% conf)` : ''}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					SKU <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.sku ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kemasan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.packaging}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Berat bersih')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.netWeight}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Berat kotor')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.grossWeight}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					MOQ <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.moq}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Waktu tunggu')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product.leadTime}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Sertifikat')}</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5 p-0 pt-4">
				{#each data.product.certificates ?? [] as certificate}
					<Badge variant="outline">{certificate}</Badge>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Pemasaran AI')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2 p-0 pt-4">
				<Button variant="outline" href="/marketing" class="w-fit">{t('Market Intelligence & Pricing')}</Button>
				<Button
					variant="outline"
					disabled={catalogLoading || data.product.status !== 'Enriched'}
					onclick={handleGenerateCatalog}
					class="w-fit"
				>
					{#if catalogLoading}
						<span class="inline-flex items-center gap-2">
							<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
							{t('Generating...')}
						</span>
					{:else}
						{catalogDesc ? t('Regenerate Deskripsi Katalog') : t('Generate Deskripsi Katalog AI')}
					{/if}
				</Button>
				{#if data.product.status === 'Enriched'}
					<span class="text-xs font-semibold text-muted-foreground">{t('Produk siap dianalisis pasar (HS & SKU tersedia).')}</span>
				{:else}
					<span class="text-xs font-semibold text-muted-foreground">{t('Jalankan enrichment dulu sebelum analisis pasar.')}</span>
				{/if}
				{#if catalogError}
					<p class="text-sm font-bold text-destructive">{catalogError}</p>
				{/if}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Pagar pembatas AI')}</Badge>
				<CardTitle>{t('Catatan klasifikasi')}</CardTitle>
			</CardHeader>
			<CardContent class="p-0 pt-4">
				<p class="leading-relaxed text-muted-foreground">
					{t('Rekomendasi HS harus dikonfirmasi oleh peninjau manusia sebelum digunakan pada invoice komersial, packing list, atau certificate of origin.')}
				</p>
				{#if enriched}
					<p class="mt-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">
						{t('Enrichment diproses di backend.')}
					</p>
				{/if}
			</CardContent>
		</Card>

		{#if catalogDesc}
			<Card class="md:col-span-2 border-primary/20">
				<CardHeader class="p-0">
					<Badge variant="outline" class="border-primary/30 text-primary w-fit">🤖 AI</Badge>
					<CardTitle class="mt-2">{t('Deskripsi Katalog AI')}</CardTitle>
					<CardDescription class="mt-1">{t('Deskripsi B2B yang dihasilkan AI untuk katalog ekspor produk ini.')}</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-4 p-0 pt-4">
					<div class="rounded-lg border bg-muted/30 p-4">
						<p class="text-sm font-semibold text-muted-foreground mb-2">{t('Deskripsi Ekspor')}</p>
						<p class="leading-relaxed">{catalogDesc.export_description}</p>
					</div>
					{#if catalogDesc.technical_specs?.length}
						<div class="rounded-lg border bg-muted/30 p-4">
							<p class="text-sm font-semibold text-muted-foreground mb-2">{t('Spesifikasi Teknis')}</p>
							<dl class="grid gap-2 sm:grid-cols-2">
								{#each catalogDesc.technical_specs as spec}
									<div>
										<dt class="text-xs font-bold text-muted-foreground">{spec.label}</dt>
										<dd class="text-sm font-medium">{spec.value}</dd>
									</div>
								{/each}
							</dl>
						</div>
					{/if}
					{#if catalogDesc.safety_info?.length}
						<div class="rounded-lg border bg-muted/30 p-4">
							<p class="text-sm font-semibold text-muted-foreground mb-2">{t('Informasi Keselamatan')}</p>
							<dl class="grid gap-2 sm:grid-cols-2">
								{#each catalogDesc.safety_info as info}
									<div>
										<dt class="text-xs font-bold text-muted-foreground">{info.label}</dt>
										<dd class="text-sm font-medium">{info.value}</dd>
									</div>
								{/each}
							</dl>
						</div>
					{/if}
				</CardContent>
			</Card>
		{/if}
	</div>
</AppShell>