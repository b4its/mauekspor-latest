<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { integrations } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listIntegrations, connectIntegration, syncIntegration } from '$lib/api/integrations';
	import { createRemoteList } from '$lib/api/remote-list.svelte';

	const filters = ['All', 'Logistics', 'Finance', 'Compliance', 'Commerce', 'AI'];
	let activeFilter = $state('All');
	let query = $state('');
	let synced = $state(false);
	let syncing = $state(false);
	let connected = $state(false);
	let error = $state('');
	let connectedId = $state('');

	let items = createRemoteList(listIntegrations, integrations);
	$effect(() => {
		items.load();
	});

	let filteredIntegrations = $derived(
		items.items.filter(
			(item) =>
				(activeFilter === 'All' || item.category === activeFilter) &&
				[item.name, item.category, item.status, item.description, ...item.scopes].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let connectedCount = $derived(items.items.filter((item) => item.status === 'Connected').length + (connected ? 1 : 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleSync() {
		error = '';
		syncing = true;
		try {
			const connected = items.items.find((item) => item.status === 'Connected') ?? items.items[0];
			if (connected) await syncIntegration(connected.id);
			synced = true;
		} catch {
			error = 'Gagal sinkronisasi.';
		} finally {
			syncing = false;
		}
	}

	async function handleConnect(itemId: string) {
		error = '';
		try {
			await connectIntegration(itemId);
			connectedId = itemId;
		} catch {
			error = 'Gagal menghubungkan integrasi.';
		}
	}
</script>

<svelte:head>
	<title>Integrations | MauEkspor</title>
</svelte:head>

<AppShell title="Integrations" eyebrow="Connected trade systems">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>Integration hub</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Connect MauEkspor to logistics, finance, compliance, commerce, and AI systems.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Keep rates, payment milestones, regulatory references, and AI workflows synchronized with the export operating system.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleSync} disabled={syncing}>{synced ? 'Synced' : syncing ? 'Syncing...' : 'Sync connected'}</Button>
			<Badge variant="secondary">Connected {connectedCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if synced}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Integrations synced.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Sinkronisasi dijalankan di backend.
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search integration, scope, status..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredIntegrations as item}
			<Card class="gap-4">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone((connected || connectedId === item.id) && item.status === 'Needs Auth' ? 'Connected' : item.status))}>{(connected || connectedId === item.id) && item.status === 'Needs Auth' ? 'Connected' : item.status}</Badge>
					<strong class="text-sm font-bold text-muted-foreground">{item.category}</strong>
				</div>
				<CardHeader class="p-0">
					<CardTitle class="text-xl font-bold tracking-tight">{item.name}</CardTitle>
					<CardDescription class="leading-relaxed">{item.description}</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-3 p-0">
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Last sync <strong class="mt-1 block text-sm font-bold text-foreground">{connected && item.status === 'Needs Auth' ? 'Just now' : item.lastSync}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Scopes <strong class="mt-1 block text-sm font-bold text-foreground">{item.scopes.length}</strong>
						</div>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each item.scopes as scope}
							<span class="rounded-full border bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">{scope}</span>
						{/each}
					</div>
				</CardContent>
				<Button variant="outline" onclick={() => handleConnect(item.id)}>{(connected || connectedId === item.id) && item.status === 'Needs Auth' ? 'Connected' : item.status === 'Connected' ? 'Reconnect' : 'Connect'}</Button>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No integration matched your search.</div>
		{/each}
	</div>
</AppShell>