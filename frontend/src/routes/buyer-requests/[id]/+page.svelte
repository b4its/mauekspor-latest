<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { matchBuyerRequest } from '$lib/api/buyer-requests';

	let { data } = $props();
	let matched = $state(false);
	let matching = $state(false);
	let error = $state('');
	let displayStatus = $derived(matched ? 'Matched' : data.request.status);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleMatch() {
		error = '';
		matching = true;
		try {
			await matchBuyerRequest(data.request.id);
			matched = true;
		} catch {
			error = 'Gagal mencocokkan permintaan.';
		} finally {
			matching = false;
		}
	}
</script>

<svelte:head>
	<title>{data.request.subject} | MauEkspor</title>
</svelte:head>

<AppShell title={data.request.id} eyebrow="Buyer request detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.request.subject}
				</CardTitle>
				<CardDescription class="mt-2">{data.buyer?.name ?? 'Unknown buyer'} wants {data.request.quantity} for {data.request.destination}.</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<Button variant="outline" href={`/buyer-requests/${data.request.id}/edit`}>Edit request</Button>
				<Button disabled={matched || matching} onclick={handleMatch}>{matched ? 'Matched to product' : matching ? 'Matching...' : 'Match to product'}</Button>
				<Button variant="outline" href="/quotations">Create quotation</Button>
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader><CardTitle>Request terms</CardTitle></CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Buyer <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer?.name ?? 'Unknown'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Product <strong class="mt-1 block text-sm font-bold text-foreground">{data.product?.name ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Quantity <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.quantity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Destination <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.destination}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Deadline <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.deadline}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Status <strong class="mt-1 block text-sm font-bold text-foreground">{displayStatus}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Requirements</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2">
				{#each data.request.requirements as requirement}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{requirement}</span>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">AI next step</Badge>
				<CardTitle>Recommended action</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					{matched
						? 'Matching selesai di backend.'
						: 'Match this request to an existing product to unlock focus on the evidence blockers: pricing, timing, and labeling.'}
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>