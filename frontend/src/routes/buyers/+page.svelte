<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { buyers as seedBuyers } from '$lib/data/trade';
import { listBuyers, createBuyer, batchDeleteBuyers } from '$lib/api/buyers';
	import { downloadFile, exportPath } from '$lib/api/client';
import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone, toneVariant } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { label } from '$lib/utils/labels';
import Pagination from '$lib/components/Pagination.svelte';
import SortSelect from '$lib/components/SortSelect.svelte';
import BulkActionsBar from '$lib/components/BulkActionsBar.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
	import DataStateBanner from '$lib/components/DataStateBanner.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { sortBy, type SortDir } from '$lib/utils/sort';
import { createBulkSelection } from '$lib/utils/bulkSelection.svelte';
import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { page } from '$app/state';
	import { syncFiltersToUrl } from '$lib/utils/urlFilters';

	// Konfirmasi terpusat untuk hapus massal buyer.
	const confirm = createConfirmController();

	const filters = ['All', 'Lead', 'Qualified', 'Negotiating', 'Active', 'At Risk'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'fitScore', label: t('Skor kecocokan') },
		{ value: 'estimatedAnnualValue', label: t('Nilai tahunan') },
		{ value: 'name', label: t('Nama') },
		{ value: 'country', label: t('Negara') },
		{ value: 'status', label: t('Status') }
	];
	let error = $state('');
	let message = $state('');
	let showForm = $state(false);
	let creating = $state(false);
	let formError = $state('');
	let fName = $state('');
	let fCountry = $state('');
	let fSegment = $state('');
	let fProducts = $state('');

	let buyers = createRemoteList(listBuyers, seedBuyers);
	$effect(() => {
		buyers.load();
	});

	let filteredBuyers = $derived(
		sortBy(
			buyers.items.filter((buyer) => {
				const matchesFilter = activeFilter === 'All' || buyer.status === activeFilter;
				const matchesQuery = [buyer.name, buyer.country, buyer.segment, buyer.status, ...(buyer.interestedProducts ?? [])]
					.join(' ')
					.toLowerCase()
					.includes(query.trim().toLowerCase());
				return matchesFilter && matchesQuery;
			}),
			sortKey,
			sortDir
		)
	);

	let activeCount = $derived(buyers.items.filter((buyer) => ['Active', 'Negotiating'].includes(buyer.status)).length);
	let pipelineValue = $derived(buyers.items.reduce((sum, buyer) => sum + buyer.estimatedAnnualValue, 0));
	let avgFit = $derived(Math.round(buyers.items.reduce((sum, buyer) => sum + buyer.fitScore, 0) / (buyers.items.length || 1)));

	function openCreate() {
		formError = '';
		fName = '';
		fCountry = '';
		fSegment = '';
		fProducts = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fName.trim()) {
			formError = t('Nama wajib diisi.');
			return;
		}
		creating = true;
		try {
			const res = await createBuyer({
				name: fName.trim(),
				country: fCountry.trim(),
				segment: fSegment.trim(),
				interestedProducts: fProducts
					.split(',')
					.map((item) => item.trim())
					.filter(Boolean)
			});
			if (res.data) {
				buyers.upsert(res.data);
			} else {
				await buyers.load();
			}
			message = `Buyer "${fName.trim()}" ditambahkan.`;
			showForm = false;
			fName = '';
			fCountry = '';
			fSegment = '';
			fProducts = '';
		} catch {
			formError = t('Gagal menambahkan buyer.');
		} finally {
			creating = false;
		}
	}

	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredBuyers ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredBuyers?.length ?? 0, paginationPageSize));

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
			const res = await batchDeleteBuyers(bulk.ids);
			bulk.clear();
			await buyers.load();
			message = `${res.data.deletedCount} ${t('buyer dihapus.')}`;
		} catch {
			error = t('Gagal menghapus buyer terpilih.');
		} finally {
			batchDeleting = false;
		}
	}


	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter, sort: sortKey, dir: sortKey ? sortDir : '' };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(
			() => syncFiltersToUrl(page.url, state, { query: '', status: '', sort: '', dir: '' }, ['query', 'status', 'sort', 'dir']),
			250
		);
		return () => clearTimeout(syncTimer);
	});
	// FR-EXP-2: export mengikuti cakupan yang sedang ditinjau (terpilih > filter/pencarian).
	async function exportList(ext: 'csv' | 'xlsx') {
		error = '';
		try {
			const scope = bulk.count
				? { ids: bulk.ids }
				: { search: query.trim(), status: activeFilter === 'All' ? '' : activeFilter };
			const path = exportPath(`/buyers/export.${ext}`, scope);
			await downloadFile(path, `buyers.${ext}`);
		} catch (e) {
			error = e instanceof Error && e.message ? e.message : t('Gagal mengekspor data.');
		}
	}

</script>

<svelte:head>
	<title>{t('Pembeli')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Buyers')} eyebrow={t('Export buyer CRM')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Buyer pipeline')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Manage importer relationships from market signal to repeat order.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Qualify buyers, track contact context, connect accounts to projects, and prioritize the next action that moves export deals forward.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Add buyer lead')}</Button>
			<Button variant="outline" onclick={() => exportList('csv')}>{t('Export CSV')}</Button>
			<Button variant="outline" onclick={() => exportList('xlsx')}>{t('Excel (.xlsx)')}</Button>
			<Badge variant="secondary">{t('Active')} {activeCount}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nama')}
						<Input bind:value={fName} placeholder="Hikari Foods Co." />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Negara')}
						<Input bind:value={fCountry} placeholder="Japan" />
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Segmen')}
						<Input bind:value={fSegment} placeholder={t('Food & Beverage')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Produk diminati')}
						<Input bind:value={fProducts} placeholder="Coffee Beans, Spices" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Adding...') : t('Simpan buyer')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{error}</p>
	{/if}

	<DataStateBanner usingFallback={buyers.usingFallback} error={buyers.error} />

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600" role="status">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button
					class={activeFilter === filter ? '' : ''}
					variant={activeFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (activeFilter = filter)}
				>
					{filter === 'All' ? t('Semua') : label(filter)}
				</Button>
			{/each}
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<label class="flex cursor-pointer items-center gap-1.5 text-sm font-semibold text-muted-foreground">
				<input type="checkbox" class="size-4" checked={bulk.allOf(pagedItems.map((x) => x.id))} onchange={() => bulk.toggleAll(pagedItems.map((x) => x.id))} />
				{t('Pilih semua')}
			</label>
			<Input bind:value={query} type="search"
				aria-label={t('Search buyer, country, segment...')} placeholder={t('Search buyer, country, segment...')} class="max-w-xs" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
	</div>

	<BulkActionsBar
		count={bulk.count}
		busy={batchDeleting}
		noun={t('buyer')}
		ondelete={() => confirm.ask({
			title: t('Hapus buyer terpilih'),
			description: t('Buyer terpilih akan dihapus permanen dari workspace.'),
			detail: `${bulk.count} ${t('buyer')}`,
			action: removeSelected
		})}
		onclear={() => bulk.clear()}
	/>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Buyer accounts')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{buyers.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Annual pipeline')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(pipelineValue)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Average fit')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{avgFit}%</strong></CardContent></Card>
	</div>

	{#if buyers.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-16" />
						<Skeleton class="h-7 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
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
			{#each pagedItems as buyer}
				<Card class={`relative transition-all hover:border-ring/40 hover:shadow-md ${bulk.has(buyer.id) ? 'border-primary ring-2 ring-primary/30' : ''}`}>
					<div class="absolute top-4 right-4 z-10">
						<input type="checkbox" class="size-4" checked={bulk.has(buyer.id)} aria-label={`${t('Pilih')} ${buyer.name}`} onchange={() => bulk.toggle(buyer.id)} onclick={(e) => e.stopPropagation()} />
					</div>
					<a href={`/buyers/${buyer.id}`} class="grid h-full gap-3 p-5 no-underline">
						<div class="flex items-center justify-between gap-3 pr-6">
							<Badge variant={toneVariant(statusTone(buyer.status))}>{label(buyer.status)}</Badge>
							<strong class="text-2xl font-bold tracking-tight">{buyer.fitScore}%</strong>
						</div>
						<h3 class="text-2xl font-bold tracking-tight">{buyer.name}</h3>
						<p class="text-sm text-muted-foreground">{buyer.segment} · {buyer.country}</p>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Pipeline')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(buyer.estimatedAnnualValue)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Payment')}<strong class="mt-1 block text-sm font-bold text-foreground">{buyer.paymentProfile}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Products')}<strong class="mt-1 block text-sm font-bold text-foreground">{(buyer.interestedProducts ?? []).join(', ')}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Next step')}<strong class="mt-1 block text-sm font-bold text-foreground">{buyer.nextStep}</strong></div>
						</div>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No buyer matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredBuyers?.length ?? 0} />

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