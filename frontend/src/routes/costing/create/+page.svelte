<script lang="ts">
	import { page } from '$app/state';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';
	import CountrySelect from '$lib/components/CountrySelect.svelte';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { products as seedProducts, projects as seedProjects } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { createCostingScenario } from '$lib/api/costing';
	import { t } from '$lib/i18n.svelte';

	let projects = createRemoteList(listTradeProjects, seedProjects);
	let products = createRemoteList(listProducts, seedProducts);
	projects.load();
	products.load();

	let projectId = $state('');
	let productId = $state('');
	let title = $state('');
	let destination = $state('');
	let incoterm = $state('FOB');
	let targetMargin = $state('22');
	let created = $state(false);
	let createdId = $state('');
	let creating = $state(false);
	let error = $state('');

	$effect(() => {
		const destParam = page.url.searchParams.get('destination') || page.url.searchParams.get('country');
		if (destParam && !destination) destination = destParam;

		const projParam = page.url.searchParams.get('projectId');
		if (projParam && !projectId) projectId = projParam;

		const prodParam = page.url.searchParams.get('productId') || page.url.searchParams.get('product');
		if (prodParam && !productId) productId = prodParam;
	});

	const incoterms = ['EXW', 'FOB', 'CIF', 'DAP'];

	let valid = $derived(title.trim().length > 3 && productId && destination.trim().length > 1 && Number(targetMargin) > 0);

	async function create() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib: judul, produk, destination, dan target margin.');
			return;
		}
		creating = true;
		try {
			const res = await createCostingScenario({
				title,
				projectId,
				productId,
				incoterm: incoterm as 'EXW' | 'FOB' | 'CIF' | 'DAP',
				margin: Number(targetMargin),
				destination
			});
			created = true;
			if (res.data?.id) {
				createdId = res.data.id;
			}
		} catch {
			error = t('Gagal membuat skenario costing.');
		} finally {
			creating = false;
		}
	}

</script>

<svelte:head>
	<title>{t('Buat Skenario Costing')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Costing')} eyebrow={t('Create costing scenario')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Model harga')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Model margin dan biaya landed untuk sebuah pasar.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Mencakup EXW hingga DAP, kurs, freight, asuransi, dan biaya tujuan. Skenario disimpan ke backend.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card>
			<CardContent class="grid gap-2 p-6">
				<Badge variant="secondary" class="w-fit">{t('Skenario dibuat')}</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{title}</h3>
				<p class="text-sm text-muted-foreground">{destination} · {incoterm} · {t('margin target')} {targetMargin}%. {t('Skenario tersimpan di backend.')}</p>
				<div class="mt-2 flex flex-wrap gap-2.5">
					{#if createdId}
						<Button href={`/costing/${createdId}`}>{t('Buka Skenario Costing')}</Button>
					{/if}
					<Button variant="outline" href="/costing">{t('Kembali ke costing')}</Button>
				</div>
			</CardContent>
		</Card>

	{:else}
		<Card>
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); create(); }}>
				<div class="grid gap-2">
					<Label for="cost-title">{t('Judul skenario')}</Label>
					<Input id="cost-title" bind:value={title} placeholder="Japan Coffee FOB Base Case" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="cost-project" id="cost-project-label">{t('Proyek')}</Label>
						<SearchableSelect id="cost-project" labelledby="cost-project-label" bind:value={projectId} options={projects.items.map((p) => ({ value: p.id, label: p.name }))} />
					</div>
					<div class="grid gap-2">
						<Label for="cost-product" id="cost-product-label">{t('Produk')}</Label>
						<SearchableSelect id="cost-product" labelledby="cost-product-label" bind:value={productId} options={products.items.map((p) => ({ value: p.id, label: p.name, sub: p.hs ? `HS ${p.hs}` : '' }))} />
					</div>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="cost-destination">{t('Tujuan')}</Label>
						<CountrySelect id="cost-destination" bind:value={destination} />
					</div>
					<div class="grid gap-2">
						<Label for="cost-incoterm" id="cost-incoterm-label">{t('Incoterm')}</Label>
						<SearchableSelect id="cost-incoterm" labelledby="cost-incoterm-label" bind:value={incoterm} options={incoterms.map((i) => ({ value: i, label: i }))} />
					</div>
				</div>
				<div class="grid gap-2">
					<Label for="cost-margin">{t('Target margin %')}</Label>
					<Input id="cost-margin" bind:value={targetMargin} inputmode="decimal" />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href="/costing">{t('Batal')}</Button>
					<Button type="submit" disabled={creating}>{creating ? t('Membuat...') : t('Buat draf skenario')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>
