<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '$lib/components/ui/table/index.js';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { listCountries, compareExportAnalyses } from '$lib/api/export-analysis';
	import type { CompareResult } from '$lib/api/export-analysis';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { Product } from '$lib/data/trade';

	let products = createRemoteList<Product>(listProducts, seedProducts);
	let countries = $state<{ country_code: string; country_name: string }[]>([]);
	let selectedProductId = $state('');
	let selectedCodes = $state<string[]>([]);
	let results = $state<CompareResult[] | null>(null);
	let comparing = $state(false);
	let error = $state('');
	let productName = $state('');

	$effect(() => {
		products.load();
		listCountries()
			.then((res) => (countries = res.data))
			.catch(() => {});
	});

	function toggleCountry(code: string) {
		if (selectedCodes.includes(code)) {
			selectedCodes = selectedCodes.filter((c) => c !== code);
		} else if (selectedCodes.length < 5) {
			selectedCodes = [...selectedCodes, code];
		}
	}

	async function runCompare() {
		error = '';
		if (!selectedProductId || selectedCodes.length < 2) {
			error = 'Pilih 1 produk dan minimal 2 negara.';
			return;
		}
		comparing = true;
		try {
			const res = await compareExportAnalyses({ product_id: selectedProductId, country_codes: selectedCodes });
			results = res.data.results;
			productName = res.data.product.name;
		} catch {
			error = 'Gagal menjalankan perbandingan.';
		} finally {
			comparing = false;
		}
	}

	function scoreTone(score: number) {
		if (score >= 80) return 'default';
		if (score >= 50) return 'outline';
		return 'destructive';
	}

	const bestCountry = $derived(results && results.length > 0 ? results[0].country : '');
</script>

<svelte:head>
	<title>Compare Markets | MauEkspor</title>
</svelte:head>

<AppShell title="Compare Markets" eyebrow="Decision support">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Decision support</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Bandingkan 2-5 negara untuk satu produk.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Pilih produk yang sudah di-enrich, pilih 2-5 negara tujuan, lalu bandingkan skor kesiapan, grade, dan isu kepatuhan.
			</CardDescription>
		</CardHeader>
	</Card>

	<Card>
		<CardContent class="grid gap-4 p-6">
			<div class="grid gap-2">
				<label class="text-xs font-bold uppercase tracking-wide text-muted-foreground" for="cmp-product">1. Pilih produk</label>
				<select id="cmp-product" class="h-10 rounded-md border bg-background px-3 text-sm" bind:value={selectedProductId}>
					<option value="">— Pilih produk —</option>
					{#each products.items as product}
						<option value={product.id}>{product.name} (HS {product.hs})</option>
					{/each}
				</select>
			</div>
			<div class="grid gap-2">
				<label class="text-xs font-bold uppercase tracking-wide text-muted-foreground" for="cmp-countries">
					2. Pilih negara (min 2, maks 5) — {selectedCodes.length} dipilih
				</label>
				<div class="flex flex-wrap gap-2">
					{#each countries as country}
						<button
							class={`rounded-full border px-3.5 py-1.5 text-xs font-bold transition-colors ${
								selectedCodes.includes(country.country_code)
									? 'border-ring bg-primary/10 text-primary'
									: 'bg-muted/30 text-muted-foreground hover:bg-muted/60'
							}`}
							onclick={() => toggleCountry(country.country_code)}
						>
							{country.country_name} ({country.country_code})
						</button>
					{/each}
				</div>
			</div>
			<Button onclick={runCompare} disabled={comparing || selectedCodes.length < 2 || !selectedProductId}>
				{comparing ? 'Membandingkan...' : 'Bandingkan'}
			</Button>
			{#if error}
				<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
		</CardContent>
	</Card>

	{#if results}
		<Card class="overflow-x-auto p-0">
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>Metric</TableHead>
						{#each results as result}
							<TableHead class="text-center">
								{result.country}
								{#if result.country === bestCountry}
									<Badge variant="secondary" class="ml-1">Terbaik ⭐</Badge>
								{/if}
							</TableHead>
						{/each}
					</TableRow>
				</TableHeader>
				<TableBody>
					<TableRow>
						<TableCell class="font-semibold text-muted-foreground">Produk</TableCell>
						{#each results as _}
							<TableCell class="text-center">{productName}</TableCell>
						{/each}
					</TableRow>
					<TableRow>
						<TableCell class="font-semibold text-muted-foreground">Score</TableCell>
						{#each results as result}
							<TableCell class="text-center">
								<Badge variant={scoreTone(result.score)}>{result.score}</Badge>
							</TableCell>
						{/each}
					</TableRow>
					<TableRow>
						<TableCell class="font-semibold text-muted-foreground">Grade</TableCell>
						{#each results as result}
							<TableCell class="text-center">{result.grade}</TableCell>
						{/each}
					</TableRow>
					<TableRow>
						<TableCell class="font-semibold text-muted-foreground">Isu kritis</TableCell>
						{#each results as result}
							<TableCell class="text-center">{result.critical_issues}</TableCell>
						{/each}
					</TableRow>
					<TableRow>
						<TableCell class="font-semibold text-muted-foreground">Rekomendasi</TableCell>
						{#each results as result}
							<TableCell class="max-w-[240px] text-xs leading-relaxed text-muted-foreground">{result.recommendation}</TableCell>
						{/each}
					</TableRow>
				</TableBody>
			</Table>
		</Card>
	{/if}
</AppShell>
