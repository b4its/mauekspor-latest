<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { projects as seedProjects, tradeDocuments as seedDocuments } from '$lib/data/trade';
	import type { TradeDocument } from '$lib/data/trade';
	import { listTradeDocuments, generateTradeDocument, approveTradeDocument, deleteTradeDocument, documentPdfUrl, batchDeleteDocuments, listDocumentTypes } from '$lib/api/documents';
	import type { DocumentTypeSpec } from '$lib/api/documents';
	// documentPdfUrl dipakai untuk membentuk path unduhan terautentikasi.
	import { downloadFile, exportPath } from '$lib/api/client';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
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
	import { formatDateTime } from '$lib/utils/date';

	const filters = ['All', 'Ready', 'Needs Review', 'Approved', 'Missing'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'validationScore', label: t('Skor validasi') },
		{ value: 'type', label: t('Tipe') },
		{ value: 'status', label: t('Status') },
		{ value: 'owner', label: t('Pemilik') },
		{ value: 'updatedAt', label: t('Terakhir diperbarui') },
		{ value: 'id', label: 'ID' }
	];
	let generating = $state(false);
	let message = $state('');
	let showForm = $state(false);
	let formError = $state('');
	let fProjectId = $state('');
	let fType = $state('Commercial Invoice');
	let error = $state('');

	let tradeDocuments = createRemoteList(listTradeDocuments, seedDocuments);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	// Katalog tipe dokumen dari backend (satu sumber kebenaran, PRD §5.8).
	let docTypes = $state<DocumentTypeSpec[]>([]);
	let requiredDocs = $state<string[]>([]);
	$effect(() => {
		tradeDocuments.load();
		projects.load();
		listDocumentTypes()
			.then((res) => {
				docTypes = res.data.types ?? [];
				requiredDocs = res.data.required ?? [];
			})
			.catch(() => {
				docTypes = [];
			});
	});

	let filteredDocuments = $derived(
		sortBy(
			tradeDocuments.items.filter((document) => {
				const matchesFilter = activeFilter === 'All' || document.status === activeFilter;
				const matchesQuery = [document.id, document.type, document.owner, document.projectId]
					.join(' ')
					.toLowerCase()
					.includes(query.trim().toLowerCase());
				return matchesFilter && matchesQuery;
			}),
			sortKey,
			sortDir
		)
	);

	let averageScore = $derived(
		Math.round(tradeDocuments.items.reduce((sum, document) => sum + document.validationScore, 0) / (tradeDocuments.items.length || 1))
	);
	let needsReviewCount = $derived(tradeDocuments.items.filter((document) => document.status !== 'Ready' && document.status !== 'Approved').length);

	// Konfirmasi terpusat untuk hapus dokumen (pengganti window.confirm).
	const confirm = createConfirmController();

	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter, sort: sortKey, dir: sortKey ? sortDir : '' };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '', sort: '', dir: '' }, ['query', 'status', 'sort', 'dir']), 250);
		return () => clearTimeout(syncTimer);
	});

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}

	// FR-EXP-2: export mengikuti cakupan yang sedang ditinjau (terpilih >
	// filter/pencarian). Nama berkas mencerminkan scope.
	async function exportDocuments(ext: 'csv' | 'xlsx') {
		error = '';
		try {
			const scope = bulk.count
				? { ids: bulk.ids }
				: { search: query.trim(), status: activeFilter === 'All' ? '' : activeFilter };
			const path = exportPath(`/documents/export.${ext}`, scope);
			await downloadFile(path, `documents.${ext}`);
		} catch (e) {
			error = e instanceof Error && e.message ? e.message : t('Gagal mengekspor dokumen.');
		}
	}

	// FR-EXP-1: unduhan PDF lewat helper terautentikasi (bearer token), bukan
	// tautan biasa yang akan 401 karena token ada di sessionStorage.
	let downloadingId = $state('');
	async function downloadTradeDocumentPdf(document: TradeDocument) {
		error = '';
		downloadingId = document.id;
		try {
			const path = documentPdfUrl(document.id).replace(import.meta.env.VITE_API_BASE_URL ?? '/api/v1', '');
			await downloadFile(path, `${document.id}.pdf`);
		} catch (e) {
			error = e instanceof Error && e.message ? e.message : t('Gagal mengunduh PDF.');
		} finally {
			downloadingId = '';
		}
	}

	function openCreate() {
		fProjectId = '';
		fType = 'Commercial Invoice';
		formError = '';
		showForm = true;
	}

	let actionId = $state('');

	async function generateDocument() {
		formError = '';
		if (!fProjectId) {
			formError = t('Project wajib dipilih.');
			return;
		}
		generating = true;
		try {
			const res = await generateTradeDocument({
				projectId: fProjectId,
				type: fType as TradeDocument['type']
			});
			if (res.data) {
				tradeDocuments.upsert(res.data);
			} else {
				await tradeDocuments.load();
			}
			message = `Dokumen ${fType} dibuat.`;
			showForm = false;
		} catch {
			formError = t('Gagal generate dokumen.');
		} finally {
			generating = false;
		}
	}

	async function handleApprove(doc: TradeDocument) {
		error = '';
		actionId = doc.id;
		try {
			const res = await approveTradeDocument(doc.id);
			if (res.data) {
				tradeDocuments.upsert(res.data);
			} else {
				await tradeDocuments.load();
			}
			message = `Dokumen ${doc.id} disetujui.`;
		} catch {
			error = t('Gagal menyetujui dokumen.');
		} finally {
			actionId = '';
		}
	}

	async function handleDelete(doc: TradeDocument) {
		error = '';
		actionId = doc.id;
		try {
			await deleteTradeDocument(doc.id);
			tradeDocuments.remove(doc.id);
			message = `Dokumen ${doc.id} dihapus.`;
		} catch {
			error = t('Gagal menghapus dokumen.');
		} finally {
			actionId = '';
		}
	}

	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredDocuments ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredDocuments?.length ?? 0, paginationPageSize));

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
			const res = await batchDeleteDocuments(bulk.ids);
			bulk.clear();
			await tradeDocuments.load();
			message = `${res.data.deletedCount} ${t('dokumen dihapus.')}`;
		} catch {
			error = t('Gagal menghapus dokumen terpilih.');
		} finally {
			batchDeleting = false;
		}
	}

</script>

<svelte:head>
	<title>{t('Dokumen')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Documents')} eyebrow={t('Trade document center')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Kontrol dokumen')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Generate, validate, approve, and version trade documents.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Keep invoice, packing list, certificate of origin, lab reports, insurance, and shipment documents consistent with product, quotation, and shipment data.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Generate document')}</Button>
			<Button variant="outline" onclick={() => exportDocuments('csv')}>{t('Export CSV')}</Button>
			<Button variant="outline" onclick={() => exportDocuments('xlsx')}>{t('Excel (.xlsx)')}</Button>
			<Badge variant="secondary">Avg validation {averageScore}%</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Project')}
						<select bind:value={fProjectId} class="h-10 rounded-md border bg-background px-3 text-sm">
							<option value="">{t('Pilih project')}</option>
							{#each projects.items as project}
								<option value={project.id}>{project.name}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tipe dokumen')}
						<select bind:value={fType} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each (docTypes.length ? docTypes.map((d) => d.type) : ['Commercial Invoice', 'Packing List', 'Proforma Invoice', 'Certificate of Origin']) as type}
								<option value={type}>{label(type)}</option>
							{/each}
						</select>
					</label>
				</div>
				{#if requiredDocs.length}
					<p class="text-xs font-semibold text-muted-foreground">
						{t('Dokumen wajib (indikatif)')}: {requiredDocs.map((d) => label(d)).join(', ')}
					</p>
				{/if}
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={generating} onclick={generateDocument}>{generating ? t('Generating...') : t('Generate document')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if tradeDocuments.error}
		<p role="alert" class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{tradeDocuments.error}</p>
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
				<input type="checkbox" class="size-4" checked={bulk.allOf(pagedItems.map((x) => x.id))} onchange={() => bulk.toggleAll(pagedItems.map((x) => x.id))} />
				{t('Pilih semua')}
			</label>
			<Input bind:value={query} type="search" aria-label={t('Cari dokumen, pemilik, proyek...')} placeholder={t('Cari dokumen, pemilik, proyek...')} class="w-[min(390px,100%)]" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
	</div>

	<BulkActionsBar
		count={bulk.count}
		busy={batchDeleting}
		noun={t('dokumen')}
		ondelete={() => confirm.ask({
			title: t('Hapus dokumen terpilih'),
			description: t('Dokumen terpilih akan dihapus permanen dari workspace.'),
			detail: `${bulk.count} ${t('dokumen')}`,
			action: removeSelected
		})}
		onclear={() => bulk.clear()}
	/>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total documents')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{tradeDocuments.items.length}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Need attention')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{needsReviewCount}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Validation score')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{averageScore}%</strong>
			</CardContent>
		</Card>
	</div>

	{#if tradeDocuments.loading}
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
			{#each pagedItems as document}
				<Card class={`relative flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md ${bulk.has(document.id) ? 'border-primary ring-2 ring-primary/30' : ''}`}>
					<div class="absolute top-4 right-4 z-10">
						<input type="checkbox" class="size-4" checked={bulk.has(document.id)} aria-label={`${t('Pilih')} ${document.id}`} onchange={() => bulk.toggle(document.id)} onclick={(e) => e.stopPropagation()} />
					</div>
					<div class="p-5">
						<div class="flex items-center justify-between gap-3 pr-6">
							<Badge variant={toneVariant(statusTone(document.status))}>{label(document.status)}</Badge>
							<strong class="text-3xl font-bold tracking-tight">{document.validationScore}%</strong>
						</div>
						<a href={`/documents/${document.id}`} class="mt-4 block no-underline hover:underline">
							<h3 class="text-xl font-bold tracking-tight text-foreground">{document.type}</h3>
							<p class="mt-1 text-sm text-muted-foreground">{projectName(document.projectId)}</p>
						</a>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('ID')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.id}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Version')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.version}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{document.owner}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Updated')} <strong class="mt-1 block text-sm font-bold text-foreground">{formatDateTime(document.updatedAt)}</strong>
							</div>
						</div>
					</div>
					<div class="flex items-center justify-between border-t bg-muted/10 px-5 py-3">
						<a href={`/documents/${document.id}`} class="text-xs font-semibold text-primary hover:underline">
							{t('Lihat detail')} &rarr;
						</a>
						<div class="flex items-center gap-1.5">
							{#if document.status !== 'Approved'}
								<Button
									variant="outline"
									size="sm"
									class="h-7 text-xs"
									disabled={actionId === document.id}
									onclick={() => handleApprove(document)}
								>
									{actionId === document.id ? '...' : t('Setujui')}
								</Button>
							{/if}
							<Button
								variant="outline"
								size="sm"
								class="h-7 text-xs"
								disabled={downloadingId === document.id}
								onclick={() => downloadTradeDocumentPdf(document)}
							>
								{downloadingId === document.id ? '…' : 'PDF'}
							</Button>
							<Button
								variant="ghost"
								size="sm"
								class="h-7 text-xs text-destructive hover:bg-destructive/10"
								disabled={actionId === document.id}
								onclick={() =>
									confirm.ask({
										title: t('Hapus dokumen'),
										description: t('Dokumen ini akan dihapus permanen dari workspace.'),
										detail: `${document.type} · ${document.id}`,
										action: () => handleDelete(document)
									})}
							>
								{t('Hapus')}
							</Button>

						</div>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No document matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredDocuments?.length ?? 0} />

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