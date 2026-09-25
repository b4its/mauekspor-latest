<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { billingRecords as seedBillingRecords } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { changePlan, downloadInvoice, getBilling } from '$lib/api/billing';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	
	let changed = $state(false);
	let downloaded = $state(false);
	let busy = $state(false);
	let error = $state('');
	let message = $state('');
	let showPlanSelector = $state(false);
	let billings = createRemoteList(getBilling, seedBillingRecords);
	let billing = $derived(billings.items[0] ?? seedBillingRecords[0]);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		billings.load();
	});

	async function handleChangePlan(targetPlan: 'Starter' | 'Growth' | 'Enterprise') {
		error = '';
		busy = true;
		try {
			const res = await changePlan(targetPlan);
			if (res.data) {
				billings.upsert(res.data);
			} else {
				await billings.load();
			}
			changed = true;
			message = `Plan berhasil diubah ke ${targetPlan}.`;
			showPlanSelector = false;
		} catch {
			error = t('Gagal mengubah plan.');
		} finally {
			busy = false;
		}
	}

	async function handleDownload() {
		error = '';
		busy = true;
		try {
			const res = await downloadInvoice(billing.id);
			if (res.data) {
				billings.upsert(res.data);
			}
			downloaded = true;
			message = t('Invoice berhasil diunduh.');
		} catch {
			error = t('Gagal mengunduh invoice.');
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Billing')} | MauEkspor</title>
</svelte:head>

<AppShell title="Billing" eyebrow={t('Subscription and usage')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(billing.status))}>{billing.status}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{billing.plan} {t('plan for export operations.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Monitor subscription status, usage limits, invoice period, and upgrade needs for your MauEkspor workspace.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={() => (showPlanSelector = !showPlanSelector)} disabled={busy}>
				{showPlanSelector ? t('Batal') : changed ? t('Plan updated') : t('Change plan')}
			</Button>
			<Button variant="outline" onclick={handleDownload} disabled={busy}>
				{downloaded ? t('Invoice ready') : t('Download invoice')}
			</Button>
		</CardContent>

		{#if showPlanSelector}
			<div class="mt-6 grid gap-4 rounded-xl border bg-muted/20 p-4 sm:grid-cols-3">
				{#each [
					{ name: 'Starter' as const, price: '$99/mo', desc: '50 projects, 500 AI credits, 3 team seats' },
					{ name: 'Growth' as const, price: '$249/mo', desc: 'Unlimited projects, 2000 AI credits, 10 team seats' },
					{ name: 'Enterprise' as const, price: '$599/mo', desc: 'Dedicated infra, unlimited AI, custom forwarder rates' }
				] as plan}
					<div class="flex flex-col justify-between rounded-lg border bg-background p-4 shadow-sm">
						<div>
							<div class="flex items-center justify-between">
								<strong class="text-base font-bold">{plan.name}</strong>
								{#if billing.plan === plan.name}
									<Badge variant="default">{t('Aktif')}</Badge>
								{/if}
							</div>
							<span class="mt-1 block text-lg font-black">{plan.price}</span>
							<p class="mt-2 text-xs text-muted-foreground">{plan.desc}</p>
						</div>
						<Button
							size="sm"
							class="mt-4"
							variant={billing.plan === plan.name ? 'secondary' : 'default'}
							disabled={busy || billing.plan === plan.name}
							onclick={() => handleChangePlan(plan.name)}
						>
							{billing.plan === plan.name ? t('Plan aktif') : t('Pilih plan')}
						</Button>
					</div>
				{/each}
			</div>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if billings.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{billings.error}</p>
	{/if}

	{#if changed}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Plan change simulated.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Perubahan plan tersimpan di backend.')}</span>
		</div>
	{/if}
	{#if downloaded}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Invoice download prepared.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Invoice diekspor dari backend.')}</span>
		</div>
	{/if}

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Monthly amount')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(billing.amount)}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Period')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{billing.period}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Due date')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{billing.dueDate}</strong>
			</CardContent>
		</Card>
	</div>

	{#if billings.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<Skeleton class="h-4 w-24" />
					<Skeleton class="mt-2 h-7 w-1/2" />
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each billing.usage as item}
				<Card class="gap-4">
					<CardHeader class="flex-row items-center justify-between gap-3 space-y-0 p-0">
						<CardTitle class="text-base font-bold">{item.label}</CardTitle>
						<span class="text-sm text-muted-foreground">{item.used} / {item.limit}</span>
					</CardHeader>
					<CardContent class="p-0">
						<Progress value={item.limit ? Math.round((item.used / item.limit) * 100) : 0} />
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</AppShell>