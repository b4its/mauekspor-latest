<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { runRegulationCheck } from '$lib/api/export-analysis';

	let { data } = $props();
	let rechecked = $state(false);
	let rerunning = $state(false);
	let error = $state('');

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleRerun() {
		error = '';
		rerunning = true;
		try {
			await runRegulationCheck(data.analysis.id);
			rechecked = true;
		} catch {
			error = 'Gagal menjalankan ulang analisis.';
		} finally {
			rerunning = false;
		}
	}
</script>

<svelte:head>
	<title>{data.analysis.productName} Export Analysis | MauEkspor</title>
</svelte:head>

<AppShell title={data.analysis.id} eyebrow="Market analysis detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.analysis.status))}>{data.analysis.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.analysis.productName} to {data.analysis.destination}
				</CardTitle>
				<CardDescription class="mt-2">HS {data.analysis.hsCode} - classification confidence {data.analysis.confidence}%.</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Opportunity score</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{data.analysis.score}</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Market summary</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl leading-relaxed">{data.analysis.summary}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" disabled={rechecked || rerunning} onclick={handleRerun}>
						{rechecked ? 'Regulation recheck queued' : rerunning ? 'Running...' : 'Re-run analysis'}
					</Button>
					<Button href={`/export-analysis/${data.analysis.id}/regulation-recommendations`}>View recommendations</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					HS Code <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.hsCode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Market demand <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.marketDemand}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Confidence <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.confidence}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Duties <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.duties}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>Restrictions & evidence</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each data.analysis.restrictions as restriction}
					<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">Gate</Badge><strong class="text-sm">{restriction}</strong></div>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">AI note</Badge>
				<CardTitle>Next best action</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					Recommended: review each regulation recommendation, attach evidence, then move the pair to
					costing. The analysis job is wired to <code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">runRegulationCheck()</code>.
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>