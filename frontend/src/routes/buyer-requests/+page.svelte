<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { buyerRequests as seedRequests, buyers, products } from '$lib/data/trade';
	import { listBuyerRequests } from '$lib/api/buyer-requests';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	const filters = ['All', 'New', 'Matched', 'Quoted', 'Closed'];
	let activeFilter = $state('All');
	let query = $state('');

	let requests = createRemoteList(listBuyerRequests, seedRequests);
	$effect(() => {
		requests.load();
	});

	let filteredRequests = $derived(
		requests.items.filter((request) => {
			const matchesFilter = activeFilter === 'All' || request.status === activeFilter;
			const matchesQuery = [request.subject, request.destination, request.quantity, request.productId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let newCount = $derived(requests.items.filter((request) => request.status === 'New').length);

	function resolveBuyer(id: string) {
		return buyers.find((buyer) => buyer.id === id)?.name ?? id;
	}

	function resolveProduct(id: string) {
		return products.find((product) => product.id === id)?.name ?? id;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Buyer Requests | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Requests" eyebrow="Inbound demand">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Inbound lead flow</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Act on buyer demand before it cools.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Review request subject, destination, quantity, deadline, and requirements, then match products or send a quotation.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/buyer-requests/create">Log buyer request</Button>
			<Badge variant="secondary">{newCount} new</Badge>
		</CardContent>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button
					variant={activeFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (activeFilter = filter)}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search subject, destination, product..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredRequests as request}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/buyer-requests/${request.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(request.status))}>{request.status}</Badge>
						<small class="text-xs font-semibold text-muted-foreground">{request.deadline}</small>
					</div>
					<h3 class="mt-4 text-2xl font-bold tracking-tight">{request.subject}</h3>
					<p class="mt-2 text-sm text-muted-foreground">{resolveBuyer(request.buyerId)} wants {request.quantity} for {request.destination}.</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Product <strong class="mt-1 block text-sm font-bold text-foreground">{resolveProduct(request.productId)}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Quantity <strong class="mt-1 block text-sm font-bold text-foreground">{request.quantity}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Destination <strong class="mt-1 block text-sm font-bold text-foreground">{request.destination}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Deadline <strong class="mt-1 block text-sm font-bold text-foreground">{request.deadline}</strong></div>
					</div>
					<div class="mt-4 flex flex-wrap gap-2">
						{#each request.requirements as requirement}
							<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{requirement}</span>
						{/each}
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No buyer request matched your filter.</div>
		{/each}
	</div>
</AppShell>