<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { listHsCodes } from '$lib/api/hs-codes';
	import type { HSCode } from '$lib/api/hs-codes';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';

	let query = $state('');
	let codes = $state<HSCode[]>([]);
	let loading = $state(true);
	let error = $state('');
	let searchTimer: ReturnType<typeof setTimeout> | undefined;

	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
	let pagedItems = $derived(paginate(codes ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(codes?.length ?? 0, paginationPageSize));

	async function load(search = '') {
		error = '';
		loading = true;
		try {
			codes = (await listHsCodes(search, 200)).data;
		} catch {
			error = t('Gagal memuat daftar HS code.');
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		load();
	});

	function onSearch(value: string) {
		query = value;
		paginationPage = 1;
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => load(value.trim()), 300);
	}
</script>

<svelte:head>
	<title>{t('HS Code')} | MauEkspor</title>
</svelte:head>

<AppShell title="HS Code" eyebrow={t('Browsing kode HS')}>
	<Card class="panel-hero p-6 md:p-8">
		<Badge variant="secondary" class="w-fit">{t('Klasifikasi tarif')}</Badge>
		<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
			{t('Browsing kode HS untuk klasifikasi produk ekspor.')}
		</CardTitle>
		<CardDescription class="mt-2 max-w-2xl leading-relaxed">
			{t('Kode HS (Harmonized System) menentukan tarif bea masuk, persyaratan kepatuhan, dan statistik perdagangan. Cari dan telusuri hierarki kode.')}
		</CardDescription>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<Input
			type="search"
			placeholder={t('Cari kode atau deskripsi...')}
			value={query}
			oninput={(e) => onSearch((e.currentTarget as HTMLInputElement).value)}
			class="w-[min(390px,100%)]"
		/>
		<span class="text-xs font-semibold text-muted-foreground">{codes.length} {t('kode')}</span>
	</div>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if loading}
		<div class="grid gap-2.5">
			{#each Array(8) as _}
				<Skeleton class="h-16 w-full rounded-lg" />
			{/each}
		</div>
	{:else}
		<div class="grid gap-2.5">
			{#each pagedItems as code}
				<a href={`/hs-codes/${code.hs_code}`} class="rounded-lg border bg-muted/30 p-3.5 transition-colors hover:border-ring/40 hover:bg-muted/50">
					<div class="flex flex-wrap items-center justify-between gap-2">
						<strong class="text-sm font-bold font-mono">{code.hs_code}</strong>
						{#if code.level}<Badge variant="outline">L{code.level}</Badge>{/if}
					</div>
					<p class="mt-1 text-sm text-muted-foreground">{code.description}</p>
				</a>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada kode HS yang cocok.')}</div>
			{/each}
		</div>
		<div class="mt-4">
			<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={codes?.length ?? 0} />
		</div>
	{/if}
</AppShell>