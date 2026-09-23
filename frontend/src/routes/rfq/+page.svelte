<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { rfqs as seedRFQs } from '$lib/data/trade';
	import { listRFQs, createRFQ } from '$lib/api/rfq';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Matching', 'Quoted', 'Accepted'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let rfqs = createRemoteList(listRFQs, seedRFQs);
	$effect(() => {
		rfqs.load();
	});

	let filteredRFQs = $derived(
		rfqs.items.filter((rfq) => {
			const matchesFilter = activeFilter === 'All' || rfq.status === activeFilter;
			const matchesQuery = [rfq.id, rfq.buyer, rfq.product, rfq.destination, rfq.incoterm]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let averageMatch = $derived(Math.round(rfqs.items.reduce((sum, rfq) => sum + rfq.matchScore, 0) / (rfqs.items.length || 1)));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			const seed = seedRFQs[0];
			await createRFQ({
				buyer: seed?.buyer ?? 'Hikari Foods Co.',
				product: seed?.product ?? 'Gayo Arabica Coffee Beans',
				destination: seed?.destination ?? 'Tokyo, Japan',
				quantity: seed?.quantity ?? '500 kg',
				incoterm: seed?.incoterm ?? 'FOB Tanjung Priok',
				deadline: seed?.deadline ?? '2026-09-30'
			});
			created = true;
		} catch {
			error = t('Gagal membuat RFQ.');
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>{t('RFQ')} | MauEkspor</title>
</svelte:head>

<AppShell title="RFQ" eyebrow={t('Buyer demand workspace')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Smart matching')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Match buyer requirements with verified exporter capabilities.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Manage RFQs, destination terms, required certificates, deadlines, and transparent supplier matching explanations.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? t('RFQ draft created') : creating ? t('Creating...') : t('Create RFQ')}</Button>
			<Badge variant="secondary">{t('Avg match')} {averageMatch}%</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('RFQ draft ready.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('RFQ tersimpan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search buyer, product, destination...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredRFQs as rfq}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/rfq/${rfq.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(rfq.status))}>{rfq.status}</Badge>
						<strong class="text-3xl font-bold tracking-tight">{rfq.matchScore}%</strong>
					</div>
					<h3 class="mt-4 text-xl font-bold tracking-tight">{rfq.product}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{rfq.buyer} - {rfq.destination}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('RFQ')} <strong class="mt-1 block text-sm font-bold text-foreground">{rfq.id}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Quantity')} <strong class="mt-1 block text-sm font-bold text-foreground">{rfq.quantity}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Incoterm')} <strong class="mt-1 block text-sm font-bold text-foreground">{rfq.incoterm}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Deadline')} <strong class="mt-1 block text-sm font-bold text-foreground">{rfq.deadline}</strong>
						</div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No RFQ matched your search.')}</div>
		{/each}
	</div>
</AppShell>