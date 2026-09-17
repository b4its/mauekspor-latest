<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { tradeReports } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listReports, generateReport } from '$lib/api/reports';
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
	let generated = $state(false);
	let generating = $state(false);
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

	async function handleGenerate() {
		error = '';
		generating = true;
		try {
			const target = reports.items.find((report) => report.status !== 'Ready') ?? reports.items[0];
			if (target) await generateReport(target.id);
			generated = true;
		} catch {
			error = t('Gagal generate laporan.');
		} finally {
			generating = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
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
			<Button onclick={handleGenerate} disabled={generating}>{generated ? t('Laporan berhasil dibuat') : generating ? t('Membuat...') : t('Buat laporan')}</Button>
			<Badge>{t('Ready')} {readyCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if reports.error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{reports.error}</p>
	{/if}

	{#if generated}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Laporan berhasil dibuat.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Laporan dibuat di backend.')}</span>
		</div>
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
				<Card class="transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/reports/${report.id}`} class="block h-full p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(report.status))}>{report.status}</Badge>
							<strong class="text-sm font-bold tracking-tight">{report.type}</strong>
						</div>
						<h3 class="mt-3 text-2xl font-bold tracking-tight">{report.title}</h3>
						<p class="mt-1 text-sm text-muted-foreground">{report.period} · {report.owner}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Bagian')}<strong class="mt-1 block text-sm font-bold text-foreground">{report.sections.length}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Wawasan')}<strong class="mt-1 block text-sm font-bold text-foreground">{report.insights.length}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Updated')}<strong class="mt-1 block text-sm font-bold text-foreground">{report.updatedAt}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('ID Laporan')}<strong class="mt-1 block text-sm font-bold text-foreground">{report.id}</strong></div>
						</div>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada laporan yang cocok dengan pencarian.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredReports?.length ?? 0} />

</AppShell>
