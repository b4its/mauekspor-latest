<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { generateReport, scheduleReport } from '$lib/api/reports';
	let { data } = $props();
	let generated = $state(false);
	let scheduled = $state(false);
	let busy = $state(false);
	let error = $state('');
	let displayStatus = $derived(scheduled ? 'Scheduled' : generated ? 'Ready' : data.report.status);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleGenerate() {
		error = '';
		busy = true;
		try {
			await generateReport(data.report.id);
			generated = true;
		} catch {
			error = 'Gagal generate laporan.';
		} finally {
			busy = false;
		}
	}

	async function handleSchedule() {
		error = '';
		busy = true;
		try {
			await scheduleReport(data.report.id);
			scheduled = true;
		} catch {
			error = 'Gagal menjadwalkan laporan.';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head>
	<title>{data.report.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.report.id} eyebrow="Report detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(displayStatus))} class="w-fit">{displayStatus}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{data.report.title}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.report.type} · {data.report.period} · {data.report.owner}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Sections<strong class="mt-1 block text-sm font-bold text-foreground">{data.report.sections.length}</strong></div>
		</CardContent>
	</Card>

	<div class="grid gap-4">
		<Card>
			<CardContent class="grid gap-4 p-5">
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div>
						<h3 class="text-xl font-bold tracking-tight">Report Builder</h3>
						<p class="mt-1 text-sm text-muted-foreground">Updated {data.report.updatedAt}. Generate a fresh report or schedule recurring delivery.</p>
					</div>
					<div class="flex flex-wrap gap-2">
						<Button variant="outline" onclick={handleSchedule} disabled={busy}>{scheduled ? 'Scheduled' : 'Schedule'}</Button>
						<Button onclick={handleGenerate} disabled={busy}>{generated ? 'Report generated' : busy ? 'Working...' : 'Generate now'}</Button>
					</div>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				<div class="flex flex-wrap gap-2">
					{#each data.report.sections as section}
						<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{section}</span>
					{/each}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-5">
				<Badge variant="secondary" class="w-fit">Insights</Badge>
				<CardTitle>Executive Notes</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 p-5">
				<div class="grid gap-3 sm:grid-cols-3">
					{#each data.report.insights as insight}
						<div class="rounded-lg border bg-muted/40 p-3 text-sm font-semibold text-muted-foreground">{insight}</div>
					{/each}
				</div>
				{#if generated}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Laporan dibuat di backend.</p>
				{/if}
				{#if scheduled}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Laporan dijadwalkan di backend.</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>