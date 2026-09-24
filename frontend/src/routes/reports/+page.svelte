<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { tradeReports } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listReports, generateReport, createReport } from '$lib/api/reports';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Executive', 'Compliance', 'Financial', 'Shipment'];

	function trType(x: string) {
		return t(x === 'All' ? 'Semua' : x === 'Executive' ? 'Eksekutif' : x === 'Compliance' ? 'Kepatuhan' : x === 'Financial' ? 'Keuangan' : 'Pengiriman');
	}
	let activeFilter = $state('All');
	let query = $state('');
	let message = $state('');
	let busyId = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let fTitle = $state('');
	let fType = $state('Summary');
	let fPeriod = $state('');
	let error = $state('');

	let reports = createRemoteList(listReports, tradeReports);
	$effect(() => {
		reports.load();
	});

	let filteredReports = $derived(
		reports.items.filter(
			(report) =>
				(activeFilter === 'All' || report.type === activeFilter) &&
				[report.title, report.type, report.status, report.owner].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let readyCount = $derived(reports.items.filter((report) => report.status === 'Ready').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleGenerate(reportId: string, title: string) {
		error = '';
		busyId = reportId;
		try {
			const res = await generateReport(reportId);
			if (res.data) {
				reports.upsert(res.data);
			} else {
				await reports.load();
			}
			message = `Laporan "${title}" dibuat.`;
		} catch {
			error = t('Gagal generate laporan.');
		} finally {
			busyId = '';
		}
	}

	function openCreate() {
		fTitle = '';
		fType = 'Summary';
		fPeriod = '';
		formError = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fTitle.trim()) {
			formError = t('Judul wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await createReport({
				title: fTitle.trim(),
				type: fType,
				period: fPeriod.trim()
			});
			if (res.data) {
				reports.upsert(res.data);
			} else {
				await reports.load();
			}
			message = `Laporan "${fTitle.trim()}" ditambahkan.`;
			showForm = false;
		} catch {
			formError = t('Gagal membuat laporan.');
		} finally {
			saving = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredReports ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredReports?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('Laporan')} | MauEkspor</title>
</svelte:head>

<AppShell title="Reports" eyebrow={t('Pelaporan intelijen ekspor')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Pembuat laporan')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Buat laporan dagang dari sinyal ruang kerja ekspor secara langsung.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Kemas wawasan eksekutif, kepatuhan, keuangan, dan pengiriman untuk manajemen, buyer, finance, dan operasional.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Buat laporan')}</Button>
			<Badge>{t('Ready')} {readyCount}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={fTitle} placeholder={t('Laporan ekspor bulanan')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tipe')}
						<select bind:value={fType} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['Summary', 'Financial', 'Compliance', 'Operational'] as type}
								<option value={type}>{type}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Periode')}
						<Input bind:value={fPeriod} placeholder="Aug 2026" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleCreate}>{saving ? t('Menyimpan...') : t('Simpan laporan')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if reports.error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{reports.error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{trType(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari laporan, pemilik, jenis...')} class="w-[min(390px,100%)]" />
	</div>

	{#if reports.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-5 w-16 rounded-full" />
					</div>
					<Skeleton class="mt-3 h-7 w-3/4" />
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
			{#each pagedItems as report}
				<Card class="grid gap-0 transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/reports/${report.id}`} class="block h-full p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(report.status))}>{report.status}</Badge>
							<strong class="text-sm font-bold tracking-tight">{report.type}</strong>
						</div>
						<h3 class="mt-3 text-2xl font-bold tracking-tight">{report.title}</h3>
						<p class="mt-1 text-sm text-muted-foreground">{report.period} · {report.owner}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Bagian')}<strong class="mt-1 block text-sm font-bold text-foreground">{(report.sections ?? []).length}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Wawasan')}<strong class="mt-1 block text-sm font-bold text-foreground">{(report.insights ?? []).length}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Updated')}<strong class="mt-1 block text-sm font-bold text-foreground">{report.updatedAt}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('ID Laporan')}<strong class="mt-1 block text-sm font-bold text-foreground">{report.id}</strong></div>
						</div>
					</a>
					<div class="flex flex-wrap gap-2 px-5 pb-5">
						<Button variant="outline" size="sm" disabled={busyId === report.id} onclick={() => handleGenerate(report.id, report.title)}>{t('Generate')}</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada laporan yang cocok dengan pencarian.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredReports?.length ?? 0} />

</AppShell>
