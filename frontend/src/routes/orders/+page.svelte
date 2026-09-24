<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { orders as seedOrders } from '$lib/data/trade';
	import { listOrders, createOrder, confirmOrder, deleteOrder } from '$lib/api/orders';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Draft', 'Confirmed', 'Document Prep', 'In Shipment'];
	let activeFilter = $state('All');
	let query = $state('');
	let error = $state('');
	let message = $state('');
	let showForm = $state(false);
	let creating = $state(false);
	let formError = $state('');
	let fBuyer = $state('');
	let fSupplier = $state('');
	let fQuotation = $state('');
	let fValue = $state('');
	let fIncoterm = $state('FOB');
	let fCurrency = $state('USD');
	let fPaymentTerms = $state('30 days after B/L');
	let fDeliveryWindow = $state('2-3 weeks');

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

	let busyId = $state('');

	async function handleConfirm(order: { id: string }) {
		error = '';
		busyId = order.id;
		try {
			const res = await confirmOrder(order.id);
			if (res.data) {
				orders.upsert(res.data);
			} else {
				await orders.load();
			}
			message = `Order ${order.id} dikonfirmasi.`;
		} catch {
			error = t('Gagal mengonfirmasi order.');
		} finally {
			busyId = '';
		}
	}

	async function handleDelete(order: { id: string }) {
		if (!confirm(`Hapus order ${order.id}?`)) return;
		error = '';
		busyId = order.id;
		try {
			await deleteOrder(order.id);
			orders.remove(order.id);
			message = `Order ${order.id} dihapus.`;
		} catch {
			error = t('Gagal menghapus order.');
		} finally {
			busyId = '';
		}
	}

	function openCreate() {
		formError = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fBuyer.trim()) {
			formError = t('Buyer wajib diisi.');
			return;
		}
		creating = true;
		try {
			const res = await createOrder({
				buyer: fBuyer.trim(),
				supplier: fSupplier.trim(),
				quotationId: fQuotation.trim(),
				value: Number(fValue) || 0,
				incoterm: fIncoterm,
				currency: fCurrency,
				paymentTerms: fPaymentTerms.trim(),
				deliveryWindow: fDeliveryWindow.trim()
			});
			if (res.data) {
				orders.upsert(res.data);
			} else {
				await orders.load();
			}
			message = `Order "${res.data.id}" dibuat.`;
			showForm = false;
			fBuyer = '';
			fSupplier = '';
			fQuotation = '';
			fValue = '';
		} catch {
			formError = t('Gagal membuat order.');
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
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create order')}</Button>
			<Badge variant="secondary">{t('Pipeline')} {currency.format(totalValue)}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Buyer')}
						<Input bind:value={fBuyer} placeholder="Hikari Foods Co." />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Supplier')}
						<Input bind:value={fSupplier} placeholder="PT Kopi Gayo Nusantara" />
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Quotation ID')}
						<Input bind:value={fQuotation} placeholder="Q-001" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nilai')}
						<Input bind:value={fValue} type="number" placeholder="0" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Incoterm')}
						<select bind:value={fIncoterm} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['FOB', 'CIF', 'EXW', 'DAP'] as term}
								<option value={term}>{term}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Mata uang')}
						<select bind:value={fCurrency} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['USD', 'IDR', 'EUR'] as cur}
								<option value={cur}>{cur}</option>
							{/each}
						</select>
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Syarat pembayaran')}
						<Input bind:value={fPaymentTerms} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Jendela pengiriman')}
						<Input bind:value={fDeliveryWindow} />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : t('Simpan order')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if orders.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{orders.error}</p>
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
				<Card class="flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md">
					<div class="grid gap-3 p-5">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(order.status))}>{order.status}</Badge>
							<strong class="text-2xl font-bold tracking-tight">{order.readiness}%</strong>
						</div>
						<a href={`/orders/${order.id}`} class="block no-underline hover:underline">
							<h3 class="text-2xl font-bold tracking-tight text-foreground">{order.id}</h3>
							<p class="text-sm text-muted-foreground">{order.supplier} to {order.buyer}</p>
						</a>
						<Progress value={order.readiness} />
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Value')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(order.value)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{order.incoterm}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Payment')}<strong class="mt-1 block text-sm font-bold text-foreground">{order.paymentTerms}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Delivery')}<strong class="mt-1 block text-sm font-bold text-foreground">{order.deliveryWindow}</strong></div>
						</div>
					</div>
					<div class="flex items-center justify-between border-t bg-muted/10 px-5 py-3">
						<a href={`/orders/${order.id}`} class="text-xs font-semibold text-primary hover:underline">
							{t('Lihat detail')} &rarr;
						</a>
						<div class="flex items-center gap-1.5">
							{#if order.status !== 'Confirmed'}
								<Button
									variant="outline"
									size="sm"
									class="h-7 text-xs"
									disabled={busyId === order.id}
									onclick={() => handleConfirm(order)}
								>
									{busyId === order.id ? '...' : t('Konfirmasi')}
								</Button>
							{/if}
							<Button
								variant="ghost"
								size="sm"
								class="h-7 text-xs text-destructive hover:bg-destructive/10"
								disabled={busyId === order.id}
								onclick={() => handleDelete(order)}
							>
								{t('Hapus')}
							</Button>
						</div>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No order matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredOrders?.length ?? 0} />

</AppShell>
