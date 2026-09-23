<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { products as seedProducts, suppliers as seedSuppliers } from '$lib/data/trade';
	import { listSuppliers } from '$lib/api/suppliers';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { requestSupplierEvidence } from '$lib/api/suppliers';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Verified', 'In Review', 'Needs Evidence'];
	let activeFilter = $state('All');
	let query = $state('');
	let requested = $state(false);
	let requesting = $state(false);
	let error = $state('');

	let suppliers = createRemoteList(listSuppliers, seedSuppliers);
	let products = createRemoteList(listProducts, seedProducts);
	$effect(() => {
		suppliers.load();
		products.load();
	});

	let filteredSuppliers = $derived(
		suppliers.items.filter((supplier) => {
			const names = supplier.productIds.map((id) => products.items.find((product) => product.id === id)?.name ?? id).join(' ');
			return (
				(activeFilter === 'All' || supplier.status === activeFilter) &&
				[supplier.name, supplier.location, supplier.category, names].join(' ').toLowerCase().includes(query.trim().toLowerCase())
			);
		})
	);
	let verifiedCount = $derived(suppliers.items.filter((supplier) => supplier.status === 'Verified').length);
	let avgCapability = $derived(Math.round(suppliers.items.reduce((sum, supplier) => sum + supplier.capabilityScore, 0) / (suppliers.items.length || 1)));
	function productNames(ids: string[]) {
		return ids.map((id) => products.items.find((product) => product.id === id)?.name ?? id).join(', ');
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleEvidence() {
		error = '';
		requesting = true;
		try {
			const target = suppliers.items.find((supplier) => supplier.status === 'Needs Evidence') ?? suppliers.items[0];
			if (target) await requestSupplierEvidence(target.id);
			requested = true;
		} catch {
			error = t('Gagal meminta bukti kepatuhan.');
		} finally {
			requesting = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Pemasok')} | MauEkspor</title>
</svelte:head>

<AppShell title="Suppliers" eyebrow={t('Exporter and supplier network')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Supplier readiness')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Verify supplier capability before RFQ matching and order execution.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Track capacity, certificates, quality signals, compliance evidence, and operational risks across the export supplier network.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleEvidence} disabled={requesting}>{requested ? t('Evidence requested') : requesting ? t('Requesting...') : t('Request evidence')}</Button>
			<Badge variant="secondary">{t('Verified')} {verifiedCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if requested}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Permintaan bukti dikirim ke backend.')}</strong>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search supplier, product, location...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Suppliers')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{suppliers.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Verified')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{verifiedCount}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Avg capability')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{avgCapability}%</strong></CardContent></Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredSuppliers as supplier}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/suppliers/${supplier.id}`} class="grid h-full gap-3 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(supplier.status))}>{supplier.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{supplier.capabilityScore}%</strong>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{supplier.name}</h3>
					<p class="text-sm text-muted-foreground">{supplier.category} · {supplier.location}</p>
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Products')}<strong class="mt-1 block text-sm font-bold text-foreground">{productNames(supplier.productIds)}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Capacity')}<strong class="mt-1 block text-sm font-bold text-foreground">{supplier.capacity}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Lead time')}<strong class="mt-1 block text-sm font-bold text-foreground">{supplier.leadTime}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Next audit')}<strong class="mt-1 block text-sm font-bold text-foreground">{supplier.nextAudit}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No supplier matched your search.')}</div>
		{/each}
	</div>
</AppShell>
