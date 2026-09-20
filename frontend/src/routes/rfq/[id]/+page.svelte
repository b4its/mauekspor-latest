<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { createQuotation } from '$lib/api/quotations';
	import { shortlistRFQMatch } from '$lib/api/rfq';

	let { data } = $props();
	let shortlisted = $state('');
	let shortlisting = $state('');
	let quoteCreated = $state(false);
	let creatingQuote = $state(false);
	let error = $state('');

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleShortlist(supplier: string) {
		error = '';
		shortlisting = supplier;
		try {
			const res = await shortlistRFQMatch(data.rfq.id, supplier);
			data.rfq = res.data;
			shortlisted = supplier;
		} catch {
			error = t('Gagal menambahkan supplier ke shortlist.');
		} finally {
			shortlisting = '';
		}
	}

	async function handleCreateQuote() {
		error = '';
		creatingQuote = true;
		try {
			await createQuotation({
				rfqId: data.rfq.id,
				incoterm: data.rfq.incoterm,
				value: 42800,
				currency: 'IDR',
				validUntil: '2026-09-30'
			});
			quoteCreated = true;
		} catch {
			error = 'Gagal membuat quotation draft.';
		} finally {
			creatingQuote = false;
		}
	}
</script>

<svelte:head>
	<title>{data.rfq.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.rfq.id} eyebrow="RFQ detail">
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.rfq.status))}>{data.rfq.status}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.rfq.product}
				</CardTitle>
				<CardDescription class="mt-2">{data.rfq.buyer} - {data.rfq.destination}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Best match')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{data.rfq.matchScore}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="p-0"><CardTitle>{t('RFQ Requirements')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Proyek')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.project?.name ?? data.rfq.projectId}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Quantity')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.rfq.quantity}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Incoterm')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.rfq.incoterm}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Deadline')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.rfq.deadline}</strong>
					</div>
				</div>
				<div class="flex flex-wrap gap-2.5">
					{#each data.rfq.requirements as requirement}
						<Badge variant="outline">{requirement}</Badge>
					{/each}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Supplier Matches')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 pt-4">
				{#each data.rfq.matches as match}
					<div class="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<div>
							<strong class="block text-sm font-bold">{match.supplier}</strong>
							<p class="my-1 text-sm text-muted-foreground">{match.catalog}</p>
							<small class="text-xs text-muted-foreground">{match.reason}</small>
						</div>
						<div class="grid justify-items-end gap-2">
							<b class="text-2xl font-bold tracking-tight">{match.score}%</b>
							<Button variant="outline" size="sm" disabled={shortlisting !== ''} onclick={() => handleShortlist(match.supplier)}>{shortlisting === match.supplier ? t('Shortlisting...') : t('Shortlist')}</Button>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Commercial action')}</Badge>
				<CardTitle>{t('Create quotation')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<p class="text-muted-foreground">{shortlisted ? t('{} is shortlisted for quotation.').replace('{}', shortlisted) : t('Shortlist a supplier match before creating quotation.')}</p>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				{#if quoteCreated}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Quotation draft tersimpan di backend.')}</p>
				{/if}
				<Button class="w-fit" disabled={!shortlisted || quoteCreated} onclick={handleCreateQuote}>{quoteCreated ? 'Draft created' : creatingQuote ? 'Creating...' : 'Create quotation draft'}</Button>
			</CardContent>
		</Card>
	</div>
</AppShell>