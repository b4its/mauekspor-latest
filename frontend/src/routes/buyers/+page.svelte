<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { buyers as seedBuyers } from '$lib/data/trade';
import { listBuyers, createBuyer } from '$lib/api/buyers';
import { csvExportUrl } from '$lib/api/client';
import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Lead', 'Qualified', 'Negotiating', 'Active', 'At Risk'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let buyers = createRemoteList(listBuyers, seedBuyers);
	$effect(() => {
		buyers.load();
	});

	let filteredBuyers = $derived(
		buyers.items.filter((buyer) => {
			const matchesFilter = activeFilter === 'All' || buyer.status === activeFilter;
			const matchesQuery = [buyer.name, buyer.country, buyer.segment, buyer.status, ...buyer.interestedProducts]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let activeCount = $derived(buyers.items.filter((buyer) => ['Active', 'Negotiating'].includes(buyer.status)).length);
	let pipelineValue = $derived(buyers.items.reduce((sum, buyer) => sum + buyer.estimatedAnnualValue, 0));
	let avgFit = $derived(Math.round(buyers.items.reduce((sum, buyer) => sum + buyer.fitScore, 0) / (buyers.items.length || 1)));

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			const seed = seedBuyers[0];
			await createBuyer({
				name: seed?.name ?? 'New Buyer Co.',
				country: seed?.country ?? 'Japan',
				segment: seed?.segment ?? 'Food & Beverage',
				interestedProducts: seed?.interestedProducts ?? ['Coffee Beans']
			});
			created = true;
		} catch {
			error = t('Gagal menambahkan buyer.');
		} finally {
			creating = false;
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Buyers | MauEkspor</title>
</svelte:head>

<AppShell title="Buyers" eyebrow={t('Export buyer CRM')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Buyer pipeline')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Manage importer relationships from market signal to repeat order.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Qualify buyers, track contact context, connect accounts to projects, and prioritize the next action that moves export deals forward.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating} class="w-full">{created ? t('Lead captured') : creating ? t('Adding...') : t('Add buyer lead')}</Button>
			<Button href={csvExportUrl('/buyers/export.csv')} variant="outline">CSV</Button>
			<Button href={csvExportUrl('/buyers/export.xlsx')} variant="outline">Excel (.xlsx)</Button>
			<Badge variant="secondary">{t('Active')} {activeCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Buyer lead captured.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Lead tersimpan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button
					class={activeFilter === filter ? '' : ''}
					variant={activeFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (activeFilter = filter)}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search buyer, country, segment...')} class="max-w-xs" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Buyer accounts')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{buyers.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Annual pipeline')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(pipelineValue)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Average fit')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{avgFit}%</strong></CardContent></Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredBuyers as buyer}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/buyers/${buyer.id}`} class="grid h-full gap-3 p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(buyer.status))}>{buyer.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{buyer.fitScore}%</strong>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{buyer.name}</h3>
					<p class="text-sm text-muted-foreground">{buyer.segment} · {buyer.country}</p>
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Pipeline')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(buyer.estimatedAnnualValue)}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Payment')}<strong class="mt-1 block text-sm font-bold text-foreground">{buyer.paymentProfile}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Products')}<strong class="mt-1 block text-sm font-bold text-foreground">{buyer.interestedProducts.join(', ')}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Next step')}<strong class="mt-1 block text-sm font-bold text-foreground">{buyer.nextStep}</strong></div>
					</div>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No buyer matched your search.')}</div>
		{/each}
	</div>
</AppShell>