<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { quotations as seedQuotations } from '$lib/data/trade';
	import { listQuotations, createQuotation } from '$lib/api/quotations';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'In Review', 'Revision Needed', 'Accepted'];
	let activeFilter = $state('All');
	let query = $state('');
	let error = $state('');
	let message = $state('');
	let showForm = $state(false);
	let creating = $state(false);
	let formError = $state('');
	let fBuyer = $state('');
	let fSupplier = $state('');
	let fValue = $state('');
	let fIncoterm = $state('FOB');
	let fCurrency = $state('USD');
	let fValidUntil = $state('');
	let fMargin = $state('');

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

	function openCreate() {
		formError = '';
		fBuyer = '';
		fSupplier = '';
		fValue = '';
		fIncoterm = 'FOB';
		fCurrency = 'USD';
		fValidUntil = '';
		fMargin = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fBuyer.trim()) {
			formError = t('Buyer wajib diisi.');
			return;
		}
		creating = true;
		try {
			await createQuotation({
				buyer: fBuyer.trim(),
				supplier: fSupplier.trim(),
				value: Number(fValue) || 0,
				incoterm: fIncoterm,
				currency: fCurrency,
				validUntil: fValidUntil,
				margin: Number(fMargin) || 0
			});
			await quotations.load();
			message = `Quotation "${fBuyer.trim()}" dibuat.`;
			showForm = false;
			fBuyer = '';
			fSupplier = '';
			fValue = '';
			fValidUntil = '';
			fMargin = '';
		} catch {
			formError = t('Gagal membuat quotation.');
		} finally {
			creating = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredQuotations ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredQuotations?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Quotations')} | MauEkspor</title>
</svelte:head>

<AppShell title="Quotations" eyebrow={t('Commercial offer management')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Incoterm clarity')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Create traceable export quotations with cost and validity control.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Separate EXW, FOB, CIF, landed-cost assumptions, freight validity, currency, named place, margin, and revision history.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create quotation')}</Button>
			<Badge variant="secondary">{t('Pipeline')} {currency.format(totalValue)}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Buyer')}
						<Input bind:value={fBuyer} placeholder="Hikari Foods Co." />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Supplier')}
						<Input bind:value={fSupplier} placeholder="PT Kopi Gayo Nusantara" />
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nilai')}
						<Input bind:value={fValue} type="number" placeholder="0" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Incoterm')}
						<select bind:value={fIncoterm} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['FOB', 'CIF', 'EXW', 'DAP'] as term}
								<option value={term}>{term}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Mata uang')}
						<select bind:value={fCurrency} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['USD', 'IDR', 'EUR'] as cur}
								<option value={cur}>{cur}</option>
							{/each}
						</select>
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Valid until')}
						<Input bind:value={fValidUntil} type="date" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Margin')}
						<Input bind:value={fMargin} type="number" placeholder="0" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : t('Simpan quotation')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if quotations.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{quotations.error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search quotation, buyer, incoterm...')} class="w-[min(390px,100%)]" />
	</div>

	{#if quotations.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-7 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-1/2" />
					<Skeleton class="mt-2 h-4 w-2/3" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as quote}
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
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredQuotations?.length ?? 0} />

</AppShell>