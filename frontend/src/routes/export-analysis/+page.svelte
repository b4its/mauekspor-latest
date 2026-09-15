<script lang="ts">
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

	let filteredAnalyses = $derived(
		exportAnalyses.items.filter((analysis) => {
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
</script>

<svelte:head>
	<title>{t('Analisis Ekspor')} | MauEkspor</title>
</svelte:head>

<AppShell title="Export Analysis" eyebrow={t('Intelijen kesiapan pasar')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Intelijen pasar AI')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Kenali tujuan sebelum Anda menawar.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Klasifikasi HS, bea masuk, pembatasan, dan rekomendasi regulasi untuk setiap pasangan produk-pasar.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/export-analysis/create">{t('Analisis baru')}</Button>
			<Button href="/export-analysis/compare" variant="outline">{t('Bandingkan pasar')}</Button>
			<Button href="/hs-codes" variant="outline">{t('Browsing HS code')}</Button>
			<Button href={csvExportUrl('/export-analysis/export.csv')} variant="outline">{t('Ekspor CSV')}</Button>
		</CardContent>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{trStatus(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari produk, tujuan, HS...')} class="max-w-xs" />
	</div>

	{#if exportAnalyses.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{exportAnalyses.error}</p>
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
			{#each filteredAnalyses as analysis}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(analysis.status))}>{trStatus(analysis.status)}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{analysis.score}</strong>
					</div>
					<h3 class="mt-3 text-2xl font-bold tracking-tight">{analysis.productName}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{analysis.destination} - HS {analysis.hsCode}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Keyakinan')}<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.confidence}%</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Permintaan')}<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.marketDemand}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Bea masuk')}<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.duties.split(' ')[0]}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Pembatasan')}<strong class="mt-1 block text-sm font-bold text-foreground">{analysis.restrictions.length}</strong></div>
					</div>
					<div class="mt-4 flex flex-wrap gap-3">
						<Button variant="ghost" size="sm" href={`/export-analysis/${analysis.id}`}>{t('Buka analisis')}</Button>
						<Button variant="outline" size="sm" href={`/export-analysis/${analysis.id}/regulation-recommendations`}>{t('Rekomendasi')}</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada analisis yang cocok dengan filter.')}</div>
			{/each}
		{/if}
	</div>
</AppShell>
