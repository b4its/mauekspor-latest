<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { catalogs as seedCatalogs, forwarders as seedForwarders } from '$lib/data/trade';
	import { listForwarderCatalogs } from '$lib/api/catalogs';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { Catalog } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const forwarder = seedForwarders[0];
	let query = $state('');
	let catalogs = createRemoteList<Catalog>(listForwarderCatalogs, seedCatalogs);
	catalogs.load();

	let filteredCatalogs = $derived(
		catalogs.items.filter((catalog) => {
			const matchesQuery = [catalog.title, catalog.targetMarket, catalog.status]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return catalog.status === 'Published' && matchesQuery;
		})
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredCatalogs ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredCatalogs?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('Katalog Forwarder')} | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarder Catalogs" eyebrow={t('Inventaris kuotasi freight')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(forwarder.status))}>{forwarder.name}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Katalog ekspor aktif yang tersedia untuk kuotasi.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Katalog yang diterbitkan mewakili inventaris siap-kuotasi yang dapat dilayani forwarder ini di seluruh jalur yang dicakup.')}
			</CardDescription>
		</CardHeader>
	</Card>

	<div class="flex flex-wrap items-center justify-end gap-3">
		<Input bind:value={query} type="search" placeholder={t('Cari katalog yang diterbitkan...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each pagedItems as catalog}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/catalogs/${catalog.id}`} class="grid h-full gap-3 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(catalog.status))}>{catalog.status}</Badge>
						<Badge variant="outline">{forwarder.lanes.length} {t('jalur')}</Badge>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{catalog.title}</h3>
					<p class="text-sm text-muted-foreground">{catalog.targetMarket}</p>
					<div class="grid gap-2 sm:grid-cols-3">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('MOQ')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.moq}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Waktu tunggu')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.leadTime}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Harga')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.priceRange}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada katalog yang diterbitkan cocok.')}</div>
		{/each}
	</div>
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredCatalogs?.length ?? 0} />

</AppShell>
