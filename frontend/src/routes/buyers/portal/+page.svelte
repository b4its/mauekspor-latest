<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';
	import { statusTone } from '$lib/utils/format';
	import { listBuyerPortal, type BuyerPortalItem, type BuyerPortalMeta } from '$lib/api/buyers';
	import { listCountries, getCountry, type Country } from '$lib/api/export-analysis';
	import { seedCountries } from '$lib/data/trade';
	import { fetchSession, getStatus, getUser } from '$lib/stores/session.svelte';
	import { t } from '$lib/i18n.svelte';

	let allowed = $derived(
		getStatus() === 'authenticated' && (getUser()?.role === 'Admin' || getUser()?.role === 'Buyer')
	);
	$effect(() => {
		if (getStatus() === 'loading') fetchSession();
	});

	/** Kode ISO alpha-2 → emoji bendera (pola sama dengan halaman Countries). */
	function flagEmoji(code: string) {
		if (!code || code.length !== 2) return '🏳️';
		return String.fromCodePoint(...[...code.toUpperCase()].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65));
	}

	let allCountries = $state<{ code: string; name: string }[]>([]);
	let selectedCountry = $state('');
	let query = $state('');
	let items = $state<BuyerPortalItem[]>([]);
	let meta = $state<BuyerPortalMeta>({});
	let loading = $state(false);
	let error = $state('');
	let countryInfo = $state<Country | null>(null);
	let loadTimer: ReturnType<typeof setTimeout> | undefined;

	$effect(() => {
		listCountries()
			.then((res) => {
				allCountries = (res.data ?? [])
					.map((c) => ({ code: String(c.country_code ?? '').toUpperCase(), name: String(c.country_name ?? '') }))
					.filter((c) => c.code && c.name);
			})
			.catch(() => {
				allCountries = seedCountries.map((c) => ({ code: c.country_code, name: c.country_name }));
			});
	});

	async function loadPortal(country: string, search: string) {
		loading = true;
		error = '';
		try {
			const res = await listBuyerPortal({
				country: country || undefined,
				search: search || undefined
			});
			items = res.data;
			meta = res.meta;
		} catch {
			error = t('Gagal memuat portal pembeli.');
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		const a = allowed;
		const c = selectedCountry;
		const q = query.trim();
		if (!a) return;
		clearTimeout(loadTimer);
		loadTimer = setTimeout(() => loadPortal(c, q), 250);
		return () => clearTimeout(loadTimer);
	});

	let detectedCountry = $derived(meta.detectedCountry || '');
	let effectiveCountry = $derived(selectedCountry || detectedCountry);
	let effectiveCode = $derived(allCountries.find((c) => c.name === effectiveCountry)?.code ?? '');

	$effect(() => {
		const code = effectiveCode;
		if (!code) {
			countryInfo = null;
			return;
		}
		getCountry(code)
			.then((res) => (countryInfo = res.data))
			.catch(() => (countryInfo = null));
	});

	const riskTone: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
		Low: 'secondary',
		Moderate: 'outline',
		Elevated: 'default',
		High: 'destructive'
	};

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	let avgReadiness = $derived(
		Math.round(items.reduce((sum, item) => sum + (item.readiness ?? 0), 0) / (items.length || 1))
	);

	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(items ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(items?.length ?? 0, paginationPageSize));

	$effect(() => {
		selectedCountry;
		query;
		paginationPage = 1;
	});
</script>

<svelte:head>
	<title>{t('Portal Pembeli')} | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Portal" eyebrow={t('Export goods curated by buyer country')}>
	{#if !allowed}
		<div class="grid place-items-center gap-4 rounded-xl border border-destructive/30 bg-destructive/5 p-12 text-center">
			<div>
				<h2 class="text-xl font-bold">{t('Akses Ditolak')}</h2>
				<p class="mt-1 text-sm text-muted-foreground">{t('Halaman ini khusus Admin dan Pembeli.')}</p>
			</div>
			<div class="flex gap-2">
				<Button href="/login" variant="outline">{t('Masuk')}</Button>
				<Button href="/dashboard">{t('Kembali ke Dashboard')}</Button>
			</div>
		</div>
	{:else}
		<Card class="panel-hero p-6 md:p-8">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Portal pembeli')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Katalog ekspor dipilih berdasarkan negara asal pembeli.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed">
					{t('Temukan komoditas yang siap kirim ke negara Anda, lengkap dengan relevansi target market dan syarat impor tujuan.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<div class="grid gap-1">
					<label class="text-xs font-semibold uppercase tracking-wide text-muted-foreground" for="portal-country">
						{t('Negara asal pembeli')}
					</label>
					<NativeSelect id="portal-country" class="w-56" bind:value={selectedCountry}>
						<option value="">{t('Auto (sesuai profil saya)')}</option>
						{#each allCountries as country}
							<option value={country.name}>{flagEmoji(country.code)} {country.name}</option>
						{/each}
					</NativeSelect>
				</div>
				<Input bind:value={query} type="search" placeholder={t('Cari katalog, produk, pasar...')} class="max-w-xs" />
				{#if effectiveCountry}
					<Badge variant="outline" class="text-sm">
						{flagEmoji(effectiveCode)} {t('Negara asal terdeteksi')}: {effectiveCountry}
					</Badge>
				{/if}
			</CardContent>
		</Card>

		{#if error}
			<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}

		<div class="grid gap-4 sm:grid-cols-3">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Katalog relevan')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{items.length}</strong>
				</CardContent>
			</Card>
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Published total')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{meta.publishedTotal ?? '—'}</strong>
				</CardContent>
			</Card>
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Kesiapan rata-rata')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{avgReadiness}%</strong>
				</CardContent>
			</Card>
		</div>

		{#if effectiveCountry && !loading}
			<Card>
				<CardHeader class="p-0">
					<CardTitle class="text-lg">{t('Konteks regulasi')} · {flagEmoji(effectiveCode)} {effectiveCountry}</CardTitle>
					{#if countryInfo && !countryInfo.has_details}
						<CardDescription class="mt-1">
							{t('Detail regulasi belum tersedia untuk negara ini; konsultasikan dengan bea cukai setempat.')}
						</CardDescription>
					{/if}
				</CardHeader>
				{#if countryInfo}
					<CardContent class="grid gap-2 pt-4 sm:grid-cols-3">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Sistem kepabeanan')}
							<strong class="mt-1 block text-sm font-bold text-foreground">{countryInfo.customs_system || '—'}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Risiko')}
							<strong class="mt-1 block text-sm font-bold text-foreground">
								<Badge variant={riskTone[countryInfo.risk_level ?? ''] ?? 'outline'}>{countryInfo.risk_level ?? '—'}</Badge>
							</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Mata uang')}
							<strong class="mt-1 block text-sm font-bold text-foreground">{countryInfo.currency || '—'}</strong>
						</div>
						{#if (countryInfo.import_rules ?? [])[0]}
							<div class="rounded-lg border bg-muted/40 p-3 text-xs sm:col-span-3">
								<span class="font-bold text-muted-foreground">{t('Aturan impor utama')}</span>
								<ul class="mt-1 list-disc space-y-1 ps-4 text-foreground">
									{#each (countryInfo.import_rules ?? []).slice(0, 3) as rule}
										<li>{rule}</li>
									{/each}
								</ul>
							</div>
						{/if}
						<a
							href={effectiveCode ? `/countries/${effectiveCode}` : '/countries'}
							class="w-fit text-sm font-semibold text-primary underline-offset-4 hover:underline"
						>
							{t('Lihat detail negara')} →
						</a>
					</CardContent>
				{:else}
					<CardContent class="pt-4">
						<p class="text-sm text-muted-foreground">{t('Memuat konteks regulasi...')}</p>
					</CardContent>
				{/if}
			</Card>
		{/if}

		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#if loading}
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
						</div>
					</Card>
				{/each}
			{:else}
				{#each pagedItems as catalog}
					<Card class="transition-all hover:border-ring/40 hover:shadow-md">
						<a href={`/catalogs/${catalog.id}`} class="block h-full p-5 no-underline">
							<div class="flex items-center justify-between gap-3">
								<Badge variant={toneVariant(statusTone(catalog.status))}>{catalog.status}{#if catalog.relevanceScore} · {t('Relevansi')} {catalog.relevanceScore}%{/if}</Badge>
								<strong class="text-2xl font-bold tracking-tight">{catalog.readiness}%</strong>
							</div>
							<h3 class="mt-4 text-2xl font-bold tracking-tight">{catalog.title}</h3>
							<p class="mt-1 text-sm text-muted-foreground">
								{catalog.productName ?? catalog.productId}{#if catalog.productOrigin} · {catalog.productOrigin}{/if}
							</p>
							<div class="mt-4 grid grid-cols-2 gap-2">
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Market')} <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.targetMarket}</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('MOQ')} <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.moq}</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Lead time')} <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.leadTime}</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Price')} <strong class="mt-1 block text-sm font-bold text-foreground">{catalog.priceRange || '—'}</strong>
								</div>
							</div>
							{#if (catalog.highlights ?? [])[0]}
								<div class="mt-3 flex flex-wrap gap-1.5">
									{#each (catalog.highlights ?? []).slice(0, 3) as highlight}
										<Badge variant="secondary" class="font-normal">{highlight}</Badge>
									{/each}
								</div>
							{/if}
							<div class="mt-3 flex items-center justify-end">
								<Button size="sm" variant="outline">{t('Lihat katalog')}</Button>
							</div>
						</a>
					</Card>
				{:else}
					<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground md:col-span-2 xl:col-span-3">
						{t('Tidak ada katalog yang relevan dengan negara ini.')}
					</div>
				{/each}
			{/if}
		</div>

		<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={items?.length ?? 0} />
	{/if}
</AppShell>
