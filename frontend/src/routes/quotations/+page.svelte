<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { quotations as seedQuotations } from '$lib/data/trade';
	import { listQuotations, createQuotation } from '$lib/api/quotations';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'In Review', 'Revision Needed', 'Accepted'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let quotations = createRemoteList(listQuotations, seedQuotations);
	$effect(() => {
		quotations.load();
	});

	let filteredQuotations = $derived(
		quotations.items.filter((quote) => {
			const matchesFilter = activeFilter === 'All' || quote.status === activeFilter;
			const matchesQuery = [quote.id, quote.buyer, quote.supplier, quote.incoterm, quote.rfqId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);
	let totalValue = $derived(quotations.items.reduce((sum, quote) => sum + quote.value, 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			const seed = seedQuotations[0];
			await createQuotation({
				rfqId: seed?.rfqId ?? 'rfq-001',
				incoterm: seed?.incoterm ?? 'FOB Tanjung Priok',
				value: seed?.value ?? 42800,
				currency: (seed?.currency as 'USD' | 'IDR') ?? 'USD',
				validUntil: seed?.validUntil ?? '2026-09-30'
			});
			created = true;
		} catch {
			error = t('Gagal membuat quotation.');
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>Quotations | MauEkspor</title>
</svelte:head>

<AppShell title="Quotations" eyebrow={t('Commercial offer management')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Incoterm clarity')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Create traceable export quotations with cost and validity control.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Separate EXW, FOB, CIF, landed-cost assumptions, freight validity, currency, named place, margin, and revision history.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? t('Quotation draft created') : creating ? t('Creating...') : t('Create quotation')}</Button>
			<Badge variant="secondary">{t('Pipeline')} {currency.format(totalValue)}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Quotation draft ready.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Quotation tersimpan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search quotation, buyer, incoterm...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredQuotations as quote}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/quotations/${quote.id}`} class="grid h-full gap-4 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(quote.status))}>{quote.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{quote.margin}%</strong>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{quote.id}</h3>
					<p class="text-sm text-muted-foreground">{quote.supplier} to {quote.buyer}</p>
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Value')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(quote.value)}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{quote.incoterm}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('RFQ')}<strong class="mt-1 block text-sm font-bold text-foreground">{quote.rfqId}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Valid until')}<strong class="mt-1 block text-sm font-bold text-foreground">{quote.validUntil}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No quotation matched your search.')}</div>
		{/each}
	</div>
</AppShell>