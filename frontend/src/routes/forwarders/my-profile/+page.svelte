<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { forwarders } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { requestForwarderQuote } from '$lib/api/forwarders';

	let profile = $derived(forwarders[0]);
	let quoteReady = $state(false);
	let setting = $state(false);
	let error = $state('');

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleQuote() {
		error = '';
		setting = true;
		try {
			await requestForwarderQuote(profile.id);
			quoteReady = true;
		} catch {
			error = 'Gagal menandai siap kuotasi.';
		} finally {
			setting = false;
		}
	}
</script>

<svelte:head>
	<title>My Forwarder Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarder Profile" eyebrow="My freight partner identity">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(profile.status))}>{profile.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{profile.name}
				</CardTitle>
				<CardDescription class="mt-2">{profile.coverage} - {profile.mode}</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<Button variant="outline" href="/forwarders/profile">Edit profile</Button>
				<Button disabled={quoteReady || setting} onclick={handleQuote}>
					{quoteReady ? 'Ready to quote' : setting ? 'Setting...' : 'Set quote-ready'}
				</Button>
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader><CardTitle>Forwarder profile</CardTitle></CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Coverage <strong class="mt-1 block text-sm font-bold text-foreground">{profile.coverage}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Mode <strong class="mt-1 block text-sm font-bold text-foreground">{profile.mode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					On-time rate <strong class="mt-1 block text-sm font-bold text-foreground">{profile.onTimeRate}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Quote speed <strong class="mt-1 block text-sm font-bold text-foreground">{profile.quoteSpeed}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Contact <strong class="mt-1 block text-sm font-bold text-foreground">{profile.contact}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Lanes <strong class="mt-1 block text-sm font-bold text-foreground">{profile.lanes.length}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Covered lanes</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each profile.lanes as lane}
					<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">Route</Badge><strong class="text-sm">{lane}</strong></div>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">Market position</Badge>
				<CardTitle>What buyers see</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					Buyers see verified lanes, on-time performance, and quote speed when they evaluate freight
					partners for active shipments.
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>