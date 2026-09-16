<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { getRegulationRecommendations } from '$lib/api/export-analysis';
	import type { RegulationRecommendations } from '$lib/api/export-analysis';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let regs = $state<RegulationRecommendations | null>(null);
	let language = $state<'id' | 'en'>('id');
	let loading = $state(false);
	let error = $state('');

	async function loadRegs(lang: 'id' | 'en') {
		loading = true;
		error = '';
		try {
			regs = (await getRegulationRecommendations(data.analysis.id, lang)).data;
		} catch {
			error = t('Gagal memuat panduan regulasi.');
		} finally {
			loading = false;
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		loadRegs(language);
	});
</script>

<svelte:head>
	<title>{t('Rekomendasi Regulasi')} | MauEkspor</title>
</svelte:head>

<AppShell title="Regulation Recommendations" eyebrow={data.analysis.destination}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<div class="flex flex-wrap items-center gap-2">
				<Badge variant={toneVariant(statusTone(data.analysis.status))}>{data.analysis.status}</Badge>
				{#if regs?.fromCache}
					<Badge variant="outline">{t('From cache')}</Badge>
				{/if}
			</div>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Panduan regulasi untuk')} {data.analysis.productName} {t('ke')} {data.analysis.destination}.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('10 bagian panduan kepatuhan (bahan terlarang, sertifikasi, pelabelan, bea cukai, pengujian, dll). Data dibuat dari snapshot produk & regulasi negara tujuan.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-5 flex flex-wrap items-center gap-3 p-0">
			<Button
				variant={language === 'id' ? 'default' : 'outline'}
				size="sm"
				onclick={() => (language = 'id')}
			>
				Bahasa Indonesia
			</Button>
			<Button
				variant={language === 'en' ? 'default' : 'outline'}
				size="sm"
				onclick={() => (language = 'en')}
			>
				English
			</Button>
			<Button variant="outline" size="sm" href={`/export-analysis/${data.analysis.id}`}>{t('Kembali ke analisis')}</Button>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if loading && !regs}
		<p class="text-sm font-semibold text-muted-foreground">{t('Memuat panduan regulasi...')}</p>
	{/if}

	{#if regs}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each regs.sections as section, index}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Badge variant="secondary">{t('Bagian')} {index + 1}</Badge>
					</div>
					<h3 class="mt-3 text-xl font-bold tracking-tight">{section.title}</h3>
					<p class="mt-2 text-sm leading-relaxed text-muted-foreground">{section.body}</p>
				</Card>
			{/each}
		</div>
	{/if}
</AppShell>
