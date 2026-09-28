<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { quotations as seedQuotations } from '$lib/data/trade';
	import { listQuotations, createQuotation, acceptQuotation, deleteQuotation, batchDeleteQuotations } from '$lib/api/quotations';
	import { downloadFile } from '$lib/api/client';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone, toneVariant } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';
import Pagination from '$lib/components/Pagination.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
import SortSelect from '$lib/components/SortSelect.svelte';
import BulkActionsBar from '$lib/components/BulkActionsBar.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { sortBy, type SortDir } from '$lib/utils/sort';
import { createBulkSelection } from '$lib/utils/bulkSelection.svelte';
import { syncFiltersToUrl } from '$lib/utils/urlFilters';
import { page } from '$app/state';
	import { formatDate } from '$lib/utils/date';

	const filters = ['All', 'In Review', 'Revision Needed', 'Accepted'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'value', label: t('Nilai') },
		{ value: 'margin', label: t('Margin') },
		{ value: 'buyer', label: t('Buyer') },
		{ value: 'status', label: t('Status') },
		{ value: 'validUntil', label: t('Berlaku sampai') },
		{ value: 'id', label: 'ID' }
	];
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
		sortBy(
			quotations.items.filter((quote) => {
				const matchesFilter = activeFilter === 'All' || quote.status === activeFilter;
				const matchesQuery = [quote.id, quote.buyer, quote.supplier, quote.incoterm, quote.rfqId]
					.join(' ')
					.toLowerCase()
					.includes(query.trim().toLowerCase());
				return matchesFilter && matchesQuery;
			}),
			sortKey,
			sortDir
		)
	);
	let totalValue = $derived(quotations.items.reduce((sum, quote) => sum + quote.value, 0));


	let busyId = $state('');

	// Konfirmasi terpusat untuk hapus quotation (pengganti window.confirm).
	const confirm = createConfirmController();

	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter, sort: sortKey, dir: sortKey ? sortDir : '' };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '', sort: '', dir: '' }, ['query', 'status', 'sort', 'dir']), 250);
		return () => clearTimeout(syncTimer);
	});

	async function handleAccept(quote: { id: string }) {
		error = '';
		busyId = quote.id;
		try {
			const res = await acceptQuotation(quote.id);
			if (res.data) {
				quotations.upsert(res.data);
			} else {
				await quotations.load();
			}
			message = `Quotation ${quote.id} diterima.`;
		} catch {
			error = t('Gagal menerima quotation.');
		} finally {
			busyId = '';
		}
	}

	async function handleDelete(quote: { id: string }) {
		error = '';
		busyId = quote.id;
		try {
			await deleteQuotation(quote.id);
			quotations.remove(quote.id);
			message = `Quotation ${quote.id} dihapus.`;
		} catch {
			error = t('Gagal menghapus quotation.');
		} finally {
			busyId = '';
		}
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
			const res = await createQuotation({
				buyer: fBuyer.trim(),
				supplier: fSupplier.trim(),
				value: Number(fValue) || 0,
				incoterm: fIncoterm,
				currency: fCurrency,
				validUntil: fValidUntil,
				margin: Number(fMargin) || 0
			});
			if (res.data) {
				quotations.upsert(res.data);
			} else {
				await quotations.load();
			}
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
		sortKey;
		sortDir;
		paginationPage = 1;
	});

	// Aksi massal: pilih baris lalu hapus sekaligus.
	const bulk = createBulkSelection();
	let batchDeleting = $state(false);

	async function removeSelected() {
		if (bulk.count === 0) return;
		error = '';
		batchDeleting = true;
		try {
			const res = await batchDeleteQuotations(bulk.ids);
			bulk.clear();
			await quotations.load();
			message = `${res.data.deletedCount} ${t('kuotasi dihapus.')}`;
		} catch {
			error = t('Gagal menghapus kuotasi terpilih.');
		} finally {
			batchDeleting = false;
		}
	}

</script>

<svelte:head>
	<title>{t('Quotations')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Quotations')} eyebrow={t('Commercial offer management')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Incoterm clarity')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Create traceable export quotations with cost and validity control.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Separate EXW, FOB, CIF, landed-cost assumptions, freight validity, currency, named place, margin, and revision history.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create quotation')}</Button>
			<Button variant="outline" onclick={() => downloadFile('/quotations/export.csv', 'quotations.csv')}>{t('Export CSV')}</Button>
			<Button variant="outline" onclick={() => downloadFile('/quotations/export.xlsx', 'quotations.xlsx')}>{t('Excel (.xlsx)')}</Button>
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
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : t('Simpan quotation')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if quotations.error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{quotations.error}</p>
	{/if}

	{#if message}
		<p role="status" class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter === 'All' ? t('Semua') : label(filter)}</Button>
			{/each}
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<label class="flex cursor-pointer items-center gap-1.5 text-sm font-semibold text-muted-foreground">
				<input type="checkbox" class="size-4" checked={bulk.allOf(pagedItems.map((q) => q.id))} onchange={() => bulk.toggleAll(pagedItems.map((q) => q.id))} />
				{t('Pilih semua')}
			</label>
			<Input bind:value={query} type="search"
				aria-label={t('Search quotation, buyer, incoterm...')} placeholder={t('Search quotation, buyer, incoterm...')} class="w-[min(390px,100%)]" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
	</div>

	<BulkActionsBar
		count={bulk.count}
		busy={batchDeleting}
		noun={t('kuotasi')}
		ondelete={() => confirm.ask({
			title: t('Hapus kuotasi terpilih'),
			description: t('Kuotasi terpilih akan dihapus permanen dari workspace.'),
			detail: `${bulk.count} ${t('kuotasi')}`,
			action: removeSelected
		})}
		onclear={() => bulk.clear()}
	/>

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
				<Card class={`relative flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md ${bulk.has(quote.id) ? 'border-primary ring-2 ring-primary/30' : ''}`}>
					<div class="absolute top-4 right-4 z-10">
						<input type="checkbox" class="size-4" checked={bulk.has(quote.id)} aria-label={`${t('Pilih')} ${quote.id}`} onchange={() => bulk.toggle(quote.id)} onclick={(e) => e.stopPropagation()} />
					</div>
					<div class="grid gap-4 p-5">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(quote.status))}>{label(quote.status)}</Badge>
							<strong class="text-2xl font-bold tracking-tight mr-6">{quote.margin}%</strong>
						</div>
						<a href={`/quotations/${quote.id}`} class="block no-underline hover:underline">
							<h3 class="text-2xl font-bold tracking-tight text-foreground">{quote.id}</h3>
							<p class="text-sm text-muted-foreground">{quote.supplier} to {quote.buyer}</p>
						</a>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Value')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(quote.value)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{quote.incoterm}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('RFQ')}<strong class="mt-1 block text-sm font-bold text-foreground">{quote.rfqId}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Valid until')}<strong class="mt-1 block text-sm font-bold text-foreground">{formatDate(quote.validUntil)}</strong></div>
						</div>
					</div>
					<div class="flex items-center justify-between border-t bg-muted/10 px-5 py-3">
						<a href={`/quotations/${quote.id}`} class="text-xs font-semibold text-primary hover:underline">
							{t('Lihat detail')} &rarr;
						</a>
						<div class="flex items-center gap-1.5">
							{#if quote.status !== 'Accepted'}
								<Button
									variant="outline"
									size="sm"
									class="h-7 text-xs"
									disabled={busyId === quote.id}
									onclick={() => handleAccept(quote)}
								>
									{busyId === quote.id ? '...' : t('Terima')}
								</Button>
							{/if}
							<Button
								variant="ghost"
								size="sm"
								class="h-7 text-xs text-destructive hover:bg-destructive/10"
								disabled={busyId === quote.id}
								onclick={() =>
									confirm.ask({
										title: t('Hapus quotation'),
										description: t('Quotation ini akan dihapus permanen dari workspace.'),
										detail: quote.id,
										action: () => handleDelete(quote)
									})}
							>
								{t('Hapus')}
							</Button>
						</div>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No quotation matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredQuotations?.length ?? 0} />

	<ConfirmDialog
		bind:open={confirm.open}
		title={confirm.title}
		description={confirm.description}
		detail={confirm.detail}
		confirmLabel={confirm.label}
		loading={confirm.loading}
		onconfirm={confirm.run}
	/>
</AppShell>