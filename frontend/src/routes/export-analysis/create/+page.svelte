<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { products } from '$lib/data/trade';
	import { createExportAnalysis } from '$lib/api/export-analysis';

	const destinations = ['Japan', 'Germany', 'Singapore', 'United States', 'Australia', 'United Arab Emirates'];
	let productId = $state('');
	let destination = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let valid = $derived(productId && destination);

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
			error = 'Gagal menjalankan analisis.';
		} finally {
			creating = false;
		}
	}

	let selected: string | undefined = $derived(products.find((product) => product.id === productId)?.name);
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
			The analysis job will produce HS classification, duty estimates, restrictions, and regulation
			recommendations, lalu disimpan ke backend.
		</CardContent>
	</Card>

	{#if created}
		<Card class="mt-4">
			<CardHeader>
				<Badge variant="secondary" class="w-fit">Analysis started</Badge>
				<CardTitle class="text-2xl tracking-tight">{selected} to {destination}</CardTitle>
			</CardHeader>
			<CardContent class="flex flex-wrap items-center gap-2.5">
				<p class="w-full text-sm leading-relaxed text-muted-foreground">
					Analisis dibuat di backend.
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
					{#each products as product}<option value={product.id}>{product.name}</option>{/each}
				</NativeSelect>
			</div>
			<div class="grid gap-2">
				<Label>Destination market</Label>
				<NativeSelect bind:value={destination} class="w-full">
					<option value="">Select destination...</option>
					{#each destinations as market}<option value={market}>{market}</option>{/each}
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