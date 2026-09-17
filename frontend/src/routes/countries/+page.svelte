<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '$lib/components/ui/card/index.js';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { listCountries, type Country } from '$lib/api/export-analysis';
	import { seedCountries } from '$lib/data/trade';
	import { filterCountries, computeCountryStats } from '$lib/data/countries';
	import { t } from '$lib/i18n.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';

	import GlobeIcon from '@lucide/svelte/icons/globe';
	import SearchIcon from '@lucide/svelte/icons/search';
	import MapIcon from '@lucide/svelte/icons/map';
	import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';

	const allRegions = ['Asia', 'Africa', 'Europe', 'Oceania', 'Americas', 'Antarctic'] as const;

	let countries = createRemoteList(
		async () => {
			const res = await listCountries();
			return { data: res.data.map((c) => ({ id: c.country_code, ...c })) };
		},
		seedCountries.map((c) => ({ id: c.country_code, ...c }))
	);
	let search = $state('');
	let region = $state('');
	let onlyDetailed = $state(false);

	$effect(() => {
		countries.load();
	});

	let filtered = $derived(filterCountries(countries.items, { search, region, onlyDetailed }));

	let paginationPage = $state(1);
	let paginationPageSize = $state(24);
	let pagedItems = $derived(paginate(filtered ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filtered?.length ?? 0, paginationPageSize));

	// Reset ke halaman 1 saat filter berubah
	$effect(() => {
		[search, region, onlyDetailed];
		paginationPage = 1;
	});

	let stats = $derived(computeCountryStats(countries.items));

	const riskTone: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
		Low: 'secondary',
		Moderate: 'outline',
		Elevated: 'default',
		High: 'destructive',
	};

	function flagEmoji(code: string) {
		return String.fromCodePoint(...[...code.toUpperCase()].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65));
	}
</script>

<svelte:head>
	<title>{t('Direktori Regulasi Negara')} | MauEkspor</title>
</svelte:head>

<AppShell title="Countries" eyebrow={t('Regulasi ekspor & impor seluruh dunia')}>
	<Card class="p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="max-w-2xl">
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">
					<MapIcon class="size-3.5" />
					{t('195+ jurisdictions')}
				</Badge>
				<h1 class="font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Regulasi ekspor & impor setiap negara di dunia.')}
				</h1>
				<CardDescription class="mt-2 max-w-xl leading-relaxed">
					{t('Direktori kepabeanan global: sistem tarif (BTKI/HTSUS/TARIC/GACC), FTA, aturan impor & ekspor, pajak, dokumen, dan otoritas resmi. Baseline 15 Agustus 2026 — verifikasi ulang sebelum shipment.')}
				</CardDescription>
			</div>
			<div class="flex flex-wrap gap-3">
				<Button href="/hs-codes" variant="outline">
					<GlobeIcon class="size-3.5" />
					{t('Klasifikasi HS')}
				</Button>
				<Button href="/export-analysis/compare" variant="outline">
					<ArrowRightIcon class="size-3.5" />
					{t('Bandingkan negara')}
				</Button>
			</div>
		</div>

		<div class="mt-6 flex flex-wrap items-center gap-3">
			<div class="flex min-w-56 flex-1 items-center gap-2 rounded-lg border border-border bg-white px-3 py-2 dark:bg-[#0a1730]">
				<SearchIcon class="size-4 text-muted-foreground" />
				<input
					type="text"
					placeholder={t('Cari negara atau kode ISO...')}
					bind:value={search}
					class="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
				/>
			</div>
			<select bind:value={region} class="h-10 rounded-lg border border-border bg-white px-3 text-sm dark:bg-[#0a1730]">
				<option value="">{t('Semua region')}</option>
				{#each allRegions as r}
					<option value={r}>{r}</option>
				{/each}
			</select>
			<label class="flex cursor-pointer items-center gap-2 text-sm font-semibold text-muted-foreground">
				<input type="checkbox" bind:checked={onlyDetailed} class="size-4 accent-[#0b3d91]" />
				{t('Hanya negara dengan data detail')}
			</label>
		</div>

		<div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
			<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
				<strong class="font-display text-3xl font-black text-[#0b3d91] dark:text-[#5ea1ff]">{stats.total}</strong>
				<span class="mt-1 block text-xs font-bold text-muted-foreground">{t('negara & wilayah')}</span>
			</div>
			<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
				<strong class="font-display text-3xl font-black text-[#0b3d91] dark:text-[#5ea1ff]">{stats.detailed}</strong>
				<span class="mt-1 block text-xs font-bold text-muted-foreground">{t('profil regulasi detail')}</span>
			</div>
			<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
				<strong class="font-display text-3xl font-black text-red-600">{stats.highRisk}</strong>
				<span class="mt-1 block text-xs font-bold text-muted-foreground">{t('risk elevated / high')}</span>
			</div>
			<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
				<strong class="font-display text-3xl font-black text-[#0b3d91] dark:text-[#5ea1ff]">2026</strong>
				<span class="mt-1 block text-xs font-bold text-muted-foreground">{t('snapshot data')}</span>
			</div>
		</div>
	</Card>

	{#if countries.loading}
		<p class="py-12 text-center text-sm text-muted-foreground">{t('Memuat direktori...')}</p>
	{:else if countries.error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">
			{countries.error}
		</p>
	{:else if filtered.length === 0}
		<p class="py-12 text-center text-sm text-muted-foreground">{t('Tidak ada negara ditemukan.')}</p>
	{:else}
		<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each pagedItems as c (c.country_code)}
				<a
					href={`/countries/${c.country_code}`}
					class="group flex flex-col gap-3 rounded-xl border border-border bg-card p-4 text-card-foreground transition-all hover:-translate-y-0.5 hover:border-[#0b3d91]/40 hover:shadow-lg"
				>
					<div class="flex items-center gap-3">
						<span class="grid size-9 shrink-0 place-items-center rounded-lg bg-secondary text-lg">{flagEmoji(c.country_code)}</span>
						<div class="min-w-0">
							<p class="truncate text-sm font-bold">{c.country_name}</p>
							<p class="truncate text-xs text-muted-foreground">
								{c.country_code} · {t(c.region ?? '')}
							</p>
						</div>
					</div>
					<div class="flex flex-wrap items-center gap-1.5">
						{#if c.customs_system && c.customs_system !== 'PRODCOM' && c.customs_system !== ''}
							<Badge variant="outline" class="text-[10px]">{c.customs_system}</Badge>
						{/if}
						{#if c.risk_level}
							<Badge variant={riskTone[c.risk_level] ?? 'outline'} class="text-[10px]">
								{t(c.risk_level)}
							</Badge>
						{/if}
						{#if c.has_details}
							<Badge class="text-[10px] bg-[#0b3d91]/10 text-[#0b3d91] dark:bg-white/10 dark:text-white">{c.regulationsCount ?? 0} {t('aturan')}</Badge>
						{/if}
					</div>
					{#if !c.has_details}
						<p class="text-[11px] leading-snug text-muted-foreground">
							{t('Profil detail belum tersedia — gunakan panduan regional via portal resmi.')}
						</p>
					{/if}
				</a>
			{/each}
		</div>
		<div class="mt-4">
			<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filtered?.length ?? 0} />
		</div>
	{/if}
</AppShell>
