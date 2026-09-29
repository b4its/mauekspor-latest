<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { complianceRequirements as seedRequirements, projects as seedProjects, type ComplianceRequirement } from '$lib/data/trade';
	import { listComplianceRequirements, createComplianceRequirement, updateComplianceRequirement, deleteComplianceRequirement } from '$lib/api/compliance';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';
import Pagination from '$lib/components/Pagination.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
import SortSelect from '$lib/components/SortSelect.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { sortBy, type SortDir } from '$lib/utils/sort';
import { syncFiltersToUrl } from '$lib/utils/urlFilters';
import { formatDate } from '$lib/utils/date';
import { page } from '$app/state';

	const filters = ['All', 'Blocked', 'In Review', 'Evidence Uploaded', 'Verified'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'severity', label: t('Keparahan') },
		{ value: 'due', label: t('Tenggat') },
		{ value: 'title', label: t('Judul') },
		{ value: 'category', label: t('Kategori') },
		{ value: 'status', label: t('Status') }
	];
	let message = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let fTitle = $state('');
	let fCategory = $state('');
	let fSeverity = $state('Medium');
	let fOwner = $state('');
	let fSource = $state('');
	let fRequiredEvidence = $state('');
	let error = $state('');

	let complianceRequirements = createRemoteList(listComplianceRequirements, seedRequirements);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		complianceRequirements.load();
		projects.load();
	});

	let filteredRequirements = $derived(
		sortBy(
			complianceRequirements.items.filter((item) => {
				const matchesFilter = activeFilter === 'All' || item.status === activeFilter;
				const matchesQuery = [item.title, item.category, item.owner, item.source, item.projectId]
					.join(' ')
					.toLowerCase()
					.includes(query.trim().toLowerCase());
				return matchesFilter && matchesQuery;
			}),
			sortKey,
			sortDir
		)
	);

	let criticalCount = $derived(complianceRequirements.items.filter((item) => item.severity === 'Critical').length);
	let verifiedCount = $derived(complianceRequirements.items.filter((item) => item.status === 'Verified').length);

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}


	function openCreate() {
		fTitle = '';
		fCategory = '';
		fSeverity = 'Medium';
		fOwner = '';
		fSource = '';
		fRequiredEvidence = '';
		formError = '';
		showForm = true;
	}

	let busyId = $state('');

	// Konfirmasi terpusat untuk hapus persyaratan (pengganti window.confirm).
	const confirm = createConfirmController();

	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter, sort: sortKey, dir: sortKey ? sortDir : '' };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '', sort: '', dir: '' }, ['query', 'status', 'sort', 'dir']), 250);
		return () => clearTimeout(syncTimer);
	});

	async function handleCreate() {
		formError = '';
		if (!fTitle.trim()) {
			formError = t('Judul wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await createComplianceRequirement({
				title: fTitle.trim(),
				category: fCategory.trim() || 'Document',
				severity: fSeverity,
				owner: fOwner.trim() || 'Compliance Lead',
				source: fSource.trim() || 'Customs Authority',
				requiredEvidence: fRequiredEvidence.trim()
			});
			if (res.data) complianceRequirements.upsert(res.data);
			else await complianceRequirements.load();
			message = `Persyaratan "${fTitle.trim()}" ditambahkan.`;
			showForm = false;
		} catch {
			formError = t('Gagal membuat persyaratan kepatuhan.');
		} finally {
			saving = false;
		}
	}

	async function handleVerify(item: ComplianceRequirement) {
		error = '';
		busyId = item.id;
		try {
			const res = await updateComplianceRequirement(item.id, { status: 'Verified' });
			if (res.data) complianceRequirements.upsert(res.data);
			else complianceRequirements.upsert({ ...item, status: 'Verified' });
			message = `Persyaratan "${item.title}" diverifikasi.`;
		} catch {
			error = t('Gagal memverifikasi persyaratan.');
		} finally {
			busyId = '';
		}
	}

	async function handleDelete(item: ComplianceRequirement) {
		error = '';
		busyId = item.id;
		try {
			await deleteComplianceRequirement(item.id);
			complianceRequirements.remove(item.id);
			message = `Persyaratan "${item.title}" dihapus.`;
		} catch {
			error = t('Gagal menghapus persyaratan kepatuhan.');
		} finally {
			busyId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredRequirements ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredRequirements?.length ?? 0, paginationPageSize));

	// Reset ke halaman pertama saat filter/pencarian/pengurutan berubah.
	$effect(() => {
		activeFilter;
		query;
		sortKey;
		sortDir;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Kepatuhan')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Compliance')} eyebrow={t('Evidence-based export readiness')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Source-backed workflow')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Turn regulatory gaps into verified action items.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Track source, severity, owner, evidence, human verification, and confidence for each export requirement before documents or quotation are finalized.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Tambah persyaratan')}</Button>
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Critical')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{criticalCount}</strong></CardContent>
			</Card>
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Verified')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{verifiedCount}</strong></CardContent>
			</Card>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={fTitle} placeholder={t('Sertifikat fitosanitasi')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kategori')}
						<Input bind:value={fCategory} placeholder={t('Dokumen')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Severity')}
						<select bind:value={fSeverity} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['Low', 'Medium', 'High', 'Critical'] as severity}
								<option value={severity}>{severity}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Owner')}
						<Input bind:value={fOwner} placeholder="compliance" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Sumber')}
						<Input bind:value={fSource} placeholder={t('Peraturan pemerintah')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Bukti wajib')}
						<Input bind:value={fRequiredEvidence} placeholder={t('Sertifikat resmi')} />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleCreate}>{saving ? t('Menyimpan...') : t('Simpan persyaratan')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if message}
		<p role="status" class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if complianceRequirements.error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{complianceRequirements.error}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter === 'All' ? t('Semua') : label(filter)}</Button>
			{/each}
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Input bind:value={query} type="search"
				aria-label={t('Search requirement, source, project...')} placeholder={t('Search requirement, source, project...')} class="w-[min(390px,100%)]" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
	</div>

	{#if complianceRequirements.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-5 w-16 rounded-full" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<Skeleton class="mt-4 h-4 w-1/3" />
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as item}
				<Card class="flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/compliance/${item.id}`} class="block p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(item.status))}>{label(item.status)}</Badge>
							<span class={item.severity.toLowerCase() === 'critical' ? 'rounded-full bg-destructive/10 px-2.5 py-0.5 text-xs font-semibold text-destructive' : item.severity.toLowerCase() === 'major' ? 'rounded-full bg-orange-500/10 px-2.5 py-0.5 text-xs font-semibold text-orange-600' : 'rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary'}>{label(item.severity)}</span>
						</div>
						<h3 class="mt-4 text-2xl font-bold tracking-tight">{item.title}</h3>
						<p class="mt-2 text-sm text-muted-foreground">{projectName(item.projectId)}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Category')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.category}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.owner}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Due')} <strong class="mt-1 block text-sm font-bold text-foreground">{formatDate(item.due)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Confidence')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.confidence != null ? `${item.confidence}%` : '—'}</strong></div>
						</div>
						<p class="mt-4 text-xs font-semibold text-muted-foreground">{t('Source:')} {item.source}</p>
					</a>
					<div class="px-5 pb-4 pt-1 flex items-center justify-end gap-2 border-t">
						{#if item.status !== 'Verified'}
							<Button
								variant="outline"
								size="sm"
								disabled={busyId === item.id}
								onclick={() => handleVerify(item)}
							>
								{busyId === item.id ? t('Menyimpan...') : t('Verifikasi')}
							</Button>
						{/if}
						<Button
							variant="ghost"
							size="sm"
							class="text-destructive hover:bg-destructive/10"
							disabled={busyId === item.id}
							onclick={() =>
								confirm.ask({
									title: t('Hapus persyaratan kepatuhan'),
									description: t('Persyaratan ini akan dihapus permanen dari workspace.'),
									detail: item.title,
									action: () => handleDelete(item)
								})}
						>
							{t('Hapus')}
						</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No compliance requirement matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredRequirements?.length ?? 0} />

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