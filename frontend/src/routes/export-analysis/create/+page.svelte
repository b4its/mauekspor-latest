<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { createExportAnalysis, listCountries } from '$lib/api/export-analysis';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { Product } from '$lib/data/trade';

	let products = createRemoteList<Product>(listProducts, seedProducts);
	let countries = $state<{ country_code: string; country_name: string; region: string; regulationsCount?: number }[]>([]);
	let productId = $state('');
	let destination = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	$effect(() => {
		products.load();
		listCountries()
			.then((res) => (countries = res.data))
			.catch(() => {});
	});

	let valid = $derived(productId && destination);
	let selected = $derived(products.items.find((product) => product.id === productId)?.name);
	let selectedCountry = $derived(countries.find((c) => c.country_code === destination)?.country_name ?? destination);

	async function create() {
		error = '';
		if (!valid) {
			error = 'Pilih produk dan negara tujuan untuk memulai analisis.';
			return;
		}
		creating = true;
		try {
			await createExportAnalysis({ productId, destination });
			created = true;
		} catch {
			error = 'Gagal menjalankan analisis. Periksa apakah analisis untuk produk & negara ini sudah ada.';
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>New Export Analysis | MauEkspor</title>
</svelte:head>

<AppShell title="Export Analysis" eyebrow="Start market analysis">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<Badge variant="secondary">New analysis</Badge>
		<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
			Pick a product and a destination to begin.
		</CardTitle>
		<CardContent class="mt-3 p-0 text-muted-foreground">
			Analisis menjalankan compliance checker (bahan, spesifikasi, kemasan), membuat snapshot produk &
			regulasi, lalu menghitung skor kesiapan — disimpan ke backend.
		</CardContent>
	</Card>

	{#if created}
		<Card class="mt-4">
			<CardHeader>
				<Badge variant="secondary" class="w-fit">Analysis created</Badge>
				<CardTitle class="text-2xl tracking-tight">{selected} to {selectedCountry}</CardTitle>
			</CardHeader>
			<CardContent class="flex flex-wrap items-center gap-2.5">
				<p class="w-full text-sm leading-relaxed text-muted-foreground">
					Analisis dibuat dan siap direview di backend.
				</p>
				<Button href="/export-analysis">View analyses</Button>
				<Button variant="outline" href="/export-analysis/compare">Compare markets</Button>
			</CardContent>
		</Card>
	{:else}
		<form
			class="mt-4 grid gap-4 rounded-xl border bg-card p-6 sm:grid-cols-2"
			onsubmit={(event) => { event.preventDefault(); create(); }}
		>
			<div class="grid gap-2">
				<Label>Product</Label>
				<NativeSelect bind:value={productId} class="w-full">
					<option value="">Select product...</option>
					{#each products.items as product}<option value={product.id}>{product.name} (HS {product.hs})</option>{/each}
				</NativeSelect>
			</div>
			<div class="grid gap-2">
				<Label>Destination market</Label>
				<NativeSelect bind:value={destination} class="w-full">
					<option value="">Select destination...</option>
					{#each countries as country}<option value={country.country_code}>{country.country_name} ({country.country_code}) — {country.region}</option>{/each}
				</NativeSelect>
			</div>

			{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive sm:col-span-2">{error}</p>{/if}

			<div class="flex gap-2.5 sm:col-span-2">
				<Button variant="outline" href="/export-analysis">Cancel</Button>
				<Button type="submit" disabled={creating}>{creating ? 'Running...' : 'Run analysis'}</Button>
			</div>
		</form>
	{/if}
</AppShell>
