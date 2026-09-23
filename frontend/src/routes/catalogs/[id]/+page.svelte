<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import {
		generateCatalogDescription,
		publishCatalog,
		unpublishCatalog,
		listCatalogImages,
		listVariantTypes,
		generateCatalogAiDescription,
		addCatalogImage,
		deleteCatalogImage,
		addVariantType,
		addVariantOption,
		deleteVariantType,
		deleteVariantOption,
		createCatalogPricing,
		createCatalogMarketIntelligence
	} from '$lib/api/catalogs';
	import { uploadFileBinary, fileDownloadUrl } from '$lib/api/files';
	import type { CatalogImage, VariantType, CatalogAIDescription } from '$lib/api/catalogs';
	import { t } from '$lib/i18n.svelte';

	type CatalogPricing = {
		exwPriceUsd?: number;
		fobPriceUsd?: number;
		cifPriceUsd?: number;
		pricingInsight?: string;
		exchangeRateUsed?: number;
		pricingBreakdown?: Record<string, unknown>;
	};

	type CatalogMI = {
		recommendedCountries?: { country: string; code: string; score: number; reason?: string }[];
		overallRecommendation?: string;
		marketTrends?: string[];
	};

	let { data } = $props();
	let published = $state(false);
	let error = $state('');

	let images = $state<CatalogImage[]>([]);
	let variantTypes = $state<VariantType[]>([]);
	let aiDesc = $state<CatalogAIDescription | null>(null);
	let loadingAi = $state(false);
	let newImageUrl = $state('');
	let uploading = $state(false);
	let newVariantType = $state('');
	let newVariantOption = $state<Record<string, string>>({});
	let variantError = $state('');
	let pricing = $state<CatalogPricing | null>(null);
	let marketIntel = $state<CatalogMI | null>(null);
	let aiLoading = $state(false);
	let aiError = $state('');

	async function handlePricing() {
		aiError = '';
		aiLoading = true;
		try {
			pricing = (await createCatalogPricing(data.catalog.id, {
				cogs_per_unit_idr: 28500,
				target_margin_percent: 22,
				target_country_code: 'JP'
			})).data as CatalogPricing;
		} catch {
			aiError = t('Gagal menghitung pricing untuk katalog.');
		} finally {
			aiLoading = false;
		}
	}

	async function handleMarketIntel() {
		aiError = '';
		aiLoading = true;
		try {
			marketIntel = (await createCatalogMarketIntelligence(data.catalog.id)).data as CatalogMI;
		} catch {
			aiError = t('Gagal memuat market intelligence untuk katalog.');
		} finally {
			aiLoading = false;
		}
	}

	async function reloadVariants() {
		variantTypes = (await listVariantTypes(data.catalog.id)).data.data;
	}

	async function handleAddVariantType() {
		variantError = '';
		if (newVariantType.trim().length < 2) {
			variantError = t('Nama tipe varian minimal 2 karakter.');
			return;
		}
		try {
			await addVariantType(data.catalog.id, { type_code: 'custom', type_name: newVariantType.trim() });
			newVariantType = '';
			await reloadVariants();
		} catch {
			variantError = t('Gagal menambah tipe varian.');
		}
	}

	async function handleAddVariantOption(typeId: string) {
		variantError = '';
		const name = (newVariantOption[typeId] ?? '').trim();
		if (!name) return;
		try {
			await addVariantOption(data.catalog.id, typeId, name);
			newVariantOption[typeId] = '';
			await reloadVariants();
		} catch {
			variantError = t('Gagal menambah opsi varian.');
		}
	}

	async function handleRemoveVariantType(typeId: string) {
		if (!confirm(t('Hapus tipe varian beserta opsinya?'))) return;
		try {
			await deleteVariantType(data.catalog.id, typeId);
			await reloadVariants();
		} catch {
			variantError = t('Gagal menghapus tipe varian.');
		}
	}

	async function handleRemoveVariantOption(typeId: string, optionId: string) {
		try {
			await deleteVariantOption(data.catalog.id, typeId, optionId);
			await reloadVariants();
		} catch {
			variantError = t('Gagal menghapus opsi varian.');
		}
	}

	$effect(() => {
		published = data.catalog.status === 'Published';
	});

	$effect(() => {
		listCatalogImages(data.catalog.id)
			.then((res) => (images = res.data))
			.catch(() => {});
		listVariantTypes(data.catalog.id)
			.then((res) => (variantTypes = res.data.data))
			.catch(() => {});
	});

	async function handleUploadImage(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		error = '';
		uploading = true;
		try {
			const res = await uploadFileBinary(file, 'Catalog Image', data.catalog.projectId ?? '', []);
			const url = fileDownloadUrl(res.data.id);
			await addCatalogImage(data.catalog.id, { image_url: url, alt_text: file.name });
			const imgs = (await listCatalogImages(data.catalog.id)).data;
			images = imgs;
		} catch {
			error = t('Gagal mengunggah gambar.');
		} finally {
			uploading = false;
			input.value = '';
		}
	}

	async function handleAddImageUrl() {
		error = '';
		if (!newImageUrl.trim()) return;
		try {
			await addCatalogImage(data.catalog.id, { image_url: newImageUrl.trim(), alt_text: '' });
			newImageUrl = '';
			images = (await listCatalogImages(data.catalog.id)).data;
		} catch {
			error = t('Gagal menambahkan gambar dari URL.');
		}
	}

	async function handleRemoveImage(imageId: string) {
		error = '';
		try {
			await deleteCatalogImage(data.catalog.id, imageId);
			images = images.filter((img) => img.id !== imageId);
		} catch {
			error = t('Gagal menghapus gambar.');
		}
	}

	async function handleGenerate() {
		error = '';
		loadingAi = true;
		try {
			const res = await generateCatalogAiDescription(data.catalog.id, false);
			aiDesc = res.data;
		} catch {
			try {
				await generateCatalogDescription(data.catalog.id);
			} catch {
				error = t('Gagal generate AI copy.');
			}
		} finally {
			loadingAi = false;
		}
	}

	async function handlePublish() {
		error = '';
		try {
			await publishCatalog(data.catalog.id);
			published = true;
		} catch {
			error = t('Gagal mempublikasikan katalog.');
		}
	}

	async function handleUnpublish() {
		error = '';
		try {
			await unpublishCatalog(data.catalog.id);
			published = false;
		} catch {
			error = t('Gagal menarik publikasi katalog.');
		}
	}

	let displayStatus = $derived(published ? 'Published' : data.catalog.status);
	let displayReadiness = $derived(published ? Math.max(data.catalog.readiness, 95) : data.catalog.readiness);
	let displayDescription = $derived(aiDesc?.export_description || data.catalog.description || '');

	function trStatus(s: string) {
		return t(s === 'Published' ? 'Diterbitkan' : s === 'Draft' ? 'Draf' : s);
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.catalog.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.catalog.id} eyebrow={t('Catalog detail')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{trStatus(displayStatus)}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.catalog.title}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.catalog.projectId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Catalog readiness')}</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayReadiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Buyer-Facing Copy')}</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl leading-relaxed">{displayDescription || t('Belum ada deskripsi katalog.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/catalogs/${data.catalog.id}/edit`}>{t('Edit katalog')}</Button>
					<Button variant="outline" onclick={handleGenerate} disabled={loadingAi}>
						{loadingAi ? t('Memproses...') : aiDesc ? t('Buat ulang AI copy') : t('Buat AI copy')}
					</Button>
					{#if published}
						<Button variant="outline" onclick={handleUnpublish}>{t('Tarik publikasi')}</Button>
					{:else}
						<Button onclick={handlePublish}>{t('Publikasikan katalog')}</Button>
					{/if}
				</div>
			</CardHeader>
			{#if error}
				<p class="rounded-lg bg-destructive/10 px-4 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Produk')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product?.name ?? data.catalog.productId}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Pasar target')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.targetMarket}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('MOQ')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.moq}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Waktu tunggu')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.leadTime}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Rentang harga')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.priceRange}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Gambar')} <strong class="mt-1 block text-sm font-bold text-foreground">{images.length}</strong>
				</div>
			</CardContent>
		</Card>

		{#if images.length > 0}
			<Card>
				<CardHeader class="flex-row items-center justify-between gap-3">
					<CardTitle>{t('Gambar Katalog')}</CardTitle>
					<Badge variant="secondary">{images.length}</Badge>
				</CardHeader>
				<CardContent class="grid gap-3">
					<div class="grid grid-cols-3 gap-2.5">
						{#each images as image}
							<div class="overflow-hidden rounded-lg border bg-muted/40">
								{#if image.imageUrl}
									<img src={image.imageUrl} alt={image.altText || data.catalog.title} class="h-24 w-full object-cover" />
								{:else}
									<div class="flex h-24 items-center justify-center text-xs font-bold text-muted-foreground">{t('Tidak ada gambar')}</div>
								{/if}
								<div class="flex items-center justify-between px-2 py-1">
									{#if image.isPrimary}
										<span class="text-[10px] font-bold text-primary">{t('Utama')}</span>
									{:else}
										<span class="text-[10px] text-muted-foreground">{image.altText || '—'}</span>
									{/if}
									<button class="text-[10px] font-bold text-destructive hover:underline" onclick={() => handleRemoveImage(image.id)}>{t('Hapus')}</button>
								</div>
							</div>
						{/each}
					</div>
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader>
				<CardTitle>{t('Tambah Gambar')}</CardTitle>
				<CardDescription>{t('Unggah file (max 25MB) atau tambahkan lewat URL.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
					{t('Unggah file')}
					<input type="file" accept="image/*,application/pdf" class="rounded-lg border bg-muted/30 px-3 py-2 text-sm" onchange={handleUploadImage} disabled={uploading} />
				</label>
				<div class="flex gap-2">
					<input
						type="text"
						placeholder={t('Atau URL gambar...')}
						class="h-10 flex-1 rounded-md border bg-background px-3 text-sm"
						bind:value={newImageUrl}
					/>
					<Button variant="outline" size="sm" onclick={handleAddImageUrl} disabled={!newImageUrl.trim()}>{t('Tambah URL')}</Button>
				</div>
				{#if uploading}
					<p class="text-xs font-semibold text-muted-foreground">{t('Mengunggah...')}</p>
				{/if}
			</CardContent>
		</Card>

		{#if variantTypes.length > 0}
			<Card>
				<CardHeader class="flex-row items-center justify-between gap-3">
					<CardTitle>{t('Varian')}</CardTitle>
					<Badge variant="secondary">{variantTypes.length}</Badge>
				</CardHeader>
				<CardContent class="grid gap-2.5">
					{#each variantTypes as vt}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<div class="flex items-center justify-between gap-2">
								<strong class="text-sm">{vt.typeName}</strong>
								<button class="text-xs font-bold text-destructive hover:underline" onclick={() => handleRemoveVariantType(vt.id)}>{t('Hapus tipe')}</button>
							</div>
							<div class="mt-1.5 flex flex-wrap gap-1.5">
								{#each vt.options ?? [] as option}
									<span class="inline-flex items-center gap-1 rounded-full border bg-background/60 px-2.5 py-1 text-xs font-bold">
										{option.optionName}
										<button class="text-muted-foreground hover:text-destructive" onclick={() => handleRemoveVariantOption(vt.id, option.id)}>✕</button>
									</span>
								{/each}
							</div>
							<div class="mt-2 flex gap-2">
								<input
									type="text"
									placeholder={`${t('Tambah opsi untuk')} ${vt.typeName}...`}
									class="h-9 flex-1 rounded-md border bg-background px-3 text-sm"
									value={newVariantOption[vt.id] ?? ''}
									oninput={(e) => (newVariantOption = { ...newVariantOption, [vt.id]: (e.currentTarget as HTMLInputElement).value })}
								/>
								<Button size="sm" variant="outline" onclick={() => handleAddVariantOption(vt.id)}>+</Button>
							</div>
						</div>
					{/each}
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader>
				<CardTitle>{t('Kelola Varian')}</CardTitle>
				<CardDescription>{t('Tambah tipe varian (warna, ukuran, rasa, dll) dan opsinya.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if variantError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{variantError}</p>
				{/if}
				<div class="flex gap-2">
					<input
						type="text"
						placeholder={t('Nama tipe varian (mis. Ukuran)')}
						class="h-10 flex-1 rounded-md border bg-background px-3 text-sm"
						bind:value={newVariantType}
					/>
					<Button variant="outline" size="sm" onclick={handleAddVariantType} disabled={!newVariantType.trim()}>{t('Tambah tipe')}</Button>
				</div>
			</CardContent>
		</Card>

		{#if aiDesc}
			<Card class="md:col-span-2">
				<CardHeader>
					<Badge variant="secondary">{t('Deskripsi AI')}</Badge>
					<CardTitle>{t('Deskripsi ekspor (AI)')}</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-3">
					<p class="rounded-lg border bg-muted/30 p-3.5 text-sm leading-relaxed">{aiDesc.export_description}</p>
					{#if aiDesc.technical_specs.length > 0}
						<div class="grid gap-2 sm:grid-cols-2">
							{#each aiDesc.technical_specs as spec}
								<div class="rounded-lg border bg-muted/30 p-3 text-xs">
									<span class="text-muted-foreground">{spec.label}</span><br /><b>{spec.value}</b>
								</div>
							{/each}
						</div>
					{/if}
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader><CardTitle>{t('Sorotan Pemasaran')}</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5">
				{#each data.catalog.highlights ?? [] as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>{t('Varian dan Incoterm')}</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5">
				{#each data.catalog.variants ?? [] as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
				{#each data.catalog.incoterms ?? [] as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row flex-wrap items-center justify-between gap-3">
				<div>
					<CardTitle>{t('Pemasaran AI')}</CardTitle>
					<CardDescription>{t('Pricing EXW/FOB/CIF & market intelligence untuk katalog ini.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2">
					<Button variant="outline" size="sm" onclick={handlePricing} disabled={aiLoading}>{t('Pricing')}</Button>
					<Button variant="outline" size="sm" onclick={handleMarketIntel} disabled={aiLoading}>{t('Market Intelligence')}</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if aiError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{aiError}</p>
				{/if}
				{#if aiLoading}
					<p class="text-xs font-semibold text-muted-foreground">{t('Menganalisis...')}</p>
				{/if}
				{#if pricing}
					<div class="grid gap-2 sm:grid-cols-3">
						<div class="rounded-lg border bg-muted/40 p-3 text-center">
							<span class="text-[10px] font-bold uppercase tracking-wide text-muted-foreground">EXW</span>
							<strong class="mt-1 block text-lg font-bold">${pricing.exwPriceUsd?.toFixed(2)}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-center">
							<span class="text-[10px] font-bold uppercase tracking-wide text-muted-foreground">FOB</span>
							<strong class="mt-1 block text-lg font-bold">${pricing.fobPriceUsd?.toFixed(2)}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-center">
							<span class="text-[10px] font-bold uppercase tracking-wide text-muted-foreground">CIF</span>
							<strong class="mt-1 block text-lg font-bold">${pricing.cifPriceUsd?.toFixed(2)}</strong>
						</div>
					</div>
					{#if pricing.pricingInsight}
						<p class="rounded-lg border bg-primary/10 p-3 text-xs leading-relaxed">{pricing.pricingInsight}</p>
					{/if}
				{/if}
				{#if marketIntel}
					<div class="grid gap-2">
						{#if (marketIntel.recommendedCountries ?? []).length > 0}
							{#each marketIntel.recommendedCountries as rec}
								<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-2.5 text-xs">
									<span><b>{rec.country}</b> ({rec.code})</span>
									<span class="text-muted-foreground">{rec.reason ?? ''}</span>
									<Badge variant={rec.score >= 80 ? 'default' : 'outline'}>{rec.score}</Badge>
								</div>
							{/each}
						{/if}
						{#if marketIntel.overallRecommendation}
							<p class="rounded-lg border bg-primary/10 p-3 text-xs leading-relaxed">{marketIntel.overallRecommendation}</p>
						{/if}
					</div>
				{/if}
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">{t('Lembar spesifikasi')}</Badge>
				<CardTitle>{t('Spesifikasi Teknis')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3">
				<div class="grid gap-3 sm:grid-cols-2">
					{#each data.catalog.specifications ?? [] as spec}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<span class="block text-xs font-bold uppercase tracking-wide text-muted-foreground">{spec.label}</span>
							<strong class="mt-1 block text-sm font-bold">{spec.value}</strong>
						</div>
					{/each}
				</div>
				{#if aiDesc}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('AI description siap digunakan. Simpan via edit catalog.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>
