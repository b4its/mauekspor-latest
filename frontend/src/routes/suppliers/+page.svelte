<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { products as seedProducts, suppliers as seedSuppliers } from '$lib/data/trade';
	import { listSuppliers, requestSupplierEvidence, createSupplier, batchDeleteSuppliers } from '$lib/api/suppliers';
	import { downloadFile } from '$lib/api/client';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import { label } from '$lib/utils/labels';
import Pagination from '$lib/components/Pagination.svelte';
import SortSelect from '$lib/components/SortSelect.svelte';
import BulkActionsBar from '$lib/components/BulkActionsBar.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { sortBy, type SortDir } from '$lib/utils/sort';
import { createBulkSelection } from '$lib/utils/bulkSelection.svelte';
import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { page } from '$app/state';
	import { syncFiltersToUrl } from '$lib/utils/urlFilters';
	import { formatDate } from '$lib/utils/date';

	// Konfirmasi terpusat untuk hapus massal supplier.
	const confirm = createConfirmController();

	const filters = ['All', 'Verified', 'In Review', 'Needs Evidence'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'name', label: t('Nama') },
		{ value: 'capabilityScore', label: t('Skor') },
		{ value: 'category', label: t('Kategori') },
		{ value: 'location', label: t('Lokasi') },
		{ value: 'status', label: t('Status') },
		{ value: 'id', label: 'ID' }
	];
	let error = $state('');
	let message = $state('');
	let busyId = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let fName = $state('');
	let fLocation = $state('');
	let fCategory = $state('');
	let fCapacity = $state('');
	let fLeadTime = $state('');
	let fContact = $state('');

	let suppliers = createRemoteList(listSuppliers, seedSuppliers);
	let products = createRemoteList(listProducts, seedProducts);
	$effect(() => {
		suppliers.load();
		products.load();
	});

	let filteredSuppliers = $derived(
		sortBy(
			suppliers.items.filter((supplier) => {
				const names = (supplier.productIds ?? []).map((id) => products.items.find((product) => product.id === id)?.name ?? id).join(' ');
				return (
					(activeFilter === 'All' || supplier.status === activeFilter) &&
					[supplier.name, supplier.location, supplier.category, names].join(' ').toLowerCase().includes(query.trim().toLowerCase())
				);
			}),
			sortKey,
			sortDir
		)
	);
	let verifiedCount = $derived(suppliers.items.filter((supplier) => supplier.status === 'Verified').length);
	let avgCapability = $derived(Math.round(suppliers.items.reduce((sum, supplier) => sum + supplier.capabilityScore, 0) / (suppliers.items.length || 1)));
	function productNames(ids?: string[]) {
		return (ids ?? []).map((id) => products.items.find((product) => product.id === id)?.name ?? id).join(', ');
	}


	async function handleEvidence(supplierId: string, name: string) {
		error = '';
		busyId = supplierId;
		try {
			const res = await requestSupplierEvidence(supplierId);
			if (res.data) {
				suppliers.upsert(res.data);
			} else {
				suppliers.upsert({ ...(suppliers.items.find((s) => s.id === supplierId) as (typeof suppliers.items)[number]), status: 'Needs Evidence' });
			}
			message = `Permintaan bukti dikirim ke ${name}.`;
		} catch {
			error = t('Gagal meminta bukti kepatuhan.');
		} finally {
			busyId = '';
		}
	}

	function openCreate() {
		fName = '';
		fLocation = '';
		fCategory = '';
		fCapacity = '';
		fLeadTime = '';
		fContact = '';
		formError = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fName.trim()) {
			formError = t('Nama supplier wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await createSupplier({
				name: fName.trim(),
				location: fLocation.trim(),
				category: fCategory.trim() || 'Supplier',
				capacity: fCapacity.trim(),
				leadTime: fLeadTime.trim(),
				contact: fContact.trim()
			});
			if (res.data) {
				suppliers.upsert(res.data);
			} else {
				await suppliers.load();
			}
			message = `Supplier "${fName.trim()}" ditambahkan.`;
			showForm = false;
		} catch {
			formError = t('Gagal menambah supplier.');
		} finally {
			saving = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredSuppliers ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredSuppliers?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		sortKey;
		sortDir;
		paginationPage = 1;
	});


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

	// Aksi massal: pilih baris lalu hapus sekaligus.
	const bulk = createBulkSelection();
	let batchDeleting = $state(false);

	async function removeSelected() {
		if (bulk.count === 0) return;
		error = '';
		batchDeleting = true;
		try {
			const res = await batchDeleteSuppliers(bulk.ids);
			bulk.clear();
			await suppliers.load();
			message = `${res.data.deletedCount} ${t('supplier dihapus.')}`;
		} catch {
			error = t('Gagal menghapus supplier terpilih.');
		} finally {
			batchDeleting = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Pemasok')} | MauEkspor</title>
</svelte:head>
<AppShell title={t('Unit Pengolahan Hasil Desa')} eyebrow={t('Exporter and supplier network')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Supplier readiness')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Verify supplier capability before RFQ matching and order execution.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Track capacity, certificates, quality signals, compliance evidence, and operational risks across the export supplier network.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Tambah supplier')}</Button>
			<Button variant="outline" onclick={() => downloadFile('/suppliers/export.csv', 'suppliers.csv')}>{t('Export CSV')}</Button>
			<Button variant="outline" onclick={() => downloadFile('/suppliers/export.xlsx', 'suppliers.xlsx')}>{t('Excel (.xlsx)')}</Button>
			<Badge variant="secondary">{t('Verified')} {verifiedCount}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nama')}
						<Input bind:value={fName} placeholder="PT Kopi Gayo Nusantara" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Lokasi')}
						<Input bind:value={fLocation} placeholder="Aceh, Indonesia" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kategori')}
						<Input bind:value={fCategory} placeholder={t('Coffee processor')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kapasitas')}
						<Input bind:value={fCapacity} placeholder="12,000 bags / month" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Waktu tunggu')}
						<Input bind:value={fLeadTime} placeholder="21 days" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kontak')}
						<Input bind:value={fContact} placeholder={t('Nama kontak')} />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleCreate}>{saving ? t('Menyimpan...') : t('Simpan supplier')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600" role="status">{message}</p>
	{/if}

	{#if suppliers.error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive" role="alert">{suppliers.error}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter === 'All' ? t('Semua') : label(filter)}</Button>
			{/each}
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<label class="flex cursor-pointer items-center gap-1.5 text-sm font-semibold text-muted-foreground">
				<input type="checkbox" class="size-4" checked={bulk.allOf(pagedItems.map((x) => x.id))} onchange={() => bulk.toggleAll(pagedItems.map((x) => x.id))} />
				{t('Pilih semua')}
			</label>
			<Input bind:value={query} type="search"
				aria-label={t('Search supplier, product, location...')} placeholder={t('Search supplier, product, location...')} class="w-[min(390px,100%)]" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
	</div>

	<BulkActionsBar
		count={bulk.count}
		busy={batchDeleting}
		noun={t('supplier')}
		ondelete={() => confirm.ask({
			title: t('Hapus supplier terpilih'),
			description: t('Supplier terpilih akan dihapus permanen dari workspace.'),
			detail: `${bulk.count} ${t('supplier')}`,
			action: removeSelected
		})}
		onclear={() => bulk.clear()}
	/>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Suppliers')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{suppliers.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Verified')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{verifiedCount}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Avg capability')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{avgCapability}%</strong></CardContent></Card>
	</div>

	{#if suppliers.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-8 w-16" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-1 h-4 w-1/2" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-16 w-full rounded-lg" />
						<Skeleton class="h-16 w-full rounded-lg" />
						<Skeleton class="h-16 w-full rounded-lg" />
						<Skeleton class="h-16 w-full rounded-lg" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as supplier}
				<Card class={`relative grid gap-0 transition-all hover:border-ring/40 hover:shadow-md ${bulk.has(supplier.id) ? 'border-primary ring-2 ring-primary/30' : ''}`}>
					<div class="absolute top-4 right-4 z-10">
						<input type="checkbox" class="size-4" checked={bulk.has(supplier.id)} aria-label={`${t('Pilih')} ${supplier.name}`} onchange={() => bulk.toggle(supplier.id)} onclick={(e) => e.stopPropagation()} />
					</div>
					<a href={`/suppliers/${supplier.id}`} class="grid h-full gap-3 p-5 no-underline">
						<div class="flex items-center justify-between gap-3 pr-6">
							<Badge variant={toneVariant(statusTone(supplier.status))}>{label(supplier.status)}</Badge>
							<strong class="text-2xl font-bold tracking-tight">{supplier.capabilityScore}%</strong>
						</div>
						<h3 class="text-2xl font-bold tracking-tight">{supplier.name}</h3>
						<p class="text-sm text-muted-foreground">{supplier.category} · {supplier.location}</p>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Products')}<strong class="mt-1 block text-sm font-bold text-foreground">{productNames(supplier.productIds)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Capacity')}<strong class="mt-1 block text-sm font-bold text-foreground">{supplier.capacity}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Lead time')}<strong class="mt-1 block text-sm font-bold text-foreground">{supplier.leadTime}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Next audit')}<strong class="mt-1 block text-sm font-bold text-foreground">{formatDate(supplier.nextAudit)}</strong></div>
						</div>
					</a>
					<div class="flex flex-wrap gap-2 px-5 pb-5">
						<Button variant="outline" size="sm" disabled={busyId === supplier.id} onclick={() => handleEvidence(supplier.id, supplier.name)}>{t('Minta bukti')}</Button>
						<Button variant="outline" size="sm" href={`/suppliers/${supplier.id}`}>{t('Detail')}</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No supplier matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredSuppliers?.length ?? 0} />

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
