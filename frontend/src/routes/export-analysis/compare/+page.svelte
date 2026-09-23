<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '$lib/components/ui/table/index.js';
	import { exportAnalyses as seedAnalyses } from '$lib/data/trade';
	import { listExportAnalyses } from '$lib/api/export-analysis';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	let analyses = createRemoteList(listExportAnalyses, seedAnalyses);
	$effect(() => {
		analyses.load();
	});

	let columns = $derived(analyses.items.map((analysis) => ({ ...analysis, recommendations: [...analysis.recommendations] })));

	let rows = $derived([
		{ label: 'Product', get: (a: (typeof columns)[number]) => a.productName },
		{ label: 'Status', get: (a: (typeof columns)[number]) => a.status, badge: true },
		{ label: 'HS Code', get: (a: (typeof columns)[number]) => a.hsCode },
		{ label: 'Score', get: (a: (typeof columns)[number]) => String(a.score) },
		{ label: 'Confidence', get: (a: (typeof columns)[number]) => `${a.confidence}%` },
		{ label: 'Market demand', get: (a: (typeof columns)[number]) => a.marketDemand },
		{ label: 'Duties', get: (a: (typeof columns)[number]) => a.duties }
	]);

	let style = $derived(`--cols:${columns.length}`);
</script>

<svelte:head>
	<title>Compare Markets | MauEkspor</title>
</svelte:head>

<AppShell title="Compare Markets" eyebrow="Side-by-side analysis">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Decision support</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Compare markets to pick your first target.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Score, confidence, demand, duties, and top restrictions side by side for each analyzed market.</CardDescription>
		</CardHeader>
	</Card>

	<Card class="overflow-x-auto p-0">
		<Table>
			<TableHeader>
				<TableRow>
					<TableHead>Metric</TableHead>
					{#each columns as analysis}
						<TableHead class="text-center">{analysis.destination}</TableHead>
					{/each}
				</TableRow>
			</TableHeader>
			<TableBody>
				{#each rows as row}
					<TableRow>
						<TableCell class="font-semibold text-muted-foreground">{row.label}</TableCell>
						{#each columns as analysis}
							<TableCell class="text-center">
								{#if row.badge}
									<Badge>{row.get(analysis)}</Badge>
								{:else}
									{row.get(analysis)}
								{/if}
							</TableCell>
						{/each}
					</TableRow>
				{/each}
			</TableBody>
		</Table>
	</Card>
</AppShell>
