<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { billingRecords } from '$lib/data/trade';
	import { currency, statusTone } from '$lib/utils/format';
	import { changePlan, downloadInvoice } from '$lib/api/billing';
	let changed = $state(false);
	let downloaded = $state(false);
	let busy = $state(false);
	let error = $state('');
	const billing = billingRecords[0];

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleChangePlan() {
		error = '';
		busy = true;
		try {
			await changePlan(billing.plan === 'Starter' ? 'Growth' : 'Starter');
			changed = true;
		} catch {
			error = 'Gagal mengubah plan.';
		} finally {
			busy = false;
		}
	}

	async function handleDownload() {
		error = '';
		busy = true;
		try {
			await downloadInvoice(billing.id);
			downloaded = true;
		} catch {
			error = 'Gagal mengunduh invoice.';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head>
	<title>Billing | MauEkspor</title>
</svelte:head>

<AppShell title="Billing" eyebrow="Subscription and usage">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(billing.status))}>{billing.status}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{billing.plan} plan for export operations.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Monitor subscription status, usage limits, invoice period, and upgrade needs for your MauEkspor workspace.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleChangePlan} disabled={busy}>{changed ? 'Plan updated' : 'Change plan'}</Button>
			<Button variant="outline" onclick={handleDownload} disabled={busy}>{downloaded ? 'Invoice ready' : 'Download invoice'}</Button>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if changed}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Plan change simulated.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Perubahan plan tersimpan di backend.
			</span>
		</div>
	{/if}
	{#if downloaded}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Invoice download prepared.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Invoice diekspor dari backend.
			</span>
		</div>
	{/if}

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Monthly amount</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(billing.amount)}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Period</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{billing.period}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Due date</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{billing.dueDate}</strong>
			</CardContent>
		</Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each billing.usage as item}
			<Card class="gap-4">
				<CardHeader class="flex-row items-center justify-between gap-3 space-y-0 p-0">
					<CardTitle class="text-base font-bold">{item.label}</CardTitle>
					<span class="text-sm text-muted-foreground">{item.used} / {item.limit}</span>
				</CardHeader>
				<CardContent class="p-0">
					<Progress value={Math.round((item.used / item.limit) * 100)} />
				</CardContent>
			</Card>
		{/each}
	</div>
</AppShell>