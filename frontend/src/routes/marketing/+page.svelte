<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { products as seedProducts } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { getOrCreateMarketIntelligence, getOrCreateProductPricing } from '$lib/api/marketing';
	import type { MarketIntelligence, ProductPricing } from '$lib/api/marketing';
	import type { Product } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';

	let products = createRemoteList<Product>(listProducts, seedProducts);
products.load();

	let tab = $state<'mi' | 'pricing'>('mi');
	let search = $state('');
	let category = $state('All');
	let selectedProduct = $state<Product | null>(null);

	// Market Intelligence state
	let mi = $state<MarketIntelligence | null>(null);
	let miLoading = $state(false);
	let miError = $state('');

	// Pricing state
	let cogs = $state(10000);
	let margin = $state(30);
	let country = $state('JP');
	let pricing = $state<ProductPricing | null>(null);
	let pricingLoading = $state(false);
	let pricingError = $state('');

	const categories = $derived(['All', ...Array.from(new Set(products.items.map((p) => p.category)))]);
	const filtered = $derived(
		products.items.filter(
			(p) =>
				(category === 'All' || p.category === category) &&
				(search === '' || p.name.toLowerCase().includes(search.toLowerCase()))
		)
	);

	function openProduct(p: Product) {
		selectedProduct = p;
		if (tab === 'mi') openMarketIntelligence(p);
		else openPricing(p);
	}

	async function openMarketIntelligence(p: Product) {
		selectedProduct = p;
		mi = null;
		miError = '';
		miLoading = true;
		try {
			mi = await getOrCreateMarketIntelligence(p.id);
		} catch {
			miError = t('Gagal memuat Market Intelligence untuk produk ini.');
		} finally {
			miLoading = false;
		}
	}

	async function openPricing(p: Product) {
		selectedProduct = p;
		pricing = null;
		pricingError = '';
		pricingLoading = true;
		try {
			pricing = await getOrCreateProductPricing(p.id, {
				cogs_per_unit_idr: cogs,
				target_margin_percent: margin,
				target_country_code: country
			});
		} catch {
			pricingError = t('Gagal menghitung pricing untuk produk ini.');
		} finally {
			pricingLoading = false;
		}
	}

	function scoreTone(score: number) {
		if (score >= 80) return 'default';
		if (score >= 60) return 'outline';
		return 'secondary';
	}

	function fmtUsd(n: number | undefined) {
		if (n == null) return '—';
		return `$${n.toFixed(2)}`;
	}
</script>

<svelte:head>
	<title>Marketing | MauEkspor</title>
</svelte:head>

<AppShell title="Marketing" eyebrow={t('Intelijen pasar AI & penetapan harga')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">{t('Pusat Pemasaran AI')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{t('Kalkulator Market Intelligence & Pricing.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					{t('Generate rekomendasi negara tujuan (dengan forwarder) dan hitung harga EXW/FOB/CIF per produk.')}
				</CardDescription>
			</div>
		</div>
	</Card>

	<div class="flex flex-wrap gap-2">
		<Button variant={tab === 'mi' ? 'default' : 'outline'} onclick={() => (tab = 'mi')}>Market Intelligence</Button>
		<Button variant={tab === 'pricing' ? 'default' : 'outline'} onclick={() => (tab = 'pricing')}>{t('Kalkulator Pricing')}</Button>
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-center justify-between gap-3">
				<div class="flex flex-wrap gap-2">
					<Input placeholder={t('Cari produk...')} bind:value={search} class="w-56" />
					<select
						class="h-10 rounded-md border bg-background px-3 text-sm"
						bind:value={category}
					>
						{#each categories as c}
							<option value={c}>{c}</option>
						{/each}
					</select>
				</div>
				<CardDescription>{filtered.length} {t('produk')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
				{#each filtered as product}
					<button
						class="rounded-xl border bg-muted/30 p-4 text-left transition-colors hover:bg-muted/60"
						onclick={() => openProduct(product)}
					>
						<div class="flex items-center justify-between gap-2">
							<strong class="text-sm">{product.name}</strong>
							<Badge variant={product.status === 'Enriched' ? 'default' : 'secondary'}>{t(product.status === 'Enriched' ? 'Diperkaya' : 'Draf')}</Badge>
						</div>
						<span class="mt-1 block text-xs text-muted-foreground">{product.category} · HS {product.hs}</span>
						<span class="mt-1 block text-xs font-bold text-muted-foreground">{t('Kesiapan')} {product.readiness}%</span>
					</button>
				{/each}
			</CardContent>
		</Card>

		{#if tab === 'mi'}
			<Card class="md:col-span-2">
				<CardHeader class="flex-row items-center justify-between gap-3">
					<div>
						<CardTitle>Market Intelligence {selectedProduct ? `— ${selectedProduct.name}` : ''}</CardTitle>
						<CardDescription>{t('Negara yang direkomendasikan, risiko, tren, dan rekomendasi forwarder.')}</CardDescription>
					</div>
					{#if selectedProduct}
						<Button variant="outline" size="sm" onclick={() => openMarketIntelligence(selectedProduct!)} disabled={miLoading}>
							{miLoading ? t('Memuat...') : t('Muat ulang')}
						</Button>
					{/if}
				</CardHeader>
				<CardContent>
					{#if !selectedProduct}
						<p class="text-sm font-semibold text-muted-foreground">{t('Pilih produk di atas untuk melihat Market Intelligence.')}</p>
					{:else if miLoading && !mi}
						<p class="text-sm font-semibold text-muted-foreground">{t('Menganalisis pasar dengan AI...')}</p>
					{:else if miError}
						<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{miError}</p>
					{:else if mi}
						<div class="grid gap-4">
							<div>
								<h4 class="mb-2 text-sm font-bold uppercase tracking-wide text-muted-foreground">{t('Negara direkomendasikan')}</h4>
								<div class="grid gap-2.5 md:grid-cols-2">
									{#each mi.recommendedCountries ?? [] as rec}
										<div class="rounded-lg border bg-muted/30 p-4">
											<div class="flex items-center justify-between gap-2">
												<strong class="text-sm">{rec.country} ({rec.code})</strong>
												<Badge variant={scoreTone(rec.score)}>{rec.score}</Badge>
											</div>
											<p class="mt-1.5 text-xs leading-relaxed text-muted-foreground">{rec.reason}</p>
											{#if rec.market_size || rec.competition_level || rec.price_range}
												<p class="mt-1.5 text-xs text-muted-foreground">
													<b>{t('Pasar:')}</b> {rec.market_size ?? '—'} · <b>{t('Kompetisi:')}</b> {rec.competition_level ?? '—'} · <b>{t('Harga:')}</b> {rec.price_range ?? '—'}
												</p>
											{/if}
											{#if rec.entry_strategy}
												<p class="mt-1 text-xs text-muted-foreground"><b>{t('Strategi:')}</b> {rec.entry_strategy}</p>
											{/if}
											{#if rec.forwarders && rec.forwarders.length > 0}
												<div class="mt-2 grid gap-1.5">
													{#each rec.forwarders as fwd (fwd.id)}
														<div class="rounded-md border bg-background/60 px-2.5 py-1.5 text-xs">
															<b>{fwd.name}</b> {fwd.averageRating ? `· ⭐ ${fwd.averageRating}` : ''}
															{#if fwd.contactInfo?.phone}
																<span class="text-muted-foreground"> · {fwd.contactInfo.phone}</span>
															{/if}
														</div>
													{/each}
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>

							<div class="grid gap-4 md:grid-cols-2">
								{#if (mi.countriesToAvoid ?? []).length > 0}
									<div>
										<h4 class="mb-2 text-sm font-bold uppercase tracking-wide text-muted-foreground">{t('Negara dihindari')}</h4>
										<div class="grid gap-2">
											{#each mi.countriesToAvoid ?? [] as avoid}
												<div class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs">
													<b>{avoid.country} ({avoid.code})</b> — {avoid.reason}
												</div>
											{/each}
										</div>
									</div>
								{/if}
								<div>
									<h4 class="mb-2 text-sm font-bold uppercase tracking-wide text-muted-foreground">{t('Tren pasar')}</h4>
									<ul class="grid gap-1.5">
										{#each mi.marketTrends ?? [] as trend}
											<li class="rounded-lg border bg-muted/30 px-3 py-2 text-xs">• {trend}</li>
										{/each}
									</ul>
								</div>
							</div>

							{#if mi.overallRecommendation}
								<div class="rounded-xl border bg-primary/10 p-4 text-sm leading-relaxed">
									<b>{t('Rekomendasi keseluruhan:')}</b> {mi.overallRecommendation}
								</div>
							{/if}
						</div>
					{/if}
				</CardContent>
			</Card>
		{:else}
			<Card class="md:col-span-2">
				<CardHeader class="flex-row items-center justify-between gap-3">
					<div>
						<CardTitle>Pricing Calculator {selectedProduct ? `— ${selectedProduct.name}` : ''}</CardTitle>
						<CardDescription>{t('Hitung EXW/FOB/CIF dengan margin target dan kurs terbaru.')}</CardDescription>
					</div>
				</CardHeader>
				<CardContent class="grid gap-4">
					{#if !selectedProduct}
						<p class="text-sm font-semibold text-muted-foreground">{t('Pilih produk di atas untuk menghitung pricing.')}</p>
					{:else}
						<div class="grid gap-3 sm:grid-cols-3">
							<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
								{t('HPP (IDR / unit)')}
								<Input type="number" bind:value={cogs} />
							</label>
							<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
								{t('Target margin (%)')}
								<Input type="number" bind:value={margin} />
							</label>
							<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
								{t('Negara tujuan')}
								<select class="h-10 rounded-md border bg-background px-3 text-sm" bind:value={country}>
									<option value="JP">Japan</option>
									<option value="US">United States</option>
									<option value="DE">Germany</option>
									<option value="SG">Singapore</option>
									<option value="AU">Australia</option>
									<option value="CN">China</option>
									<option value="KR">South Korea</option>
									<option value="GB">United Kingdom</option>
									<option value="NL">Netherlands</option>
									<option value="AE">UAE</option>
								</select>
							</label>
						</div>
						<Button onclick={() => openPricing(selectedProduct!)} disabled={pricingLoading}>
							{pricingLoading ? t('Menghitung...') : t('Hitung pricing')}
						</Button>

						{#if pricingError}
							<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{pricingError}</p>
						{/if}

						{#if pricing}
							<div class="grid gap-3 sm:grid-cols-3">
								<div class="rounded-xl border bg-muted/40 p-4 text-center">
									<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">EXW</span>
									<strong class="mt-1 block text-2xl font-bold">{fmtUsd(pricing.exwPriceUsd)}</strong>
								</div>
								<div class="rounded-xl border bg-muted/40 p-4 text-center">
									<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">FOB</span>
									<strong class="mt-1 block text-2xl font-bold">{fmtUsd(pricing.fobPriceUsd)}</strong>
								</div>
								<div class="rounded-xl border bg-muted/40 p-4 text-center">
									<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">CIF</span>
									<strong class="mt-1 block text-2xl font-bold">{fmtUsd(pricing.cifPriceUsd)}</strong>
								</div>
							</div>

							<div class="grid gap-4 md:grid-cols-2">
								<div class="rounded-lg border bg-muted/30 p-4 text-xs">
									<h4 class="mb-2 font-bold uppercase tracking-wide text-muted-foreground">{t('Rincian')}</h4>
									{#if pricing.pricingBreakdown}
										{#each Object.entries(pricing.pricingBreakdown) as [key, value]}
											<div class="flex justify-between gap-3 border-b border-muted/40 py-1.5 last:border-0">
												<span class="text-muted-foreground">{key}</span>
												<b>{String(value)}</b>
											</div>
										{/each}
									{/if}
								</div>
								<div class="rounded-lg border bg-primary/10 p-4 text-sm leading-relaxed">
									<h4 class="mb-2 font-bold uppercase tracking-wide text-muted-foreground">AI Insight</h4>
									<p>{pricing.pricingInsight ?? t('Harga kompetitif untuk pasar tujuan.')}</p>
									<p class="mt-2 text-xs text-muted-foreground">
										{t('Kurs dipakai:')} {pricing.exchangeRateUsed} IDR/USD · {t('Margin')} {pricing.targetMarginPercent}%
									</p>
								</div>
							</div>
						{/if}
					{/if}
				</CardContent>
			</Card>
		{/if}
	</div>
</AppShell>
