<script lang="ts">
	import { page } from '$app/state';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { createExportAnalysis, listCountries } from '$lib/api/export-analysis';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { Product } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';

	let products = createRemoteList<Product>(listProducts, seedProducts);
	let countries = $state<{ country_code: string; country_name: string; region: string; regulationsCount?: number }[]>([]);
	let productId = $state('');
	let destination = $state('');
	let created = $state(false);
	let createdId = $state('');
	let creating = $state(false);
	let error = $state('');

	$effect(() => {
		products.load();
		listCountries()
			.then((res) => {
				countries = res.data;
				const destParam = page.url.searchParams.get('destination') || page.url.searchParams.get('country');
				if (destParam && !destination) {
					destination = destParam.toUpperCase();
				}
			})
			.catch(() => { error = t('Gagal memuat daftar negara.'); });
	});

	$effect(() => {
		if (products.items.length > 0 && !productId) {
			const prodParam = page.url.searchParams.get('productId') || page.url.searchParams.get('product');
			const hsParam = page.url.searchParams.get('hsCode');
			if (prodParam) {
				const found = products.items.find((p) => p.id === prodParam || p.id.toLowerCase() === prodParam.toLowerCase());
				if (found) productId = found.id;
			} else if (hsParam) {
				const cleanHs = hsParam.replace(/\./g, '');
				const found = products.items.find((p) => p.hs && p.hs.replace(/\./g, '').startsWith(cleanHs));
				if (found) productId = found.id;
			}
		}
	});

	let valid = $derived(productId && destination);
	let selected = $derived(products.items.find((product) => product.id === productId)?.name);
	let selectedCountry = $derived(countries.find((c) => c.country_code === destination)?.country_name ?? destination);
	let selectedProduct = $derived(products.items.find((product) => product.id === productId));
	let notEnriched = $derived(selectedProduct ? selectedProduct.status === 'Needs HS Review' : false);

	async function create() {
		error = '';
		if (!valid) {
			error = t('Pilih produk dan negara tujuan untuk memulai analisis.');
			return;
		}
		creating = true;
		try {
			const res = await createExportAnalysis({ productId, destination });
			created = true;
			if (res.data?.id) {
				createdId = res.data.id;
			}
		} catch {
			error = t('Gagal menjalankan analisis. Periksa apakah analisis untuk produk & negara ini sudah ada.');
		} finally {
			creating = false;
		}
	}

</script>

<svelte:head>
	<title>{t('Analisis Ekspor Baru')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Export Analysis')} eyebrow={t('Start market analysis')}>
	<Card class="panel-hero p-6 md:p-8">
		<Badge variant="secondary">{t('Analisis baru')}</Badge>
		<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
			{t('Pilih produk dan negara tujuan untuk memulai.')}
		</CardTitle>
		<CardContent class="mt-3 p-0 text-muted-foreground">
			{t('Analisis menjalankan compliance checker (bahan, spesifikasi, kemasan), membuat snapshot produk & regulasi, lalu menghitung skor kesiapan — disimpan ke backend.')}
		</CardContent>
	</Card>

	{#if created}
		<Card class="mt-4">
			<CardHeader>
				<Badge variant="secondary" class="w-fit">{t('Analisis dibuat')}</Badge>
				<CardTitle class="text-2xl tracking-tight">{selected} to {selectedCountry}</CardTitle>
			</CardHeader>
			<CardContent class="flex flex-wrap items-center gap-2.5">
				<p class="w-full text-sm leading-relaxed text-muted-foreground">
					{t('Analisis dibuat dan siap direview di backend.')}
				</p>
				{#if createdId}
					<Button href={`/export-analysis/${createdId}`}>{t('Buka Hasil Analisis')}</Button>
				{/if}
				<Button variant="outline" href="/export-analysis">{t('Lihat semua analisis')}</Button>
				<Button variant="outline" href="/export-analysis/compare">{t('Bandingkan pasar')}</Button>
			</CardContent>

		</Card>
	{:else}
		<form
			class="mt-4 grid gap-4 rounded-xl border bg-card p-6 sm:grid-cols-2"
			onsubmit={(event) => { event.preventDefault(); create(); }}
		>
			<div class="grid gap-2">
				<Label for="ea-product">{t('Produk')}</Label>
				<SearchableSelect
					bind:value={productId}
					placeholder={t('Pilih produk...')}
					options={products.items.map((p) => ({ value: p.id, label: p.name, sub: p.hs ? `HS ${p.hs}` : '' }))}
				/>
				{#if notEnriched}
					<p class="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs font-bold text-amber-700">
						{t('Produk belum di-enrich (HS code belum pasti). Jalankan AI enrichment di halaman produk agar hasil analisis lebih akurat.')}
					</p>
				{/if}
			</div>
			<div class="grid gap-2">
				<Label for="ea-destination" id="ea-destination-label">{t('Pasar tujuan')}</Label>
				<SearchableSelect
					id="ea-destination"
					labelledby="ea-destination-label"
					bind:value={destination}
					placeholder={t('Pilih tujuan...')}
					options={countries.map((c) => ({ value: c.country_code, label: c.country_name, sub: `${c.country_code} — ${c.region}` }))}
				/>
			</div>

			{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive sm:col-span-2" role="alert">{error}</p>{/if}

			<div class="flex gap-2.5 sm:col-span-2">
				<Button variant="outline" href="/export-analysis">{t('Batal')}</Button>
				<Button type="submit" disabled={creating}>{creating ? t('Menjalankan...') : t('Jalankan analisis')}</Button>
			</div>
		</form>
	{/if}
</AppShell>
