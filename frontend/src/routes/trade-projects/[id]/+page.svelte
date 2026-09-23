<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { complianceTasks, documents, pipeline } from '$lib/data/trade';
	import { currency, statusTone } from '$lib/utils/format';

	let { data } = $props();
	let selectedTab = $state('Compliance');
	const tabs = ['Compliance', 'Quotation', 'Documents', 'Shipment'];

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.project.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.project.id} eyebrow={data.project.name}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.project.risk))}>{data.project.risk} risk</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.project.name}
				</CardTitle>
				<CardDescription class="mt-2">{data.project.product} for {data.project.buyer} in {data.project.country}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Quotation value</span>
				<strong class="mt-1 block text-3xl font-bold tracking-tight">{currency.format(data.project.value)}</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>Execution Pipeline</CardTitle>
				<Badge variant="secondary">Current stage: {data.project.stage}</Badge>
			</CardHeader>
			<CardContent class="grid gap-4 sm:grid-cols-3">
				{#each pipeline as item}
					<div class="rounded-lg border bg-muted/30 p-3.5">
						<div class="flex items-center justify-between gap-3">
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{item.label}</span>
							<strong class="text-sm font-bold">{item.value}%</strong>
						</div>
						<Progress value={item.value} class="mt-3" />
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Commercial Terms</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Incoterm</span>
					<strong class="text-sm font-bold">{data.project.incoterm}</strong>
				</div>
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Payment</span>
					<strong class="text-sm font-bold">{data.project.payment}</strong>
				</div>
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Port route</span>
					<strong class="text-sm font-bold">{data.project.port}</strong>
				</div>
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">ETA</span>
					<strong class="text-sm font-bold">{data.project.eta}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Classification</CardTitle></CardHeader>
			<CardContent>
				<div class="rounded-xl border bg-primary/10 p-4">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">Recommended HS</span>
					<strong class="mt-2 block text-4xl font-bold tracking-tight">{data.project.hsCode}</strong>
					<p class="mt-3 text-sm leading-relaxed text-muted-foreground">
						AI confidence 84%. Requires human confirmation before document generation.
					</p>
				</div>
			</CardContent>
		</Card>
	</div>

	<Card class="mt-4">
		<CardContent class="pt-(--card-spacing)">
			<div class="mb-4 flex flex-wrap gap-2.5">
				{#each tabs as tab}
					<Button variant={selectedTab === tab ? 'default' : 'outline'} onclick={() => (selectedTab = tab)}>{tab}</Button>
				{/each}
			</div>

			{#if selectedTab === 'Compliance'}
				<div class="grid gap-2.5">
					{#each complianceTasks as task}
						<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5">
							<div>
								<strong class="block text-sm font-bold">{task.name}</strong>
								<span class="mt-1 block text-xs font-semibold text-muted-foreground">{task.owner} - due {task.due}</span>
							</div>
							<Badge variant={toneVariant(statusTone(task.status))}>{task.status}</Badge>
						</div>
					{/each}
				</div>
			{:else if selectedTab === 'Documents'}
				<div class="grid gap-2.5">
					{#each documents as doc}
						<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5">
							<div class="w-full max-w-sm">
								<strong class="block text-sm font-bold">{doc.name}</strong>
								<Progress value={doc.score} class="mt-2.5" />
							</div>
							<Badge variant={toneVariant(statusTone(doc.status))}>{doc.status}</Badge>
						</div>
					{/each}
				</div>
			{:else if selectedTab === 'Quotation'}
				<div class="rounded-xl border bg-muted/30 p-5">
					<h3 class="text-2xl font-bold tracking-tight">{data.project.incoterm}</h3>
					<p class="mt-2 leading-relaxed text-muted-foreground">
						{currency.format(data.project.value)} valid until 12 Sep 2026. Includes export packing, origin handling, and base ocean freight assumptions.
					</p>
					<Button class="mt-4">Prepare revision</Button>
				</div>
			{:else}
				<div class="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-6">
					{#each ['Cargo Ready', 'Picked Up', 'Customs Submitted', 'Loaded', 'Departed', 'Arrived'] as milestone, index}
						<div
							class={index < 3
								? 'rounded-lg border border-primary/40 bg-primary/10 p-3.5 text-center text-sm font-bold text-primary'
								: 'rounded-lg border bg-muted/30 p-3.5 text-center text-sm font-bold'}
						>
							{milestone}
						</div>
					{/each}
				</div>
			{/if}
		</CardContent>
	</Card>
</AppShell>