<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { orders as seedOrders } from '$lib/data/trade';
	import { listOrders, createOrder } from '$lib/api/orders';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Draft', 'Confirmed', 'Document Prep', 'In Shipment'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let orders = createRemoteList(listOrders, seedOrders);
	$effect(() => {
		orders.load();
	});

	let filteredOrders = $derived(
		orders.items.filter((order) => {
			const matchesFilter = activeFilter === 'All' || order.status === activeFilter;
			const matchesQuery = [order.id, order.buyer, order.supplier, order.incoterm, order.quotationId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let totalValue = $derived(orders.items.reduce((sum, order) => sum + order.value, 0));
	let avgReadiness = $derived(Math.round(orders.items.reduce((sum, order) => sum + order.readiness, 0) / (orders.items.length || 1)));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			const seed = seedOrders[0];
			await createOrder({
				quotationId: seed?.quotationId ?? 'q-001',
				paymentTerms: seed?.paymentTerms ?? '30 days after B/L',
				deliveryWindow: seed?.deliveryWindow ?? '2-3 weeks'
			});
			created = true;
		} catch {
			error = t('Gagal membuat order.');
		} finally {
			creating = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredOrders ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredOrders?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Orders')} | MauEkspor</title>
</svelte:head>

<AppShell title="Orders" eyebrow={t('Accepted quotation to execution')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Sales order control')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Convert accepted quotations into executable export orders.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Track payment terms, delivery windows, order lines, document readiness, and shipment handoff from one operational view.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? t('Order draft created') : creating ? t('Creating...') : t('Create order')}</Button>
			<Badge variant="secondary">{t('Pipeline')} {currency.format(totalValue)}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if orders.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{orders.error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Order draft ready.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Order tersimpan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search order, buyer, supplier...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Orders')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{orders.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total value')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(totalValue)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Readiness')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{avgReadiness}%</strong></CardContent></Card>
	</div>

	{#if orders.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-7 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-1/2" />
					<Skeleton class="mt-2 h-4 w-2/3" />
					<Skeleton class="mt-3 h-2 w-full" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as order}
				<Card class="transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/orders/${order.id}`} class="grid h-full gap-3 p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(order.status))}>{order.status}</Badge>
							<strong class="text-2xl font-bold tracking-tight">{order.readiness}%</strong>
						</div>
						<h3 class="text-2xl font-bold tracking-tight">{order.id}</h3>
						<p class="text-sm text-muted-foreground">{order.supplier} to {order.buyer}</p>
						<Progress value={order.readiness} />
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Value')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(order.value)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{order.incoterm}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Payment')}<strong class="mt-1 block text-sm font-bold text-foreground">{order.paymentTerms}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Delivery')}<strong class="mt-1 block text-sm font-bold text-foreground">{order.deliveryWindow}</strong></div>
						</div>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No order matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredOrders?.length ?? 0} />

</AppShell>
