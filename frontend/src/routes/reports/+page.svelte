<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { tradeReports } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listReports, generateReport } from '$lib/api/reports';
	import { createRemoteList } from '$lib/api/remote-list.svelte';

	const filters = ['All', 'Executive', 'Compliance', 'Financial', 'Shipment'];
	let activeFilter = $state('All');
	let query = $state('');
	let generated = $state(false);
	let generating = $state(false);
	let error = $state('');

	let reports = createRemoteList(listReports, tradeReports);
	$effect(() => {
		reports.load();
	});

	let filteredReports = $derived(
		reports.items.filter(
			(report) =>
				(activeFilter === 'All' || report.type === activeFilter) &&
				[report.title, report.type, report.status, report.owner].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let readyCount = $derived(reports.items.filter((report) => report.status === 'Ready').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleGenerate() {
		error = '';
		generating = true;
		try {
			const target = reports.items.find((report) => report.status !== 'Ready') ?? reports.items[0];
			if (target) await generateReport(target.id);
			generated = true;
		} catch {
			error = 'Gagal generate laporan.';
		} finally {
			generating = false;
		}
	}
</script>

<svelte:head>
	<title>Reports | MauEkspor</title>
</svelte:head>

<AppShell title="Reports" eyebrow="Export intelligence reporting">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Report builder</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Generate trade reports from live export workspace signals.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Package executive, compliance, financial, and shipment insights for management, buyers, finance, and operations.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleGenerate} disabled={generating}>{generated ? 'Report generated' : generating ? 'Generating...' : 'Generate report'}</Button>
			<Badge>Ready {readyCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if generated}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Report generated.</strong>
			<span class="block text-sm text-muted-foreground">Laporan dibuat di backend.</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search report, owner, type..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredReports as report}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/reports/${report.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(report.status))}>{report.status}</Badge>
						<strong class="text-sm font-bold tracking-tight">{report.type}</strong>
					</div>
					<h3 class="mt-3 text-2xl font-bold tracking-tight">{report.title}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{report.period} · {report.owner}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Sections<strong class="mt-1 block text-sm font-bold text-foreground">{report.sections.length}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Insights<strong class="mt-1 block text-sm font-bold text-foreground">{report.insights.length}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Updated<strong class="mt-1 block text-sm font-bold text-foreground">{report.updatedAt}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Report ID<strong class="mt-1 block text-sm font-bold text-foreground">{report.id}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No report matched your search.</div>
		{/each}
	</div>
</AppShell>
