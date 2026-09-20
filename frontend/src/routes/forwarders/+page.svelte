<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { forwarders as seedForwarders } from '$lib/data/trade';
	import { listForwarders } from '$lib/api/forwarders';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { getForwarderRecommendations } from '$lib/api/forwarders';
	import type { Forwarder } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const modeFilters = ['All', 'Ocean', 'Air', 'Multimodal'];
	let activeFilter = $state('All');
	let query = $state('');

	let forwarders = createRemoteList(listForwarders, seedForwarders);
	$effect(() => {
		forwarders.load();
	});

	let filteredForwarders = $derived(
		forwarders.items.filter((forwarder) => {
			const matchesFilter = activeFilter === 'All' || forwarder.mode === activeFilter;
			const matchesQuery = [forwarder.name, forwarder.coverage, forwarder.mode, ...forwarder.lanes]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	// Forwarder Recommendations
	let recDest = $state('JP');
	let recs = $state<Forwarder[]>([]);
	let recsLoading = $state(false);
	let recsError = $state('');
	const DEST_OPTIONS = [
		{ code: 'JP', name: 'Jepang' },
		{ code: 'US', name: 'Amerika Serikat' },
		{ code: 'DE', name: 'Jerman' },
		{ code: 'SG', name: 'Singapura' },
		{ code: 'AU', name: 'Australia' },
		{ code: 'CN', name: 'Tiongkok' },
		{ code: 'KR', name: 'Korea Selatan' },
		{ code: 'GB', name: 'Inggris' },
		{ code: 'AE', name: 'UEA' },
		{ code: 'MY', name: 'Malaysia' },
	];

	async function loadRecommendations() {
		recsLoading = true;
		recsError = '';
		recs = [];
		try {
			const res = await getForwarderRecommendations(recDest);
			recs = res.data;
		} catch {
			recsError = t('Gagal memuat rekomendasi forwarder.');
		} finally {
			recsLoading = false;
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
	let pagedItems = $derived(paginate(filteredForwarders ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredForwarders?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Forwarder')} | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarders" eyebrow={t('Freight partner network')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Logistics network')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Verified freight partners for your export lanes.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Compare on-time rates, quote speed, and covered lanes, then request a quote for active shipments.')}</CardDescription>
		</CardHeader>
	</Card>

	<!-- Forwarder Recommendations -->
	<Card class="border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-indigo-500/10">
		<CardContent class="flex flex-wrap items-end justify-between gap-4 p-4">
			<div class="flex flex-wrap items-end gap-3">
				<div class="grid gap-1.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Rekomendasi Forwarder')}</span>
					<select class="h-10 rounded-md border bg-background px-3 text-sm" bind:value={recDest}>
						{#each DEST_OPTIONS as opt}
							<option value={opt.code}>{opt.name} ({opt.code})</option>
						{/each}
					</select>
				</div>
				<Button onclick={loadRecommendations} disabled={recsLoading}>
					{recsLoading ? t('Memuat...') : t('Dapatkan Rekomendasi')}
				</Button>
			</div>
			{#if recs.length > 0}
				<span class="text-xs font-bold text-muted-foreground">{t('Top')} {recs.length} {t('forwarder ke')} {DEST_OPTIONS.find((o) => o.code === recDest)?.name}</span>
			{/if}
		</CardContent>
		{#if recsError}
			<CardContent class="pt-0"><p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{recsError}</p></CardContent>
		{/if}
		{#if recs.length > 0}
			<CardContent class="grid gap-2.5 pt-0 md:grid-cols-2">
				{#each recs as rec}
					<a href={`/forwarders/${rec.id}`} class="flex items-center justify-between gap-3 rounded-lg border bg-background/60 p-3 no-underline transition-colors hover:border-ring/40">
						<div>
							<strong class="text-sm">{rec.name}</strong>
							<p class="text-xs text-muted-foreground">
								⭐ {rec.averageRating?.toFixed(1) ?? '—'} · {rec.totalReviews ?? 0} {t('review')}
								{#if rec.lanes?.length}
									· {rec.lanes.slice(0, 2).join(', ')}
								{/if}
							</p>
						</div>
						<Button size="sm" variant="outline">{t('Lihat')}</Button>
					</a>
				{/each}
			</CardContent>
		{/if}
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each modeFilters as filter}
				<Button
					variant={activeFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (activeFilter = filter)}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search forwarder, lane, coverage...')} class="max-w-xs" />
	</div>

	{#if forwarders.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{forwarders.error}</p>
	{/if}

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#if forwarders.loading}
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-4 w-16" />
					</div>
					<Skeleton class="mt-2 h-7 w-3/4" />
					<Skeleton class="mt-1 h-4 w-1/2" />
					<div class="mt-4 grid gap-2 sm:grid-cols-3">
						<Skeleton class="h-16 w-full rounded-lg" />
						<Skeleton class="h-16 w-full rounded-lg" />
						<Skeleton class="h-16 w-full rounded-lg" />
					</div>
					<div class="mt-4 flex flex-wrap gap-2">
						<Skeleton class="h-5 w-16 rounded-full" />
						<Skeleton class="h-5 w-20 rounded-full" />
						<Skeleton class="h-5 w-14 rounded-full" />
					</div>
				</Card>
			{/each}
		{:else}
			{#each pagedItems as forwarder}
				<Card class="transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/forwarders/${forwarder.id}`} class="grid h-full gap-3 p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(forwarder.status))}>{forwarder.status}</Badge>
							<span class="text-sm text-muted-foreground">{forwarder.mode}</span>
						</div>
						<h3 class="text-2xl font-bold tracking-tight">{forwarder.name}</h3>
						<p class="text-sm text-muted-foreground">{forwarder.coverage}</p>
						<div class="grid gap-2 sm:grid-cols-3">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('On-time')}<strong class="mt-1 block text-sm font-bold text-foreground">{forwarder.onTimeRate}%</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Quote speed')}<strong class="mt-1 block text-sm font-bold text-foreground">{forwarder.quoteSpeed}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Lanes')}<strong class="mt-1 block text-sm font-bold text-foreground">{forwarder.lanes.length}</strong></div>
						</div>
						<div class="flex flex-wrap gap-2">
							{#each forwarder.lanes as lane}<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{lane}</span>{/each}
						</div>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No forwarder matched your filter.')}</div>
			{/each}
		{/if}
	</div>
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredForwarders?.length ?? 0} />

</AppShell>
