<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { recalculateCostingScenario, costingPdfUrl, getExchangeRate } from '$lib/api/costing';
	import type { ExchangeRate } from '$lib/api/costing';

	let { data } = $props();
	let recalculated = $state(false);
	let fxShock = $state(false);
	let error = $state('');
	let fx = $state<ExchangeRate | null>(null);

	type Line = { category: string; label: string; amount: number };
	type Container = { capacity_20ft?: number; capacity_40ft?: number; utilization_note?: string; tips?: string[] };

	let lines = $derived((data.scenario.lines ?? []) as Line[]);
	let container = $derived((data.scenario.container ?? null) as Container | null);

	let displayLanded = $derived(fxShock ? Math.round((data.scenario.landedCost ?? 0) * 1.035) : (data.scenario.landedCost ?? 0));
	let displayMargin = $derived(
		fxShock ? Math.max((data.scenario.margin ?? 0) - 3, 0) : recalculated ? (data.scenario.margin ?? 0) + 1 : (data.scenario.margin ?? 0)
	);
	let groupedLines = $derived(
		Object.entries(
			lines.reduce<Record<string, number>>((acc, line) => {
				acc[line.category] = (acc[line.category] ?? 0) + line.amount;
				return acc;
			}, {})
		)
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleRecalculate() {
		error = '';
		try {
			data.scenario = (await recalculateCostingScenario(data.scenario.id)).data;
			recalculated = true;
		} catch {
			error = 'Gagal menghitung ulang costing.';
		}
	}

	async function handleFx() {
		try {
			fx = (await getExchangeRate()).data;
		} catch {
			fx = null;
		}
	}
</script>

<svelte:head>
	<title>{data.scenario.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.scenario.id} eyebrow="Costing scenario detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.scenario.status))}>{data.scenario.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.scenario.title}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.scenario.projectId} - {data.product?.name ?? data.scenario.productId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Landed estimate</span>
				<strong class="mt-1 block text-3xl font-bold tracking-tight">{currency.format(displayLanded)}</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Scenario Summary</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl">Kalkulasi nyata EXW → FOB → CIF dengan kurs {data.scenario.exchangeRate ?? '—'} IDR/USD ({data.scenario.exchangeSource ?? ''}).</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/costing/${data.scenario.id}/edit`}>Edit scenario</Button>
					<Button variant="outline" onclick={handleFx}>{fx ? `FX ${fx.rate} (${fx.source})` : 'Show FX rate'}</Button>
					<Button variant="outline" onclick={() => (fxShock = !fxShock)}>{fxShock ? 'Remove FX shock' : 'Apply +3.5% FX shock'}</Button>
					<Button onclick={handleRecalculate}>{recalculated ? 'Recalculated' : 'Recalculate'}</Button>
					<Button variant="outline" href={costingPdfUrl(data.scenario.id)}>Download PDF</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Incoterm <strong class="mt-1 block text-sm font-bold text-foreground">{data.scenario.incoterm}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Destination <strong class="mt-1 block text-sm font-bold text-foreground">{data.scenario.destination}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					EXW <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.scenario.exwPrice)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					FOB <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.scenario.fobPrice)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					CIF <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.scenario.cifPrice)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Margin <strong class="mt-1 block text-sm font-bold text-foreground">{displayMargin}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Exchange rate <strong class="mt-1 block text-sm font-bold text-foreground">{data.scenario.exchangeRate ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Confidence <strong class="mt-1 block text-sm font-bold text-foreground">{data.scenario.confidence ?? '—'}%</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Cost Breakdown</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each lines as line}
					<div class="rounded-lg border bg-muted/30 p-3.5">
						<span class="block text-xs font-bold uppercase tracking-wide text-muted-foreground">{line.category}</span>
						<strong class="mt-1 block text-sm font-bold">{line.label}</strong>
						<small class="text-sm text-muted-foreground">{currency.format(line.amount)}</small>
					</div>
				{/each}
				{#if lines.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">Belum ada rincian biaya. Tambahkan COGS pada form edit.</p>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Category Totals</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each groupedLines as [category, amount]}
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{category}</span>
						<strong class="text-sm font-bold">{currency.format(amount)}</strong>
					</div>
				{/each}
			</CardContent>
		</Card>

		{#if container}
			<Card>
				<CardHeader><CardTitle>Container Capacity</CardTitle></CardHeader>
				<CardContent class="grid gap-2.5 text-sm">
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<span class="text-muted-foreground">20ft capacity</span>
						<strong>{container.capacity_20ft ?? '—'} unit</strong>
					</div>
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<span class="text-muted-foreground">40ft capacity</span>
						<strong>{container.capacity_40ft ?? '—'} unit</strong>
					</div>
					{#if container.utilization_note}
						<p class="rounded-lg border bg-muted/30 p-3 text-xs text-muted-foreground">{container.utilization_note}</p>
					{/if}
					{#if container.tips}
						{#each container.tips as tip}
							<p class="rounded-lg border bg-primary/10 p-3 text-xs">• {tip}</p>
						{/each}
					{/if}
				</CardContent>
			</Card>
		{/if}

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">Pricing guardrail</Badge>
				<CardTitle>Risks and assumptions</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3">
				<div class="flex flex-wrap gap-2.5">
					{#each (data.scenario.risks ?? []) as risk}
						<span class="rounded-full border bg-orange-500/10 px-3 py-1.5 text-xs font-bold text-orange-700">{risk}</span>
					{/each}
					{#if !(data.scenario.risks ?? []).length}
						<span class="text-sm font-semibold text-muted-foreground">Tidak ada risiko tercatat.</span>
					{/if}
				</div>
				{#if recalculated}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Skenario dihitung ulang di backend.</p>
				{/if}
				{#if fxShock}
					<p class="rounded-lg bg-orange-500/10 px-3 py-2 text-sm font-bold text-orange-700">FX shock applied. Landed estimate increased and margin compressed.</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>
