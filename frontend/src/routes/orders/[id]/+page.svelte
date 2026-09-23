<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { confirmOrder } from '$lib/api/orders';
	import { generateTradeDocument } from '$lib/api/documents';

	let { data } = $props();
	let confirmed = $state(false);
	let docsStarted = $state(false);
	let startingDocs = $state(false);
	let error = $state('');
	let displayStatus = $derived(docsStarted ? 'Document Prep' : confirmed ? 'Confirmed' : data.order.status);
	let displayReadiness = $derived(docsStarted ? Math.min(data.order.readiness + 12, 100) : confirmed ? Math.min(data.order.readiness + 7, 100) : data.order.readiness);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleDocs() {
		error = '';
		startingDocs = true;
		try {
			await generateTradeDocument({ projectId: data.project?.id ?? data.order.projectId, type: 'Commercial Invoice' });
			docsStarted = true;
		} catch {
			error = 'Gagal menyiapkan dokumen.';
		} finally {
			startingDocs = false;
		}
	}

	async function handleConfirm() {
		error = '';
		try {
			await confirmOrder(data.order.id);
			confirmed = true;
		} catch {
			error = 'Gagal mengonfirmasi order.';
		}
	}
</script>

<svelte:head>
	<title>{data.order.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.order.id} eyebrow="Sales order detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{data.order.supplier} to {data.order.buyer}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.project?.name ?? data.order.projectId}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap justify-end gap-3 p-0">
			<Card class="w-full max-w-56 text-right">
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Execution readiness</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{displayReadiness}%</strong>
				</CardContent>
			</Card>
		</CardContent>
	</Card>

	<div class="grid gap-4 lg:grid-cols-2">
		<Card class="lg:col-span-2">
			<CardContent class="grid gap-4 p-5">
				<div class="flex flex-wrap items-start justify-between gap-4">
					<div>
						<h3 class="text-2xl font-bold tracking-tight">Order Terms</h3>
						<p class="mt-1 text-sm text-muted-foreground">Order generated from quotation {data.order.quotationId}.</p>
					</div>
					<div class="flex flex-wrap gap-2">
						<Button variant="outline" disabled={confirmed} onclick={handleConfirm}>Confirm order</Button>
						<Button disabled={docsStarted || startingDocs} onclick={handleDocs}>{startingDocs ? 'Starting...' : 'Start document prep'}</Button>
					</div>
					{#if error}
						<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
				</div>
				<div class="grid gap-2 sm:grid-cols-3">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Value<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.order.value)}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Incoterm<strong class="mt-1 block text-sm font-bold text-foreground">{data.order.incoterm}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Payment<strong class="mt-1 block text-sm font-bold text-foreground">{data.order.paymentTerms}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Delivery<strong class="mt-1 block text-sm font-bold text-foreground">{data.order.deliveryWindow}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Currency<strong class="mt-1 block text-sm font-bold text-foreground">{data.order.currency}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Quotation<strong class="mt-1 block text-sm font-bold text-foreground">{data.order.quotationId}</strong></div>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardContent class="grid gap-4 p-5">
				<h3 class="text-xl font-bold tracking-tight">Order Lines</h3>
				<div class="grid gap-2">
					{#each data.order.lines as line}
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							<span class="block">{line.product}</span>
							<strong class="mt-1 block text-sm font-bold text-foreground">{line.quantity}</strong>
							<small class="mt-1 block">{currency.format(line.unitPrice)} each - {currency.format(line.total)}</small>
						</div>
					{/each}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardContent class="grid gap-4 p-5">
				<h3 class="text-xl font-bold tracking-tight">Execution Checklist</h3>
				<div class="grid gap-2">
					{#each data.order.checklist as item}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/40 p-3">
							<Badge variant={toneVariant(statusTone(item.status))}>{item.status}</Badge>
							<strong class="text-sm font-bold">{item.label}</strong>
						</div>
					{/each}
					{#if confirmed}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/40 p-3">
							<Badge>Done</Badge>
							<strong class="text-sm font-bold">Order confirmation demo completed</strong>
						</div>
					{/if}
					{#if docsStarted}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/40 p-3">
							<Badge variant="outline">Current</Badge>
							<strong class="text-sm font-bold">Document preparation started</strong>
						</div>
					{/if}
				</div>
			</CardContent>
		</Card>
	</div>
</AppShell>
