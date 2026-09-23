<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { supportTickets as seedTickets } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { listSupportTickets } from '$lib/api/support';
	import { statusTone } from '$lib/utils/format';
	import { createSupportTicket, resolveSupportTicket } from '$lib/api/support';

	const filters = ['All', 'Bug', 'Question', 'Billing', 'Integration', 'Operations'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let resolved = $state(false);
	let error = $state('');
	let resolvedId = $state('');
	let creating = $state(false);
	let tickets = createRemoteList(listSupportTickets, seedTickets);
	let filteredTickets = $derived(
		tickets.items.filter(
			(ticket) =>
				(activeFilter === 'All' || ticket.category === activeFilter) &&
				[ticket.subject, ticket.category, ticket.status, ticket.priority, ticket.owner, ticket.description].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let openCount = $derived(tickets.items.filter((ticket) => ticket.status !== 'Resolved').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		tickets.load();
	});

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			await createSupportTicket({
				subject: 'Need help with export workflow',
				category: 'Question',
				description: 'How do I start a new trade project?'
			});
			created = true;
		} catch {
			error = 'Gagal membuat tiket.';
		} finally {
			creating = false;
		}
	}

	async function handleResolve(ticketId: string) {
		error = '';
		try {
			await resolveSupportTicket(ticketId);
			resolvedId = ticketId;
		} catch {
			error = 'Gagal menyelesaikan tiket.';
		}
	}
</script>

<svelte:head>
	<title>Support | MauEkspor</title>
</svelte:head>

<AppShell title="Support" eyebrow="Help desk and product support">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Support desk</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Get help with export workflows, integrations, billing, and platform issues.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Track support tickets from creation to resolution while keeping each request tied to a clear category and owner.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? 'Ticket created' : creating ? 'Creating...' : 'Create ticket'}</Button>
			<Badge variant="outline">Open {openCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Support ticket created.</strong>
			<span class="block text-sm text-muted-foreground">Tiket tersimpan di backend.</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search ticket, owner, issue..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-3">
		{#each filteredTickets as ticket}
			<Card class="flex flex-col items-stretch justify-between gap-4 p-5 md:flex-row md:items-center">
				<div>
					<Badge variant={toneVariant(statusTone(resolved || resolvedId === ticket.id ? 'Resolved' : ticket.status))}>{resolved || resolvedId === ticket.id ? 'Resolved' : ticket.status}</Badge>
					<h3 class="mt-3 text-2xl font-bold tracking-tight">{ticket.subject}</h3>
					<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{ticket.description}</p>
					<small class="mt-2 block text-sm text-muted-foreground">{ticket.category} · {ticket.owner} · {ticket.createdAt}</small>
				</div>
				<aside class="grid justify-items-start gap-2 whitespace-nowrap md:justify-items-end">
					<strong class="text-xl font-bold tracking-tight">{ticket.priority}</strong>
					<Button variant="outline" size="sm" onclick={() => handleResolve(ticket.id)}>{resolvedId === ticket.id ? 'Resolved' : 'Resolve'}</Button>
				</aside>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No support ticket matched your search.</div>
		{/each}
	</div>
</AppShell>
