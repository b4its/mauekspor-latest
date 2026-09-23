<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { requestForwarderQuote } from '$lib/api/forwarders';

	let { data } = $props();
	let quoteRequested = $state(false);
	let requesting = $state(false);
	let error = $state('');

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleQuote() {
		error = '';
		requesting = true;
		try {
			await requestForwarderQuote(data.forwarder.id);
			quoteRequested = true;
		} catch {
			error = 'Gagal meminta kuotasi forwarder.';
		} finally {
			requesting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.forwarder.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.forwarder.id} eyebrow="Forwarder detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.forwarder.status))}>{data.forwarder.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.forwarder.name}
				</CardTitle>
				<CardDescription class="mt-2">{data.forwarder.coverage} - {data.forwarder.mode}</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<Button disabled={quoteRequested || requesting} onclick={handleQuote}>
					{quoteRequested ? 'Quote requested' : requesting ? 'Requesting...' : 'Request quote'}
				</Button>
				<Button variant="outline" href="/forwarders/catalogs">View catalogs</Button>
				<Button variant="outline" href="/shipments">Open shipments</Button>
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if quoteRequested}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Quote requested.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Permintaan kuotasi dikirim ke {data.forwarder.contact} di backend.
			</span>
		</div>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader><CardTitle>Freight profile</CardTitle></CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Coverage <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.coverage}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Mode <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.mode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					On-time rate <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.onTimeRate}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Quote speed <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.quoteSpeed}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Contact <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.contact}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Verified lanes <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.lanes.length}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Covered lanes</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each data.forwarder.lanes as lane}
					<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">Route</Badge><strong class="text-sm">{lane}</strong></div>
				{/each}
			</CardContent>
		</Card>
	</div>
</AppShell>