<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { analyticsMetrics, buyers, complianceRequirements, payments, projects, shipments, suppliers } from '$lib/data/trade';
	import { currency } from '$lib/utils/format';
	import { refreshAnalytics } from '$lib/api/analytics';
	let refreshed = $state(false);
	let refreshing = $state(false);
	let error = $state('');
	let totalPipeline = $derived(projects.reduce((sum, project) => sum + project.value, 0));
	let receivable = $derived(payments.reduce((sum, payment) => sum + payment.amount - payment.paid, 0));
	let criticalCompliance = $derived(complianceRequirements.filter((item) => item.severity === 'Critical' && item.status !== 'Verified').length);
	let shipmentRisk = $derived(shipments.filter((shipment) => shipment.status === 'Exception').length);
	let qualifiedNetwork = $derived(buyers.filter((buyer) => ['Active', 'Negotiating'].includes(buyer.status)).length + suppliers.filter((supplier) => supplier.status === 'Verified').length);
	const lanes = [
		{ label: 'Japan coffee', readiness: 82, risk: 'Label proof blocked', href: '/trade-projects/EXP-2408-017' },
		{ label: 'EU rattan', readiness: 74, risk: 'SVLK and freight validity', href: '/trade-projects/EXP-2408-021' },
		{ label: 'Singapore snacks', readiness: 91, risk: 'Reorder timing', href: '/trade-projects/EXP-2408-026' }
	];

	async function handleRefresh() {
		error = '';
		refreshing = true;
		try {
			await refreshAnalytics();
			refreshed = true;
		} catch {
			error = 'Gagal me-refresh analytics.';
		} finally {
			refreshing = false;
		}
	}
</script>

<svelte:head>
	<title>Analytics | MauEkspor</title>
</svelte:head>

<AppShell title="Analytics" eyebrow="Executive trade intelligence">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Control tower</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">One executive view across pipeline, readiness, cash, risk, and delivery.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Aggregate signals from projects, buyers, suppliers, compliance, payments, documents, and shipments to prioritize the next trade actions.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleRefresh} disabled={refreshing}>{refreshed ? 'Analytics refreshed' : refreshing ? 'Refreshing...' : 'Refresh analytics'}</Button>
			<Badge>Network {qualifiedNetwork}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if refreshed}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Analytics refreshed.</strong>
			<span class="block text-sm text-muted-foreground">Data disegarkan dari backend.</span>
		</div>
	{/if}

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each analyticsMetrics as metric}
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{metric.label}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{metric.value}</strong>
					<small class="mt-1 block text-sm text-muted-foreground">{metric.change}</small>
				</CardContent>
			</Card>
		{/each}
	</div>

	<div class="grid gap-4 lg:grid-cols-2">
		<Card>
			<CardHeader class="p-5">
				<CardTitle>Commercial Snapshot</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-2 p-5">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Project pipeline<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(totalPipeline)}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Open receivable<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(receivable)}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Active buyers<strong class="mt-1 block text-sm font-bold text-foreground">{buyers.filter((buyer) => buyer.status === 'Active').length}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Verified suppliers<strong class="mt-1 block text-sm font-bold text-foreground">{suppliers.filter((supplier) => supplier.status === 'Verified').length}</strong></div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-5">
				<CardTitle>Risk Concentration</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-2 p-5">
				<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3">
					<strong class="text-3xl font-bold tracking-tight">{criticalCompliance}</strong>
					<span class="text-sm text-muted-foreground">critical compliance blockers</span>
				</div>
				<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3">
					<strong class="text-3xl font-bold tracking-tight">{shipmentRisk}</strong>
					<span class="text-sm text-muted-foreground">shipment exception</span>
				</div>
				<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3">
					<strong class="text-3xl font-bold tracking-tight">{payments.filter((payment) => payment.risk === 'High').length}</strong>
					<span class="text-sm text-muted-foreground">high-risk payment</span>
				</div>
			</CardContent>
		</Card>
	</div>

	<Card>
		<CardHeader class="p-5">
			<Badge variant="outline" class="w-fit">Trade lanes</Badge>
			<CardTitle>Readiness by Export Lane</CardTitle>
		</CardHeader>
		<CardContent class="grid gap-3 p-5 md:grid-cols-3">
			{#each lanes as lane}
				<a href={lane.href} class="grid gap-2 rounded-lg border bg-muted/30 p-3 no-underline transition-colors hover:border-ring/40">
					<div class="flex items-center justify-between gap-3">
						<strong class="text-sm font-bold">{lane.label}</strong>
						<span class="text-xs font-semibold text-muted-foreground">{lane.readiness}% ready</span>
					</div>
					<Progress value={lane.readiness} />
					<small class="text-xs text-muted-foreground">{lane.risk}</small>
				</a>
			{/each}
		</CardContent>
	</Card>
</AppShell>
