<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { rfqs as seedRFQs } from '$lib/data/trade';
	import { listRFQs, createRFQ } from '$lib/api/rfq';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Matching', 'Quoted', 'Accepted'];
	let activeFilter = $state('All');
	let query = $state('');
	let error = $state('');
	let message = $state('');
	let showForm = $state(false);
	let creating = $state(false);
	let formError = $state('');
	let fBuyer = $state('');
	let fProduct = $state('');
	let fDestination = $state('');
	let fQuantity = $state('');
	let fIncoterm = $state('FOB');
	let fDeadline = $state('');

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

	function openCreate() {
		formError = '';
		fBuyer = '';
		fProduct = '';
		fDestination = '';
		fQuantity = '';
		fIncoterm = 'FOB';
		fDeadline = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fBuyer.trim()) {
			formError = t('Buyer wajib diisi.');
			return;
		}
		creating = true;
		try {
			await createRFQ({
				buyer: fBuyer.trim(),
				product: fProduct.trim(),
				destination: fDestination.trim(),
				quantity: fQuantity.trim(),
				incoterm: fIncoterm,
				deadline: fDeadline
			});
			await rfqs.load();
			message = `RFQ "${fProduct.trim() || fBuyer.trim()}" dibuat.`;
			showForm = false;
			fBuyer = '';
			fProduct = '';
			fDestination = '';
			fQuantity = '';
			fDeadline = '';
		} catch {
			formError = t('Gagal membuat RFQ.');
		} finally {
			creating = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredRFQs ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredRFQs?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('RFQ')} | MauEkspor</title>
</svelte:head>

<AppShell title="RFQ" eyebrow={t('Buyer demand workspace')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Smart matching')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Match buyer requirements with verified exporter capabilities.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Manage RFQs, destination terms, required certificates, deadlines, and transparent supplier matching explanations.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create RFQ')}</Button>
			<Badge variant="secondary">{t('Avg match')} {averageMatch}%</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Buyer')}
						<Input bind:value={fBuyer} placeholder="Hikari Foods Co." />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Produk')}
						<Input bind:value={fProduct} placeholder="Gayo Arabica Coffee Beans" />
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tujuan')}
						<Input bind:value={fDestination} placeholder="Tokyo, Japan" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kuantitas')}
						<Input bind:value={fQuantity} placeholder="500 kg" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Incoterm')}
						<select bind:value={fIncoterm} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['FOB', 'CIF', 'EXW', 'DAP'] as term}
								<option value={term}>{term}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Deadline')}
						<Input bind:value={fDeadline} type="date" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : t('Simpan RFQ')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if rfqs.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{rfqs.error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search buyer, product, destination...')} class="w-[min(390px,100%)]" />
	</div>

	{#if rfqs.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-16" />
						<Skeleton class="h-7 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as rfq}
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
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredRFQs?.length ?? 0} />

</AppShell>