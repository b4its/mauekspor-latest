<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { acceptQuotation } from '$lib/api/quotations';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let revised = $state(false);
	let accepted = $state(false);
	let error = $state('');
	let displayStatus = $derived(accepted ? 'Accepted' : revised ? 'In Review' : data.quotation.status);
	let displayValue = $derived(revised ? Math.round(data.quotation.value * 1.025) : data.quotation.value);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleAccept() {
		error = '';
		try {
			await acceptQuotation(data.quotation.id);
			accepted = true;
		} catch {
			error = t('Gagal menerima quotation.');
		}
	}
</script>

<svelte:head>
	<title>{data.quotation.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.quotation.id} eyebrow={t('Quotation detail')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="flex-row flex-wrap items-end justify-between gap-3 p-0">
			<div>
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{data.quotation.incoterm}</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.quotation.supplier} to {data.quotation.buyer}</CardDescription>
			</div>
			<div class="text-right">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Quote value')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(displayValue)}</strong>
			</div>
		</CardHeader>
	</Card>

	<div class="grid gap-4 lg:grid-cols-2">
		<Card class="lg:col-span-2">
			<div class="flex flex-wrap items-start justify-between gap-4">
				<div>
					<h3 class="text-2xl font-bold tracking-tight">{t('Commercial Terms')}</h3>
					<p class="mt-1 leading-relaxed text-muted-foreground">{data.quotation.notes}</p>
				</div>
				<div class="actions flex flex-wrap gap-3">
					<Button variant="outline" onclick={() => (revised = true)}>{t('Revise +2.5%')}</Button>
					<Button disabled={accepted} onclick={handleAccept}>{accepted ? t('Diterima') : t('Terima kutipan')}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</div>
			<div class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Proyek')}<strong class="mt-1 block text-sm font-bold text-foreground">{data.project?.name ?? data.quotation.projectId}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('RFQ')}<strong class="mt-1 block text-sm font-bold text-foreground">{data.quotation.rfqId}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Mata uang')}<strong class="mt-1 block text-sm font-bold text-foreground">{data.quotation.currency}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Valid until')}<strong class="mt-1 block text-sm font-bold text-foreground">{data.quotation.validUntil}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Margin')}<strong class="mt-1 block text-sm font-bold text-foreground">{data.quotation.margin}%</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Status')}<strong class="mt-1 block text-sm font-bold text-foreground">{displayStatus}</strong></div>
			</div>
		</Card>

		<Card>
			<h3 class="text-2xl font-bold tracking-tight">{t('Cost Breakdown')}</h3>
			<div class="mt-4 grid gap-3">
				{#each data.quotation.costLines as line}
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/40 px-3 py-2.5">
						<span class="text-sm font-bold text-muted-foreground">{line.label}</span>
						<strong class="text-sm font-bold">{currency.format(line.amount)}</strong>
					</div>
				{/each}
			</div>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-secondary/30">
			<Badge variant="secondary">{t('Decision guardrail')}</Badge>
			<h3 class="mt-3 text-2xl font-bold tracking-tight">{t('Before acceptance')}</h3>
			<p class="mt-1 leading-relaxed text-muted-foreground">{t('Confirm Incoterm named place, rate validity, compliance blockers, and document readiness before converting to order.')}</p>
			{#if revised}<p class="mt-3 rounded-lg bg-emerald-500/10 px-3 py-2 font-bold text-emerald-600">{t('Revision diterapkan.')}</p>{/if}
			{#if accepted}<p class="mt-3 rounded-lg bg-emerald-500/10 px-3 py-2 font-bold text-emerald-600">{t('Kuotasi diterima di backend.')}</p>{/if}
		</Card>
	</div>
</AppShell>