<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { payments as seedPayments } from '$lib/data/trade';
	import { listPayments } from '$lib/api/payments';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';
	import { sendPaymentReminder } from '$lib/api/payments';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Pending', 'Deposit Paid', 'Due Soon', 'Overdue', 'Settled'];
	let activeFilter = $state('All');
	let query = $state('');
	let reminderSent = $state(false);
	let reminding = $state(false);
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

	async function handleReminders() {
		error = '';
		reminding = true;
		try {
			const duePayments = payments.items.filter((payment) => payment.status === 'Overdue' || payment.status === 'Due Soon');
			const target = duePayments[0] ?? payments.items.filter((payment) => payment.status === 'Pending')[0] ?? payments.items[0];
			if (target) await sendPaymentReminder(target.id);
			reminderSent = true;
		} catch {
			error = t('Gagal mengirim pengingat pembayaran.');
		} finally {
			reminding = false;
		}
	}
</script>

<svelte:head>
	<title>Payments | MauEkspor</title>
</svelte:head>

<AppShell title="Payments" eyebrow={t('Export receivables and settlement')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Cashflow control')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Track deposits, LC milestones, and export receivables before shipment release.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Keep payment terms connected to orders, document release, and buyer risk so operations never ships without commercial control.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleReminders} disabled={reminding}>{reminderSent ? t('Reminder sent') : reminding ? t('Sending...') : t('Send reminders')}</Button>
			<Badge variant="destructive">{t('Risk')} {highRisk}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if reminderSent}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Payment reminders sent.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Pengingat dikirim melalui backend.')}</span>
		</div>
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

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredPayments as payment}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/payments/${payment.id}`} class="grid h-full gap-3 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(payment.status))}>{payment.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{Math.round((payment.paid / payment.amount) * 100)}%</strong>
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
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No payment matched your search.')}</div>
		{/each}
	</div>
</AppShell>
