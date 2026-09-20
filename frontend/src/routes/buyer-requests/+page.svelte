<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { buyerRequests as seedRequests, buyers as seedBuyers, products as seedProducts } from '$lib/data/trade';
	import { listBuyerRequests, deleteBuyerRequest } from '$lib/api/buyer-requests';
	import { listBuyers } from '$lib/api/buyers';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'New', 'Matched', 'Quoted', 'Closed'];
	let activeFilter = $state('All');
	let query = $state('');

	let requests = createRemoteList(listBuyerRequests, seedRequests);
	let buyers = createRemoteList(listBuyers, seedBuyers);
	let products = createRemoteList(listProducts, seedProducts);
	$effect(() => {
		requests.load();
		buyers.load();
		products.load();
	});

	let deletingId = $state('');

	async function handleDelete(id: string) {
		if (!confirm(t('Hapus permintaan buyer ini?'))) return;
		deletingId = id;
		try {
			await deleteBuyerRequest(id);
			await requests.load();
		} catch {
			alert(t('Gagal menghapus permintaan buyer.'));
		} finally {
			deletingId = '';
		}
	}

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
		return buyers.items.find((buyer) => buyer.id === id)?.name ?? id;
	}

	function resolveProduct(id: string) {
		return products.items.find((product) => product.id === id)?.name ?? id;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
	let pagedItems = $derived(paginate(filteredRequests ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredRequests?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Permintaan Pembeli')} | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Requests" eyebrow={t('Inbound demand')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Inbound lead flow')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Act on buyer demand before it cools.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Review request subject, destination, quantity, deadline, and requirements, then match products or send a quotation.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/buyer-requests/create">{t('Log buyer request')}</Button>
			<Badge variant="secondary">{newCount} {t('new')}</Badge>
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
		<Input bind:value={query} type="search" placeholder={t('Search subject, destination, product...')} class="max-w-xs" />
	</div>

	{#if requests.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{requests.error}</p>
	{/if}

	{#if requests.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-16" />
						<Skeleton class="h-4 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-full" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<div class="mt-4 flex flex-wrap gap-2">
						<Skeleton class="h-5 w-20 rounded-full" />
						<Skeleton class="h-5 w-14 rounded-full" />
						<Skeleton class="h-5 w-16 rounded-full" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as request}
			<Card class="relative transition-all hover:border-ring/40 hover:shadow-md">
				<Button
					variant="outline"
					size="sm"
					class="absolute top-3 right-3 z-10 text-destructive hover:bg-destructive/10"
					disabled={deletingId === request.id}
					onclick={() => handleDelete(request.id)}
				>
					{deletingId === request.id ? t('Menghapus...') : t('Hapus')}
				</Button>
				<a href={`/buyer-requests/${request.id}`} class="block p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(request.status))}>{request.status}</Badge>
						<small class="text-xs font-semibold text-muted-foreground">{request.deadline}</small>
					</div>
					<h3 class="mt-4 text-2xl font-bold tracking-tight">{request.subject}</h3>
					<p class="mt-2 text-sm text-muted-foreground">{resolveBuyer(request.buyerId)} {t('wants')} {request.quantity} {t('for')} {request.destination}.</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Product')} <strong class="mt-1 block text-sm font-bold text-foreground">{resolveProduct(request.productId)}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Quantity')} <strong class="mt-1 block text-sm font-bold text-foreground">{request.quantity}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Destination')} <strong class="mt-1 block text-sm font-bold text-foreground">{request.destination}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Deadline')} <strong class="mt-1 block text-sm font-bold text-foreground">{request.deadline}</strong></div>
					</div>
					<div class="mt-4 flex flex-wrap gap-2">
						{#each request.requirements as requirement}
							<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{requirement}</span>
						{/each}
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No buyer request matched your filter.')}</div>
		{/each}
	</div>
{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredRequests?.length ?? 0} />

</AppShell>