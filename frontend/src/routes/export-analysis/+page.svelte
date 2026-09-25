<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { exportAnalyses as seedAnalyses } from '$lib/data/trade';
	import { listExportAnalyses } from '$lib/api/export-analysis';
	import { csvExportUrl } from '$lib/api/client';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';

	import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
	import FilterIcon from '@lucide/svelte/icons/filter';
	import XIcon from '@lucide/svelte/icons/x';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';

	const filters = ['All', 'Ready', 'In Progress', 'Needs Review'];

	function trStatus(s: string) {
		return t(s === 'All' ? 'Semua' : s === 'Ready' ? 'Siap' : s === 'In Progress' ? 'Sedang berjalan' : 'Perlu tinjauan');
	}
	let activeFilter = $state('All');
	let query = $state('');

	let exportAnalyses = createRemoteList(listExportAnalyses, seedAnalyses);
	$effect(() => {
		exportAnalyses.load();
	});

	const countryParam = $derived(page.url.searchParams.get('country') || '');
	const productParam = $derived(page.url.searchParams.get('product') || '');

	// Match targeted analysis if query parameters are present
	const matchedAnalysis = $derived.by(() => {
		if (!countryParam && !productParam) return null;
		const c = countryParam.trim().toLowerCase();
		const p = productParam.trim().toLowerCase();
		return (
			exportAnalyses.items.find((item) => {
				const itemDest = String(item.destination || item.countryCode || '').toLowerCase();
				const itemProdId = String(item.productId || '').toLowerCase();
				const itemProdName = String(item.productName || '').toLowerCase();

				const matchesCountry = !c || itemDest === c;
				const matchesProduct = !p || itemProdId === p || itemProdName.includes(p);
				return matchesCountry && matchesProduct;
			}) ?? null
		);
	});

	let filteredAnalyses = $derived(
		exportAnalyses.items.filter((analysis) => {
			if (countryParam) {
				const itemDest = String(analysis.destination || analysis.countryCode || '').toLowerCase();
				if (itemDest !== countryParam.trim().toLowerCase()) return false;
			}
			if (productParam) {
				const itemProdId = String(analysis.productId || '').toLowerCase();
				const itemProdName = String(analysis.productName || '').toLowerCase();
				const p = productParam.trim().toLowerCase();
				if (itemProdId !== p && !itemProdName.includes(p)) return false;
			}
			const matchesFilter = activeFilter === 'All' || analysis.status === activeFilter;
			const matchesQuery = [analysis.productName, analysis.destination, analysis.hsCode, analysis.status]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(6);
	let pagedItems = $derived(paginate(filteredAnalyses ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredAnalyses?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		countryParam;
		productParam;
		paginationPage = 1;
	});
</script>

<svelte:head>
	<title>{t('Analisis Ekspor')} | MauEkspor</title>
</svelte:head>

<AppShell title="Export Analysis" eyebrow={t('Intelijen kesiapan pasar')}>
	<div class="space-y-6">
		<Card class="panel-hero p-6 md:p-8">
			<CardHeader class="p-0">
				<Badge variant="outline">{t('Intelijen pasar AI')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Kenali tujuan sebelum Anda menawar.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed">
					{t('Klasifikasi HS, bea masuk, pembatasan, dan rekomendasi regulasi untuk setiap pasangan produk-pasar.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/export-analysis/create">{t('Analisis baru')}</Button>
				<Button href="/export-analysis/compare" variant="outline">{t('Bandingkan pasar')}</Button>
				<Button href="/hs-codes" variant="outline">{t('Browsing HS code')}</Button>
				<Button href={csvExportUrl('/export-analysis/export.csv')} variant="outline">{t('Ekspor CSV')}</Button>
			</CardContent>
		</Card>

		<!-- Targeted Query Param Match Banner -->
		{#if matchedAnalysis}
			<Card class="border-emerald-500/40 bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent p-5 shadow-sm">
				<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
					<div class="space-y-1">
						<div class="flex items-center gap-2">
							<Badge variant="default" class="bg-emerald-600 text-white font-bold">
								<SparklesIcon class="mr-1 size-3" />
								{t('Analisis Lengkap Tersedia')}
							</Badge>
							<span class="text-xs text-muted-foreground font-mono font-bold">
								{matchedAnalysis.destination}
							</span>
						</div>
						<h3 class="text-xl font-bold tracking-tight text-foreground">
							{matchedAnalysis.productName} &rarr; {matchedAnalysis.destination}
						</h3>
						<p class="text-xs text-muted-foreground">
							{t('Skor Kesiapan')}: <strong class="text-foreground">{matchedAnalysis.score}/100</strong> &bull; {t('Status')}: <strong class="text-foreground">{trStatus(matchedAnalysis.status)}</strong>
						</p>
					</div>
					<div class="flex items-center gap-2">
						<Button href={`/export-analysis/${matchedAnalysis.id}`} class="font-bold">
							<span>{t('Buka Analisis Lengkap')}</span>
							<ArrowRightIcon class="ms-1 size-4" />
						</Button>
						<Button variant="ghost" size="sm" onclick={() => goto('/export-analysis')}>
							<XIcon class="size-4" />
							<span class="sr-only">{t('Reset Filter')}</span>
						</Button>
					</div>
				</div>
			</Card>
		{:else if countryParam || productParam}
			<div class="flex items-center justify-between gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs font-semibold text-amber-800 dark:text-amber-300">
				<div class="flex items-center gap-2">
					<FilterIcon class="size-4 shrink-0" />
					<span>{t('Memfilter analisis untuk:')} <strong>{productParam || ''}</strong> ({countryParam || ''})</span>
				</div>
				<Button variant="outline" size="sm" onclick={() => goto('/export-analysis')} class="h-7 text-xs">
					{t('Tampilkan Semua')}
				</Button>
			</div>
		{/if}

		<div class="flex flex-wrap items-center justify-between gap-3">
			<div class="flex flex-wrap gap-2">
				{#each filters as filter}
					<Button
						variant={activeFilter === filter ? 'default' : 'outline'}
						size="sm"
						onclick={() => (activeFilter = filter)}
					>
						{trStatus(filter)}
					</Button>
				{/each}
			</div>
			<Input
				bind:value={query}
				type="search"
				placeholder={t('Cari produk, tujuan, HS...')}
				class="max-w-xs"
			/>
		</div>

		{#if exportAnalyses.error}
			<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">
				{exportAnalyses.error}
			</p>
		{/if}

		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#if exportAnalyses.loading}
				{#each Array(6) as _}
					<Card class="p-5">
						<div class="flex items-center justify-between gap-3">
							<Skeleton class="h-5 w-24" />
							<Skeleton class="h-8 w-16" />
						</div>
						<Skeleton class="mt-3 h-7 w-3/4" />
						<Skeleton class="mt-1 h-4 w-1/2" />
						<div class="mt-4 grid grid-cols-2 gap-2">
							<Skeleton class="h-16 w-full rounded-lg" />
							<Skeleton class="h-16 w-full rounded-lg" />
							<Skeleton class="h-16 w-full rounded-lg" />
							<Skeleton class="h-16 w-full rounded-lg" />
						</div>
					</Card>
				{/each}
			{:else}
				{#each pagedItems as analysis}
					<Card class="p-5 flex flex-col justify-between">
						<div>
							<div class="flex items-center justify-between gap-3">
								<Badge variant={toneVariant(statusTone(analysis.status))}>
									{trStatus(analysis.status)}
								</Badge>
								<strong class="text-2xl font-bold tracking-tight">{analysis.score}</strong>
							</div>
							<h3 class="mt-3 text-xl font-bold tracking-tight">{analysis.productName}</h3>
							<p class="mt-1 text-sm text-muted-foreground">{analysis.destination} - HS {analysis.hsCode}</p>
							<div class="mt-4 grid grid-cols-2 gap-2">
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Keyakinan')}<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.confidence}%</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Permintaan')}<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.marketDemand ?? '—'}</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Bea masuk')}<strong class="mt-1 block text-sm font-bold text-foreground">{(analysis.duties ?? '—').split(' ')[0]}</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Pembatasan')}<strong class="mt-1 block text-sm font-bold text-foreground">{(analysis.restrictions ?? []).length}</strong>
								</div>
							</div>
						</div>
						<div class="mt-4 flex flex-wrap gap-2 border-t pt-3">
							<Button variant="default" size="sm" href={`/export-analysis/${analysis.id}`}>
								{t('Buka analisis')}
							</Button>
							<Button variant="outline" size="sm" href={`/export-analysis/${analysis.id}/regulation-recommendations`}>
								{t('Rekomendasi')}
							</Button>
						</div>
					</Card>
				{:else}
					<div class="col-span-full rounded-xl border border-dashed p-8 text-center font-semibold text-muted-foreground">
						<p>{t('Tidak ada analisis yang cocok dengan filter.')}</p>
						{#if countryParam || productParam}
							<div class="mt-3 flex justify-center gap-2">
								<Button variant="outline" size="sm" onclick={() => goto('/export-analysis')}>
									{t('Reset Filter')}
								</Button>
								<Button size="sm" href={`/export-analysis/create?product=${productParam}&country=${countryParam}`}>
									{t('Buat Analisis Baru')}
								</Button>
							</div>
						{/if}
					</div>
				{/each}
			{/if}
		</div>

		<Pagination
			bind:page={paginationPage}
			bind:pageSize={paginationPageSize}
			totalPages={paginationTotalPages}
			totalItems={filteredAnalyses?.length ?? 0}
		/>
	</div>
</AppShell>
