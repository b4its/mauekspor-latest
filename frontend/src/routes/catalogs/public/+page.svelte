<script lang="ts">
	import { onMount } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { listPublicCatalogs } from '$lib/api/catalogs';
	import { currency } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import type { Catalog } from '$lib/data/trade';

	let catalogs = $state<Catalog[]>([]);
	let loading = $state(true);
	let error = $state('');
	let query = $state('');
	let tag = $state('');

	async function load() {
		loading = true;
		error = '';
		try {
			const res = await listPublicCatalogs(query.trim(), tag.trim());
			catalogs = res.data ?? [];
		} catch {
			error = t('Gagal memuat katalog publik.');
		} finally {
			loading = false;
		}
	}

	onMount(load);
</script>

<svelte:head>
	<title>{t('Katalog Publik')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Katalog Publik')} eyebrow={t('Katalog terbuka untuk buyer & mitra')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Katalog publik')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Jelajahi katalog ekspor yang telah dipublikasikan.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Hanya katalog berstatus Published yang tampil di sini dan dapat dilihat tanpa login.')}
			</CardDescription>
		</CardHeader>
		<div class="mt-6 flex flex-wrap items-center gap-2">
			<Input bind:value={query} type="search" placeholder={t('Cari judul atau deskripsi...')} class="w-[min(320px,100%)]" />
			<Input bind:value={tag} placeholder={t('Filter tag...')} class="w-[min(200px,100%)]" />
			<Button variant="outline" onclick={load} disabled={loading}>{loading ? t('Memuat...') : t('Cari')}</Button>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<Skeleton class="h-6 w-2/3" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<Skeleton class="mt-4 h-16 w-full rounded-lg" />
				</Card>
			{/each}
		</div>
	{:else if catalogs.length === 0}
		<div class="rounded-xl border border-dashed p-8 text-center font-semibold text-muted-foreground">
			{t('Belum ada katalog publik.')}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each catalogs as catalog (catalog.id)}
				<Card class="flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md">
					<div class="grid gap-3 p-5">
						<div class="flex items-center justify-between gap-3">
							<Badge>{catalog.status}</Badge>
							<span class="text-xs font-semibold text-muted-foreground">{catalog.targetMarket}</span>
						</div>
						<a href={`/catalogs/public/${catalog.id}`} class="block no-underline hover:underline">
							<h3 class="text-xl font-bold tracking-tight text-foreground">{catalog.title}</h3>
						</a>
						<p class="line-clamp-2 text-sm text-muted-foreground">{catalog.description}</p>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('MOQ')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.moq}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Waktu tunggu')}<strong class="mt-1 block text-sm font-bold text-foreground">{catalog.leadTime}</strong></div>
						</div>
					</div>
					<div class="flex items-center justify-between border-t bg-muted/10 px-5 py-3">
						<span class="text-xs font-semibold text-muted-foreground">{catalog.priceRange || currency.format(0)}</span>
						<Button href={`/catalogs/public/${catalog.id}`} size="sm" variant="outline">{t('Lihat detail')}</Button>
					</div>
				</Card>
			{/each}
		</div>
	{/if}
</AppShell>
