<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';

	let { data } = $props();
	let completed = $state<string[]>([]);

	function toggle(id: string) {
		completed = completed.includes(id)
			? completed.filter((item) => item !== id)
			: [...completed, id];
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Regulation Recommendations | MauEkspor</title>
</svelte:head>

<AppShell title="Regulation Recommendations" eyebrow={data.analysis.destination}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(data.analysis.status))}>{data.analysis.status}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Market gate checklist for {data.analysis.productName}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Each gate maps to a required evidence item for {data.analysis.destination}. Mark progress here.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" href={`/export-analysis/${data.analysis.id}`}>Back to analysis</Button>
		</CardContent>
	</Card>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each data.analysis.recommendations as recommendation, index}
			<Card class={`p-5 transition-all ${completed.includes(recommendation.title) ? 'ring-2 ring-blue-500/40' : ''}`}>
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(recommendation.status))}>{recommendation.status}</Badge>
					<small class="text-xs text-muted-foreground">{recommendation.type}</small>
				</div>
				<h3 class="mt-3 text-xl font-bold tracking-tight">{recommendation.title}</h3>
				<p class="mt-1 text-sm text-muted-foreground">{recommendation.detail}</p>
				<Button
					variant={completed.includes(recommendation.title) ? 'default' : 'ghost'}
					class="mt-4 w-fit"
					onclick={() => toggle(recommendation.title)}
				>
					{completed.includes(recommendation.title) ? 'Marked complete' : `Mark complete (${index + 1}/${data.analysis.recommendations.length})`}
				</Button>
			</Card>
		{/each}
	</div>
</AppShell>
