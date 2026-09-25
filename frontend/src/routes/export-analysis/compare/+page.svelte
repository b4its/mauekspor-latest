<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '$lib/components/ui/table/index.js';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { listCountries, compareExportAnalyses, downloadComparePdf } from '$lib/api/export-analysis';
	import type { CompareResult } from '$lib/api/export-analysis';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { Product } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';

	import SearchIcon from '@lucide/svelte/icons/search';
	import TrophyIcon from '@lucide/svelte/icons/trophy';
	import DownloadIcon from '@lucide/svelte/icons/download';
	import AlertTriangleIcon from '@lucide/svelte/icons/alert-triangle';
	import LayoutGridIcon from '@lucide/svelte/icons/layout-grid';
	import TableIcon from '@lucide/svelte/icons/table';
	import XIcon from '@lucide/svelte/icons/x';
	import CheckIcon from '@lucide/svelte/icons/check';
	import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import ShieldAlertIcon from '@lucide/svelte/icons/shield-alert';
	import TrendingUpIcon from '@lucide/svelte/icons/trending-up';
	import ScaleIcon from '@lucide/svelte/icons/scale';

	let products = createRemoteList<Product>(listProducts, seedProducts);
	let countries = $state<{ country_code: string; country_name: string }[]>([]);
	let selectedProductId = $state('');
	let selectedCodes = $state<string[]>([]);
	let results = $state<CompareResult[] | null>(null);
	let comparing = $state(false);
	let downloadingPdf = $state(false);
	let error = $state('');
	let productName = $state('');
	let countrySearch = $state('');
	let viewMode = $state<'cards' | 'table'>('cards');

	const POPULAR_DESTINATIONS = [
		{ code: 'JP', name: 'Jepang' },
		{ code: 'SG', name: 'Singapura' },
		{ code: 'US', name: 'Amerika Serikat' },
		{ code: 'AE', name: 'Uni Emirat Arab' },
		{ code: 'CN', name: 'Tiongkok' },
		{ code: 'MY', name: 'Malaysia' },
		{ code: 'DE', name: 'Jerman' },
		{ code: 'AU', name: 'Australia' }
	];

	$effect(() => {
		products.load();
		listCountries()
			.then((res) => {
				countries = res.data;
			})
			.catch(() => {
				error = t('Gagal memuat daftar negara.');
			});
	});

	function countryFlag(code: string): string {
		if (!code || code.length !== 2) return '🌐';
		const upper = code.toUpperCase();
		const first = upper.codePointAt(0);
		const second = upper.codePointAt(1);
		if (!first || !second || first < 65 || first > 90 || second < 65 || second > 90) return '🌐';
		return String.fromCodePoint(first + 127397, second + 127397);
	}

	function toggleCountry(code: string) {
		if (selectedCodes.includes(code)) {
			selectedCodes = selectedCodes.filter((c) => c !== code);
		} else if (selectedCodes.length < 5) {
			selectedCodes = [...selectedCodes, code];
		}
	}

	function removeCountry(code: string) {
		selectedCodes = selectedCodes.filter((c) => c !== code);
	}

	function clearSelectedCountries() {
		selectedCodes = [];
	}

	const filteredCountries = $derived(
		countrySearch.trim()
			? countries.filter(
					(c) =>
						c.country_name.toLowerCase().includes(countrySearch.trim().toLowerCase()) ||
						c.country_code.toLowerCase().includes(countrySearch.trim().toLowerCase())
				)
			: countries
	);

	const selectedCountryObjects = $derived(
		selectedCodes.map((code) => {
			const found = countries.find((c) => c.country_code === code);
			return {
				code,
				name: found ? found.country_name : code
			};
		})
	);

	async function runCompare() {
		error = '';
		if (!selectedProductId || selectedCodes.length < 2) {
			error = t('Pilih 1 produk dan minimal 2 negara.');
			return;
		}
		comparing = true;
		try {
			const res = await compareExportAnalyses({ product_id: selectedProductId, country_codes: selectedCodes });
			results = res.data.results;
			productName = res.data.product.name;
		} catch {
			error = t('Gagal menjalankan perbandingan.');
		} finally {
			comparing = false;
		}
	}

	async function handleDownloadPdf() {
		if (!selectedProductId || selectedCodes.length < 2) return;
		downloadingPdf = true;
		try {
			await downloadComparePdf({ product_id: selectedProductId, country_codes: selectedCodes });
		} catch {
			error = t('Gagal mengunduh PDF.');
		} finally {
			downloadingPdf = false;
		}
	}

	function scoreTone(score: number): 'default' | 'outline' | 'destructive' {
		if (score >= 80) return 'default';
		if (score >= 50) return 'outline';
		return 'destructive';
	}

	function scoreColorClass(score: number): string {
		if (score >= 80) return 'text-emerald-600 dark:text-emerald-400';
		if (score >= 50) return 'text-amber-600 dark:text-amber-400';
		return 'text-rose-600 dark:text-rose-400';
	}

	function scoreBgClass(score: number): string {
		if (score >= 80) return 'bg-emerald-500';
		if (score >= 50) return 'bg-amber-500';
		return 'bg-rose-500';
	}

	const bestResult = $derived(results && results.length > 0 ? results[0] : null);
</script>

<svelte:head>
	<title>{t('Bandingkan Pasar')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Bandingkan Pasar')} eyebrow={t('Decision support')}>
	<div class="space-y-6">
		<!-- Panel Hero -->
		<Card class="panel-hero border-none bg-gradient-to-br from-[#0b1d3a] to-[#1e3a5f] p-6 text-white md:p-8 shadow-xl">
			<CardHeader class="p-0">
				<div class="flex items-center gap-2">
					<Badge variant="outline" class="border-white/30 bg-white/10 text-white font-medium">
						<SparklesIcon class="mr-1.5 size-3.5 inline-block text-amber-300" />
						{t('Decision support')}
					</Badge>
				</div>
				<CardTitle class="mt-3 font-display text-3xl font-black tracking-tight text-white md:text-4xl">
					{t('Bandingkan 2-5 negara untuk satu produk.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed text-slate-200">
					{t('Pilih produk yang sudah di-enrich, pilih 2-5 negara tujuan, lalu bandingkan skor kesiapan, grade, dan isu kepatuhan.')}
				</CardDescription>
			</CardHeader>
		</Card>

		<!-- Configuration Card -->
		<Card class="shadow-sm">
			<CardContent class="grid gap-6 p-6">
				<!-- Step 1: Select Product -->
				<div class="grid gap-2">
					<div class="flex items-center justify-between">
						<label class="text-xs font-bold uppercase tracking-wider text-muted-foreground" for="cmp-product">
							{t('1. Pilih produk')}
						</label>
						{#if selectedProductId}
							<Badge variant="secondary" class="text-xs font-semibold">
								{products.items.find((p) => p.id === selectedProductId)?.name || ''}
							</Badge>
						{/if}
					</div>
					<SearchableSelect
						bind:value={selectedProductId}
						placeholder={t('— Pilih produk —')}
						options={products.items.map((p) => ({
							value: p.id,
							label: p.name,
							sub: p.hs ? `HS ${p.hs}` : ''
						}))}
					/>
				</div>

				<!-- Step 2: Select Countries -->
				<div class="grid gap-3 border-t pt-5">
					<div class="flex flex-wrap items-center justify-between gap-2">
						<label class="text-xs font-bold uppercase tracking-wider text-muted-foreground" for="cmp-countries">
							{t('Pilih negara tujuan (2 - 5 negara)')}
						</label>
						<div class="flex items-center gap-2">
							<Badge variant={selectedCodes.length >= 2 ? 'default' : 'outline'} class="text-xs font-semibold">
								{selectedCodes.length} / 5 {t('dipilih')}
							</Badge>
							{#if selectedCodes.length > 0}
								<button
									type="button"
									onclick={clearSelectedCountries}
									class="text-xs text-muted-foreground hover:text-destructive transition-colors font-medium underline"
								>
									{t('Hapus Semua')}
								</button>
							{/if}
						</div>
					</div>

					<!-- Selected Countries Tray -->
					{#if selectedCountryObjects.length > 0}
						<div class="flex flex-wrap items-center gap-2 rounded-xl bg-muted/40 p-3 border border-border/60">
							<span class="text-xs font-medium text-muted-foreground flex items-center gap-1.5 mr-1">
								<GlobeIcon class="size-3.5" />
								{t('Negara Dipilih')}:
							</span>
							{#each selectedCountryObjects as country}
								<span
									class="inline-flex items-center gap-1.5 rounded-lg bg-primary/10 border border-primary/20 px-2.5 py-1 text-xs font-semibold text-primary shadow-xs"
								>
									<span>{countryFlag(country.code)}</span>
									<span>{country.name}</span>
									<span class="text-[10px] opacity-70">({country.code})</span>
									<button
										type="button"
										onclick={() => removeCountry(country.code)}
										class="ml-0.5 rounded-full p-0.5 hover:bg-primary/20 text-primary transition-colors"
										aria-label="Remove country"
									>
										<XIcon class="size-3" />
									</button>
								</span>
							{/each}
						</div>
					{/if}

					<!-- Quick-Pick Major Destinations -->
					<div class="space-y-1.5">
						<span class="text-[11px] font-semibold text-muted-foreground">
							{t('Pasar Ekspor Utama:')}
						</span>
						<div class="flex flex-wrap gap-1.5">
							{#each POPULAR_DESTINATIONS as dest}
								{@const isSelected = selectedCodes.includes(dest.code)}
								{@const isDisabled = !isSelected && selectedCodes.length >= 5}
								<button
									type="button"
									disabled={isDisabled}
									onclick={() => toggleCountry(dest.code)}
									class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-all {isSelected
										? 'border-primary bg-primary text-primary-foreground font-semibold shadow-xs'
										: isDisabled
											? 'border-border/40 bg-muted/20 text-muted-foreground/50 cursor-not-allowed'
											: 'border-border bg-background hover:bg-muted/60 text-foreground'}"
								>
									<span>{countryFlag(dest.code)}</span>
									<span>{dest.name}</span>
									{#if isSelected}
										<CheckIcon class="size-3 ml-0.5" />
									{/if}
								</button>
							{/each}
						</div>
					</div>

					<!-- Search & Scrollable Country Grid -->
					<div class="space-y-2 mt-1">
						<div class="relative">
							<SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
							<input
								type="text"
								bind:value={countrySearch}
								placeholder={t('Cari nama atau kode negara...')}
								class="h-9 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-xs placeholder:text-muted-foreground focus:outline-hidden focus:ring-2 focus:ring-ring"
							/>
						</div>

						<div class="max-h-44 overflow-y-auto rounded-xl border border-border/70 bg-card p-2.5">
							{#if filteredCountries.length === 0}
								<p class="py-4 text-center text-xs text-muted-foreground">
									{t('Tidak ada negara yang cocok dengan pencarian.')}
								</p>
							{:else}
								<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5">
									{#each filteredCountries as country}
										{@const isSelected = selectedCodes.includes(country.country_code)}
										{@const isDisabled = !isSelected && selectedCodes.length >= 5}
										<button
											type="button"
											disabled={isDisabled}
											onclick={() => toggleCountry(country.country_code)}
											class="flex items-center justify-between gap-1 rounded-lg border px-2.5 py-1.5 text-xs text-left transition-colors {isSelected
												? 'border-primary bg-primary/10 text-primary font-bold shadow-xs'
												: isDisabled
													? 'border-border/30 bg-muted/10 text-muted-foreground/40 cursor-not-allowed'
													: 'border-border/60 bg-background hover:bg-muted/50 text-foreground'}"
										>
											<span class="truncate flex items-center gap-1.5">
												<span class="shrink-0">{countryFlag(country.country_code)}</span>
												<span class="truncate font-medium">{country.country_name}</span>
											</span>
											<span class="text-[10px] text-muted-foreground shrink-0 font-mono">
												{country.country_code}
											</span>
										</button>
									{/each}
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Action Button & Errors -->
				<div class="flex flex-col sm:flex-row items-center justify-between gap-3 border-t pt-4">
					<p class="text-xs text-muted-foreground">
						{#if selectedCodes.length < 2}
							{t('Pilih minimal 2 negara di atas untuk memulai analisis komparasi multi-pasar.')}
						{:else}
							{selectedCodes.length} {t('negara siap dibandingkan.')}
						{/if}
					</p>

					<Button
						onclick={runCompare}
						disabled={comparing || selectedCodes.length < 2 || !selectedProductId}
						class="w-full sm:w-auto px-6 font-bold shadow-sm"
					>
						{#if comparing}
							<span class="inline-block size-4 animate-spin rounded-full border-2 border-current border-t-transparent mr-2"></span>
							{t('Membandingkan...')}
						{:else}
							<SparklesIcon class="mr-1.5 size-4" />
							{t('Bandingkan')}
						{/if}
					</Button>
				</div>

				{#if error}
					<div class="flex items-center gap-2 rounded-xl bg-destructive/10 border border-destructive/20 p-3.5 text-sm font-semibold text-destructive">
						<AlertTriangleIcon class="size-4 shrink-0" />
						<span>{error}</span>
					</div>
				{/if}
			</CardContent>
		</Card>

		<!-- Results Section -->
		{#if results}
			<div class="space-y-6">
				<!-- Top Market Spotlight Banner -->
				{#if bestResult}
					<Card class="overflow-hidden border-emerald-500/30 bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent shadow-md">
						<CardContent class="p-6">
							<div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
								<div class="flex items-start gap-4">
									<div class="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 shadow-inner">
										<TrophyIcon class="size-7" />
									</div>
									<div class="space-y-1">
										<div class="flex flex-wrap items-center gap-2">
											<Badge variant="default" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold">
												<TrophyIcon class="mr-1 size-3" />
												{t('Negara Rekomendasi Utama')}
											</Badge>
											<span class="text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider">
												{bestResult.country}
											</span>
										</div>
										<h3 class="text-2xl font-black tracking-tight text-foreground flex items-center gap-2">
											<span>{countryFlag(bestResult.country)}</span>
											<span>{bestResult.countryName || bestResult.country}</span>
										</h3>
										<p class="max-w-2xl text-xs leading-relaxed text-muted-foreground">
											{bestResult.recommendation}
										</p>
									</div>
								</div>

								<div class="flex flex-row md:flex-col items-center md:items-end gap-3 shrink-0 w-full md:w-auto justify-between border-t md:border-t-0 pt-3 md:pt-0">
									<div class="text-left md:text-right">
										<span class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
											{t('Skor Kesiapan')}
										</span>
										<span class="font-display text-3xl font-black text-emerald-600 dark:text-emerald-400">
											{bestResult.score}<span class="text-base text-muted-foreground font-normal">/100</span>
										</span>
									</div>
									<a
										href={bestResult.analysisId ? `/export-analysis/${bestResult.analysisId}` : `/export-analysis?country=${bestResult.country}&product=${selectedProductId}`}
										class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-bold text-white hover:bg-emerald-700 transition-colors shadow-xs"
									>
										<span>{t('Buka Analisis Lengkap')}</span>
										<ArrowRightIcon class="size-3.5" />
									</a>
								</div>
							</div>
						</CardContent>
					</Card>
				{/if}

				<!-- Controls Bar: View Toggle & PDF Export -->
				<div class="flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-card p-3 shadow-xs">
					<div class="flex items-center gap-2">
						<span class="text-xs font-bold text-foreground">
							{t('Perbandingan Pasar:')}
						</span>
						<Badge variant="outline" class="font-semibold text-xs">
							{productName}
						</Badge>
					</div>

					<div class="flex items-center gap-2">
						<!-- View Mode Toggle -->
						<div class="inline-flex rounded-lg border bg-muted/40 p-1">
							<button
								type="button"
								onclick={() => (viewMode = 'cards')}
								class="inline-flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-bold transition-all {viewMode === 'cards'
									? 'bg-background text-foreground shadow-xs'
									: 'text-muted-foreground hover:text-foreground'}"
							>
								<LayoutGridIcon class="size-3.5" />
								<span>{t('Tampilan Kartu')}</span>
							</button>
							<button
								type="button"
								onclick={() => (viewMode = 'table')}
								class="inline-flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-bold transition-all {viewMode === 'table'
									? 'bg-background text-foreground shadow-xs'
									: 'text-muted-foreground hover:text-foreground'}"
							>
								<TableIcon class="size-3.5" />
								<span>{t('Tampilan Matriks')}</span>
							</button>
						</div>

						<!-- PDF Export Button -->
						<Button
							variant="outline"
							size="sm"
							onclick={handleDownloadPdf}
							disabled={downloadingPdf}
							class="text-xs font-bold gap-1.5"
						>
							<DownloadIcon class="size-3.5" />
							<span>{downloadingPdf ? t('Mengunduh PDF...') : t('Unduh PDF Perbandingan')}</span>
						</Button>
					</div>
				</div>

				<!-- VIEW 1: Side-by-Side Cards (Clean, Responsive, No Overlap) -->
				{#if viewMode === 'cards'}
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						{#each results as result, idx}
							{@const isBest = idx === 0}
							<Card class="flex flex-col justify-between overflow-hidden transition-all hover:shadow-md {isBest ? 'border-emerald-500/40 shadow-sm ring-1 ring-emerald-500/20' : ''}">
								<CardHeader class="p-5 pb-3">
									<div class="flex items-start justify-between gap-2">
										<div class="flex items-center gap-2.5">
											<span class="text-3xl leading-none">{countryFlag(result.country)}</span>
											<div>
												<CardTitle class="text-lg font-bold text-foreground">
													{result.countryName || result.country}
												</CardTitle>
												<span class="text-xs font-mono font-semibold text-muted-foreground uppercase">
													{result.country}
												</span>
											</div>
										</div>

										{#if isBest}
											<Badge variant="default" class="bg-emerald-600 text-white font-bold text-[11px] gap-1 shrink-0">
												<TrophyIcon class="size-3" />
												#1 Terbaik
											</Badge>
										{:else}
											<Badge variant="outline" class="font-bold text-xs shrink-0 text-muted-foreground">
												#{idx + 1}
											</Badge>
										{/if}
									</div>
								</CardHeader>

								<CardContent class="grid gap-4 p-5 pt-0 flex-1">
									<!-- Score Section -->
									<div class="space-y-1.5 rounded-xl bg-muted/40 p-3.5 border border-border/50">
										<div class="flex items-baseline justify-between">
											<span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
												{t('Skor Kesiapan')}
											</span>
											<div class="flex items-baseline gap-1.5">
												<span class="font-display text-2xl font-black {scoreColorClass(result.score)}">
													{result.score}
												</span>
												<span class="text-xs text-muted-foreground font-semibold">/ 100</span>
												<Badge variant={scoreTone(result.score)} class="ml-1 text-[10px] font-bold">
													{result.grade}
												</Badge>
											</div>
										</div>
										<!-- Custom Score Bar -->
										<div class="h-2 w-full rounded-full bg-muted overflow-hidden">
											<div
												class="h-full rounded-full transition-all duration-500 {scoreBgClass(result.score)}"
												style="width: {Math.max(5, Math.min(100, result.score))}%"
											></div>
										</div>
									</div>

									<!-- Key Metrics List -->
									<div class="grid grid-cols-2 gap-2 text-xs">
										<div class="rounded-lg border bg-card p-2.5 space-y-1">
											<span class="text-muted-foreground flex items-center gap-1 text-[11px] font-medium">
												<ShieldAlertIcon class="size-3" />
												{t('Isu Kritis')}
											</span>
											<div class="flex items-center gap-1.5 font-bold">
												{#if result.critical_issues > 0}
													<span class="inline-flex size-2 rounded-full bg-destructive"></span>
													<span class="text-destructive">{result.critical_issues} {t('Isu')}</span>
												{:else}
													<span class="inline-flex size-2 rounded-full bg-emerald-500"></span>
													<span class="text-emerald-600 dark:text-emerald-400">0 {t('Aman')}</span>
												{/if}
											</div>
										</div>

										<div class="rounded-lg border bg-card p-2.5 space-y-1">
											<span class="text-muted-foreground flex items-center gap-1 text-[11px] font-medium">
												<TrendingUpIcon class="size-3" />
												{t('Permintaan Pasar')}
											</span>
											<span class="font-bold text-foreground block truncate">
												{result.marketDemand || 'Normal'}
											</span>
										</div>

										<div class="col-span-2 rounded-lg border bg-card p-2.5 flex items-center justify-between">
											<span class="text-muted-foreground flex items-center gap-1 text-[11px] font-medium">
												<ScaleIcon class="size-3" />
												{t('Estimasi Tarif / Bea')}
											</span>
											<span class="font-bold font-mono text-foreground text-xs">
												{result.duties || 'Sesuai FTA / MFN'}
											</span>
										</div>
									</div>

									<!-- Strategic Recommendation (Guaranteed No Overlap with Normal Whitespace & Proper Container) -->
									<div class="space-y-1.5 rounded-xl border border-border/60 bg-muted/20 p-3.5">
										<span class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
											<SparklesIcon class="size-3 text-amber-500" />
											{t('Rekomendasi AI & Catatan Regulasi')}
										</span>
										<p class="whitespace-normal break-words text-xs leading-relaxed text-foreground/90 font-normal">
											{result.recommendation}
										</p>
									</div>

									<!-- Action Link -->
									<div class="pt-2 border-t mt-auto">
										<a
											href={result.analysisId ? `/export-analysis/${result.analysisId}` : `/export-analysis?country=${result.country}&product=${selectedProductId}`}
											class="flex items-center justify-center gap-1.5 w-full rounded-lg border bg-card hover:bg-muted/60 py-2 px-3 text-xs font-bold text-foreground transition-colors shadow-xs"
										>
											<span>{t('Buka Analisis Lengkap')}</span>
											<ArrowRightIcon class="size-3.5 text-muted-foreground" />
										</a>
									</div>
								</CardContent>
							</Card>
						{/each}
					</div>
				{/if}

				<!-- VIEW 2: Comparison Matrix Table (Table Layout with Explicit Wrapping) -->
				{#if viewMode === 'table'}
					<Card class="overflow-hidden shadow-sm">
						<div class="overflow-x-auto">
							<Table class="w-full border-collapse">
								<TableHeader>
									<TableRow class="bg-muted/40 hover:bg-muted/40">
										<TableHead class="w-44 min-w-[176px] font-bold text-foreground p-4 text-left border-r">
											{t('Metrik')}
										</TableHead>
										{#each results as result, idx}
											<TableHead class="min-w-[280px] max-w-[340px] text-center p-4 border-r last:border-r-0 {idx === 0 ? 'bg-emerald-500/5' : ''}">
												<div class="flex items-center justify-center gap-2">
													<span class="text-xl">{countryFlag(result.country)}</span>
													<span class="font-bold text-foreground">{result.countryName || result.country}</span>
													<span class="text-xs font-mono text-muted-foreground">({result.country})</span>
													{#if idx === 0}
														<Badge variant="default" class="bg-emerald-600 text-white font-bold text-[10px] ml-1">
															⭐ {t('Terbaik')}
														</Badge>
													{/if}
												</div>
											</TableHead>
										{/each}
									</TableRow>
								</TableHeader>
								<TableBody>
									<!-- Row: Produk -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-3.5 border-r bg-muted/10">
											{t('Produk')}
										</TableCell>
										{#each results as _}
											<TableCell class="text-center font-medium p-3.5 border-r last:border-r-0 whitespace-normal">
												{productName}
											</TableCell>
										{/each}
									</TableRow>

									<!-- Row: Skor Kesiapan -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-3.5 border-r bg-muted/10">
											{t('Skor Kesiapan')}
										</TableCell>
										{#each results as result}
											<TableCell class="text-center p-3.5 border-r last:border-r-0 whitespace-normal">
												<div class="flex items-center justify-center gap-2">
													<span class="font-display text-lg font-black {scoreColorClass(result.score)}">
														{result.score}
													</span>
													<span class="text-xs text-muted-foreground">/ 100</span>
													<Badge variant={scoreTone(result.score)} class="font-bold text-xs">
														{result.grade}
													</Badge>
												</div>
											</TableCell>
										{/each}
									</TableRow>

									<!-- Row: Isu Kritis -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-3.5 border-r bg-muted/10">
											{t('Isu Kritis')}
										</TableCell>
										{#each results as result}
											<TableCell class="text-center p-3.5 border-r last:border-r-0 whitespace-normal">
												{#if result.critical_issues > 0}
													<Badge variant="destructive" class="font-bold text-xs gap-1">
														<AlertTriangleIcon class="size-3" />
														{result.critical_issues} {t('Isu Kritis')}
													</Badge>
												{:else}
													<Badge variant="outline" class="border-emerald-500/40 text-emerald-600 dark:text-emerald-400 font-bold text-xs gap-1">
														<CheckIcon class="size-3" />
														0 {t('Isu Kritis')}
													</Badge>
												{/if}
											</TableCell>
										{/each}
									</TableRow>

									<!-- Row: Permintaan Pasar -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-3.5 border-r bg-muted/10">
											{t('Permintaan Pasar')}
										</TableCell>
										{#each results as result}
											<TableCell class="text-center font-semibold p-3.5 border-r last:border-r-0 whitespace-normal">
												{result.marketDemand || 'Normal'}
											</TableCell>
										{/each}
									</TableRow>

									<!-- Row: Estimasi Tarif / Bea -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-3.5 border-r bg-muted/10">
											{t('Estimasi Tarif / Bea')}
										</TableCell>
										{#each results as result}
											<TableCell class="text-center font-mono text-xs font-semibold p-3.5 border-r last:border-r-0 whitespace-normal">
												{result.duties || 'Sesuai FTA / MFN'}
											</TableCell>
										{/each}
									</TableRow>

									<!-- Row: Rekomendasi AI (Crucial: whitespace-normal break-words to prevent collision) -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-4 border-r bg-muted/10 align-top">
											{t('Rekomendasi AI')}
										</TableCell>
										{#each results as result}
											<TableCell class="p-4 border-r last:border-r-0 align-top whitespace-normal break-words min-w-[280px] max-w-[340px]">
												<div class="rounded-xl border border-border/60 bg-muted/30 p-3.5 text-xs leading-relaxed whitespace-normal break-words text-foreground/90 font-normal">
													{result.recommendation}
												</div>
											</TableCell>
										{/each}
									</TableRow>

									<!-- Row: Aksi / Detail -->
									<TableRow>
										<TableCell class="font-bold text-muted-foreground p-3.5 border-r bg-muted/10">
											{t('Aksi')}
										</TableCell>
										{#each results as result}
											<TableCell class="text-center p-3.5 border-r last:border-r-0 whitespace-normal">
												<a
													href={result.analysisId ? `/export-analysis/${result.analysisId}` : `/export-analysis?country=${result.country}&product=${selectedProductId}`}
													class="inline-flex items-center gap-1 text-xs font-bold text-primary hover:underline"
												>
													<span>{t('Lihat Detail')}</span>
													<ArrowRightIcon class="size-3" />
												</a>
											</TableCell>
										{/each}
									</TableRow>
								</TableBody>
							</Table>
						</div>
					</Card>
				{/if}
			</div>
		{/if}
	</div>
</AppShell>
