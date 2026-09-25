<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { markPaymentReceived, sendPaymentReminder, updatePayment, deletePayment } from '$lib/api/payments';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let received = $state(false);
	let reminded = $state(false);
	let error = $state('');
	let message = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let editBuyer = $state('');
	let editAmount = $state('');
	let editStatus = $state('');
	let editMethod = $state('');
	let savedBuyer = $state('');
	let savedAmount = $state(0);
	let savedStatus = $state('');
	let savedMethod = $state('');
	let serverStatus = $state('');
	let localBuyer = $derived(savedBuyer || data.payment.buyer);
	let localAmount = $derived(savedAmount || data.payment.amount);
	let localMethod = $derived(savedMethod || data.payment.method);
	let paidAmount = $derived(received ? data.payment.amount : data.payment.paid);
	let displayStatus = $derived(serverStatus || (received ? 'Settled' : savedStatus || data.payment.status));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleReceived() {
		error = '';
		try {
			const res = await markPaymentReceived(data.payment.id);
			received = true;
			if (res.data) {
				savedStatus = res.data.status;
				serverStatus = res.data.status;
				savedAmount = res.data.amount;
			}
			message = t('Pembayaran ditandai diterima.');
		} catch {
			error = t('Gagal menandai pembayaran diterima.');
		}
	}

	async function handleReminder() {
		error = '';
		try {
			const res = await sendPaymentReminder(data.payment.id);
			reminded = true;
			if (res.data?.status) {
				savedStatus = res.data.status;
				serverStatus = res.data.status;
			}
			message = t('Pengingat pembayaran berhasil dikirim.');
		} catch {
			error = t('Gagal mengirim pengingat.');
		}
	}

	function openEdit() {
		editBuyer = localBuyer;
		editAmount = String(localAmount);
		editStatus = savedStatus || data.payment.status;
		editMethod = localMethod;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editBuyer.trim()) {
			error = t('Buyer wajib diisi.');
			return;
		}
		const amount = Number(editAmount);
		if (!editAmount.trim() || Number.isNaN(amount)) {
			error = t('Jumlah pembayaran tidak valid.');
			return;
		}
		saving = true;
		try {
			const res = await updatePayment(data.payment.id, {
				buyer: editBuyer.trim(),
				amount,
				status: editStatus.trim() as (typeof data.payment.status),
				method: editMethod.trim() as (typeof data.payment.method)
			});
			savedBuyer = res.data.buyer;
			savedAmount = res.data.amount;
			savedStatus = res.data.status;
			savedMethod = res.data.method;
			message = t('Pembayaran diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan pembayaran.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus pembayaran ini secara permanen?'))) return;
		deleting = true;
		try {
			await deletePayment(data.payment.id);
			goto('/payments');
		} catch {
			error = t('Gagal menghapus pembayaran.');
		} finally {
			deleting = false;
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
					{localBuyer}
				</CardTitle>
				<CardDescription class="mt-2">{localMethod} · Due {data.payment.dueDate}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Collected')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{Math.round((paidAmount / localAmount) * 100)}%</strong>
			</div>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Buyer')}
						<Input bind:value={editBuyer} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Jumlah')}
						<Input type="number" bind:value={editAmount} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Metode')}
						<Input bind:value={editMethod} />
					</label>
				</div>
				<Button class="w-fit" disabled={saving} onclick={handleSave}>{saving ? t('Menyimpan...') : t('Simpan perubahan')}</Button>
			</div>
		{/if}
		{#if message}
			<p class="mt-4 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
		{/if}
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Settlement Control')}</CardTitle>
					<CardDescription>{t('Payment status is connected to order release, document handoff, and shipment readiness.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" onclick={handleReminder}>{reminded ? t('Reminder sent') : t('Send reminder')}</Button>
					<Button onclick={handleReceived}>{received ? t('Received') : t('Mark received')}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Total')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(localAmount)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Paid')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(paidAmount)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Outstanding')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(localAmount - paidAmount)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Risk')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.payment.risk}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Order')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.payment.orderId}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Buyer')} <strong class="mt-1 block text-sm font-bold text-foreground">{localBuyer}</strong>
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