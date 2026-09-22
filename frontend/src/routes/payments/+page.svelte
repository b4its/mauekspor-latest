<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { payments as seedPayments } from '$lib/data/trade';
	import { listPayments, sendPaymentReminder, createPayment } from '$lib/api/payments';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Pending', 'Deposit Paid', 'Due Soon', 'Overdue', 'Settled'];
	let activeFilter = $state('All');
	let query = $state('');
	let message = $state('');
	let busyId = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let fBuyer = $state('');
	let fAmount = $state('');
	let fCurrency = $state('USD');
	let fOrderId = $state('');
	let fDueDate = $state('');
	let fMethod = $state('Bank Transfer');
	let error = $state('');

	let payments = createRemoteList(listPayments, seedPayments);
	$effect(() => {
		payments.load();
	});

	let filteredPayments = $derived(
		payments.items.filter(
			(payment) =>
				(activeFilter === 'All' || payment.status === activeFilter) &&
				[payment.id, payment.orderId, payment.buyer, payment.method, payment.status]
					.join(' ')
					.toLowerCase()
					.includes(query.trim().toLowerCase())
		)
	);
	let receivable = $derived(payments.items.reduce((sum, payment) => sum + payment.amount - payment.paid, 0));
	let collected = $derived(payments.items.reduce((sum, payment) => sum + payment.paid, 0));
	let highRisk = $derived(payments.items.filter((payment) => payment.risk !== 'Low').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleReminder(paymentId: string, buyer: string) {
		error = '';
		busyId = paymentId;
		try {
			await sendPaymentReminder(paymentId);
			message = t('Pengingat dikirim ke ') + buyer + '.';
		} catch {
			error = t('Gagal mengirim pengingat pembayaran.');
		} finally {
			busyId = '';
		}
	}

	function openCreate() {
		fBuyer = '';
		fAmount = '';
		fCurrency = 'USD';
		fOrderId = '';
		fDueDate = '';
		fMethod = 'Bank Transfer';
		formError = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fBuyer.trim()) {
			formError = t('Buyer wajib diisi.');
			return;
		}
		saving = true;
		try {
			await createPayment({
				buyer: fBuyer.trim(),
				amount: Number(fAmount) || 0,
				currency: fCurrency,
				orderId: fOrderId.trim(),
				dueDate: fDueDate.trim(),
				method: fMethod.trim()
			});
			await payments.load();
			message = `Pembayaran untuk "${fBuyer.trim()}" dibuat.`;
			showForm = false;
		} catch {
			formError = t('Gagal membuat pembayaran.');
		} finally {
			saving = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredPayments ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredPayments?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Payments')} | MauEkspor</title>
</svelte:head>

<AppShell title="Payments" eyebrow={t('Export receivables and settlement')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Cashflow control')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Track deposits, LC milestones, and export receivables before shipment release.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Keep payment terms connected to orders, document release, and buyer risk so operations never ships without commercial control.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Tambah pembayaran')}</Button>
			<Badge variant="destructive">{t('Risk')} {highRisk}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Buyer')}
						<Input bind:value={fBuyer} placeholder="Hikari Foods Co." />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nilai')}
						<Input bind:value={fAmount} type="number" placeholder="0" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Mata uang')}
						<select bind:value={fCurrency} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['USD', 'IDR', 'EUR'] as cur}
								<option value={cur}>{cur}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Order ID')}
						<Input bind:value={fOrderId} placeholder="ORD-001" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Due date')}
						<Input bind:value={fDueDate} type="date" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Metode')}
						<Input bind:value={fMethod} placeholder="Bank Transfer" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleCreate}>{saving ? t('Menyimpan...') : t('Simpan pembayaran')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if payments.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{payments.error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search payment, buyer, order...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Collected')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(collected)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Receivable')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(receivable)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Tracked payments')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{payments.items.length}</strong></CardContent></Card>
	</div>

	{#if payments.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-16" />
						<Skeleton class="h-7 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-1/2" />
					<Skeleton class="mt-2 h-4 w-2/3" />
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
			{#each pagedItems as payment}
				<Card class="grid gap-0 transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/payments/${payment.id}`} class="grid h-full gap-3 p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(payment.status))}>{payment.status}</Badge>
							<strong class="text-2xl font-bold tracking-tight">{payment.amount ? Math.round((payment.paid / payment.amount) * 100) : 0}%</strong>
						</div>
						<h3 class="text-2xl font-bold tracking-tight">{payment.id}</h3>
						<p class="text-sm text-muted-foreground">{payment.buyer} · {payment.orderId}</p>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Total')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(payment.amount)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Paid')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(payment.paid)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Due')}<strong class="mt-1 block text-sm font-bold text-foreground">{payment.dueDate}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Method')}<strong class="mt-1 block text-sm font-bold text-foreground">{payment.method}</strong></div>
						</div>
					</a>
					<div class="flex flex-wrap gap-2 px-5 pb-5">
						<Button variant="outline" size="sm" disabled={busyId === payment.id} onclick={() => handleReminder(payment.id, payment.buyer)}>{t('Kirim pengingat')}</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No payment matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredPayments?.length ?? 0} />

</AppShell>
