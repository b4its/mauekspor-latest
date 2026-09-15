<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getHsCode } from '$lib/api/hs-codes';
	import type { HSCode } from '$lib/api/hs-codes';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let code = $derived(String(data.code ?? '').replace(/\./g, ''));
	let record = $state<HSCode | null>(null);
	let error = $state('');

	$effect(() => {
		error = '';
		record = null;
		getHsCode(code)
			.then((res) => (record = res.data))
			.catch(() => (error = t('Kode HS tidak ditemukan.')));
	});
</script>

<svelte:head>
	<title>{record?.hs_code ?? code} HS | MauEkspor</title>
</svelte:head>

<AppShell title="HS Code" eyebrow={t('Detail kode')}>
	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if !record && !error}
		<p class="rounded-lg border bg-muted/30 p-4 text-sm font-semibold text-muted-foreground">{t('Memuat detail HS code...')}</p>
	{/if}

	{#if record}
		<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
			<div class="flex min-w-0 flex-wrap items-end justify-between gap-6">
				<div class="min-w-0">
					<Badge variant="secondary">{t('HS code')}</Badge>
					<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl font-mono">
						{record.hs_code}
					</CardTitle>
					<CardDescription class="mt-2 max-w-2xl leading-relaxed">{record.description}</CardDescription>
				</div>
				<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
					<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Level')}</span>
					<strong class="mt-1 block text-4xl font-bold tracking-tight">L{record.level ?? '—'}</strong>
				</div>
			</div>
		</Card>

		<div class="grid gap-4 md:grid-cols-2">
			<Card>
				<CardHeader>
					<CardTitle>{t('Seksi')}</CardTitle>
					<CardDescription>{record.section_name ?? record.section ?? '—'}</CardDescription>
				</CardHeader>
				<CardContent>
					{#if record.parent}
						<a href={`/hs-codes/${record.parent}`} class="text-sm font-bold text-primary hover:underline">{t('Kode induk:')} {record.parent}</a>
					{/if}
				</CardContent>
			</Card>

			{#if (record.children ?? []).length > 0}
				<Card>
					<CardHeader class="flex-row items-center justify-between gap-3">
						<CardTitle>{t('Kode turunan')}</CardTitle>
						<Badge variant="outline">{(record.children ?? []).length}</Badge>
					</CardHeader>
					<CardContent class="grid gap-2">
						{#each record.children ?? [] as child}
							<a href={`/hs-codes/${child.hs_code}`} class="rounded-lg border bg-muted/30 p-3 transition-colors hover:border-ring/40 hover:bg-muted/50">
								<strong class="block text-sm font-mono font-bold">{child.hs_code}</strong>
								<span class="mt-0.5 block text-xs text-muted-foreground">{child.description}</span>
							</a>
						{/each}
					</CardContent>
				</Card>
			{/if}
		</div>

		<div class="mt-4 flex flex-wrap gap-2.5">
			<Button variant="outline" href="/hs-codes">{t('Kembali ke daftar')}</Button>
			<Button variant="outline" href="/export-analysis/create">{t('Analisis produk')}</Button>
		</div>
	{/if}
</AppShell>