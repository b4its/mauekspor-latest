<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getCountry } from '$lib/api/export-analysis';
	import type { Country } from '$lib/api/export-analysis';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let code = $derived((data.code ?? '').toUpperCase());
	let country = $state<Country | null>(null);
	let error = $state('');

	$effect(() => {
		error = '';
		country = null;
		getCountry(code)
			.then((res) => (country = res.data))
			.catch(() => (error = t('Negara tidak ditemukan.')));
	});

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{code} | MauEkspor</title>
</svelte:head>

<AppShell title={code} eyebrow={t('Regulasi negara tujuan')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex min-w-0 items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">{t('Negara tujuan')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{country?.country_name ?? code}
				</CardTitle>
				<CardDescription class="mt-2">
					{code} · {country?.region ?? '—'}
				</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Aturan')}</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{country?.regulations?.length ?? 0}</strong>
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if !country && !error}
		<p class="rounded-lg border bg-muted/30 p-4 text-sm font-semibold text-muted-foreground">{t('Memuat regulasi negara...')}</p>
	{/if}

	{#if country}
		{#if country.regulations && country.regulations.length > 0}
			<div class="grid gap-4 md:grid-cols-2">
				{#each Object.entries(country.regulations_by_category ?? {}) as [category, rules]}
					<Card>
						<CardHeader class="flex-row items-center justify-between gap-3">
							<CardTitle>{category}</CardTitle>
							<Badge variant="outline">{rules.length}</Badge>
						</CardHeader>
						<CardContent class="grid gap-3">
							{#each rules as rule}
								<div class="rounded-lg border bg-muted/30 p-3.5">
									{#if rule.forbidden_keywords}
										<p class="text-sm">
											<b>{t('Kata terlarang:')}</b>{' '}
											<span class="rounded-full bg-destructive/10 px-2 py-0.5 text-xs font-bold text-destructive">{rule.forbidden_keywords}</span>
										</p>
									{/if}
									{#if rule.required_specs}
										<p class="mt-1.5 text-sm"><b>{t('Spesifikasi wajib:')}</b> <span class="text-muted-foreground">{rule.required_specs}</span></p>
									{/if}
									{#if rule.description_rule}
										<p class="mt-1 text-sm"><b>{t('Aturan deskripsi:')}</b> <span class="text-muted-foreground">{rule.description_rule}</span></p>
									{/if}
								</div>
							{/each}
						</CardContent>
					</Card>
				{/each}
			</div>
		{:else}
			<p class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
				{t('Tidak ada regulasi tambahan untuk negara ini.')}
			</p>
		{/if}

		<div class="mt-4 flex flex-wrap gap-2.5">
			<Button variant="outline" href="/export-analysis/compare">{t('Bandingkan pasar')}</Button>
			<Button href="/export-analysis/create">{t('Buat analisis ekspor')}</Button>
		</div>
	{/if}
</AppShell>