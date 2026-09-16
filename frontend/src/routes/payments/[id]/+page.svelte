<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { markPaymentReceived, sendPaymentReminder } from '$lib/api/payments';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let received = $state(false);
	let reminded = $state(false);
	let error = $state('');
	let paidAmount = $derived(received ? data.payment.amount : data.payment.paid);
	let displayStatus = $derived(received ? 'Settled' : data.payment.status);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleReceived() {
		error = '';
		try {
			await markPaymentReceived(data.payment.id);
			received = true;
		} catch {
			error = 'Gagal menandai pembayaran diterima.';
		}
	}

	async function handleReminder() {
		error = '';
		try {
			await sendPaymentReminder(data.payment.id);
			reminded = true;
		} catch {
			error = 'Gagal mengirim pengingat.';
		}
	}
</script>

<svelte:head>
	<title>{data.payment.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.payment.id} eyebrow={t('Payment detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.payment.buyer}
				</CardTitle>
				<CardDescription class="mt-2">{data.payment.method} · Due {data.payment.dueDate}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Collected')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{Math.round((paidAmount / data.payment.amount) * 100)}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Settlement Control')}</CardTitle>
					<CardDescription>{t('Payment status is connected to order release, document handoff, and shipment readiness.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" onclick={handleReminder}>{reminded ? 'Reminder sent' : 'Send reminder'}</Button>
					<Button onclick={handleReceived}>{received ? 'Received' : 'Mark received'}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Total')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.payment.amount)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Paid')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(paidAmount)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Outstanding')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.payment.amount - paidAmount)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Risk')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.payment.risk}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Order')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.payment.orderId}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Buyer')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.payment.buyer}</strong>
				</div>
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-amber-500/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Payment milestones')}</Badge>
				<CardTitle>{t('Milestone Schedule')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.payment.milestones as milestone}
						<div class="grid gap-2 rounded-lg border bg-muted/30 p-3.5">
							<Badge variant={toneVariant(statusTone(received ? 'Done' : milestone.status))} class="w-fit">{received ? 'Done' : milestone.status}</Badge>
							<strong class="text-sm font-bold">{milestone.label}</strong>
							<small class="text-sm text-muted-foreground">{currency.format(milestone.amount)}</small>
						</div>
					{/each}
				</div>
				{#if data.order}
					<a href={`/orders/${data.order.id}`} class="mt-1 w-fit rounded-full border bg-muted/30 px-3.5 py-2 text-sm font-bold no-underline transition-colors hover:border-ring/40">
						Open linked order: {data.order.id}
					</a>
				{/if}
				{#if reminded}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Pengingat dikirim via backend.')}</p>
				{/if}
				{#if received}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Pembayaran ditandai diterima di backend.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>