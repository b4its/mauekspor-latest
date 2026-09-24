<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { projects as seedProjects } from '$lib/data/trade';
	import { listTradeProjects, createTradeProject } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	let search = $state('');
	let error = $state('');
	let message = $state('');
	let showForm = $state(false);
	let creating = $state(false);
	let formError = $state('');
	let fName = $state('');
	let fCountry = $state('');
	let fProjectType = $state('');
	let fProduct = $state('');
	let fBuyer = $state('');
	let fIncoterm = $state('FOB');
	let fTargetValue = $state('');
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		projects.load();
	});

	let filtered = $derived(
		projects.items.filter((project) => {
			const keyword = search.trim().toLowerCase();
			return keyword.length === 0
				? true
				: [project.name, project.buyer, project.country, project.product, project.stage]
						.join(' ')
						.toLowerCase()
						.includes(keyword);
		})
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	function openCreate() {
		formError = '';
		fName = '';
		fCountry = '';
		fProjectType = '';
		fProduct = '';
		fBuyer = '';
		fIncoterm = 'FOB';
		fTargetValue = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fName.trim()) {
			formError = t('Nama proyek wajib diisi.');
			return;
		}
		creating = true;
		try {
			const res = await createTradeProject({
				name: fName.trim(),
				country: fCountry.trim(),
				projectType: fProjectType.trim(),
				product: fProduct.trim(),
				buyer: fBuyer.trim(),
				incoterm: fIncoterm,
				targetValue: Number(fTargetValue) || 0
			});
			if (res.data) {
				projects.upsert(res.data);
			} else {
				await projects.load();
			}
			message = `Proyek "${fName.trim()}" dibuat.`;
			showForm = false;
			fName = '';
			fCountry = '';
			fProjectType = '';
			fProduct = '';
			fBuyer = '';
			fTargetValue = '';
		} catch {
			formError = t('Gagal membuat proyek.');
		} finally {
			creating = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filtered ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filtered?.length ?? 0, paginationPageSize));

	$effect(() => {
		search;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Proyek Dagang')} | MauEkspor</title>
</svelte:head>

<AppShell title="Trade Projects" eyebrow="Project-based trade operations">
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="flex-row flex-wrap items-start justify-between gap-3 p-0">
			<div>
				<Badge variant="outline">{t('Workspace proyek')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Kelola eksekusi ekspor-impor dalam satu tempat.')}</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed">
					Each project connects product, HS classification, compliance evidence, quotation,
					documents, and shipment milestones.
				</CardDescription>
			</div>
			<div class="grid gap-2">
				<Input bind:value={search} type="search" placeholder={t('Search buyer, product, country...')} class="min-w-[min(380px,100%)]" />
				<Button variant="outline" class="w-fit" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create project')}</Button>
			</div>
		</CardHeader>

		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nama')}
						<Input bind:value={fName} placeholder="Gayo Coffee Export Program" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Negara')}
						<Input bind:value={fCountry} placeholder="Japan" />
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tipe proyek')}
						<Input bind:value={fProjectType} placeholder={t('Export program')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Produk')}
						<Input bind:value={fProduct} placeholder="Coffee Beans" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Buyer')}
						<Input bind:value={fBuyer} placeholder="Hikari Foods Co." />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Incoterm')}
						<select bind:value={fIncoterm} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['FOB', 'CIF', 'EXW', 'DAP'] as term}
								<option value={term}>{term}</option>
							{/each}
						</select>
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Target nilai')}
						<Input bind:value={fTargetValue} type="number" placeholder="0" />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : t('Simpan proyek')}</Button>
			</CardContent>
		{/if}

		{#if error}
			<p class="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}
		{#if message}
			<p class="mt-4 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
		{/if}

		<CardContent class="mt-6 grid gap-4 p-0 md:grid-cols-2 xl:grid-cols-3">
			{#if projects.error}
				<p class="col-span-full rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{projects.error}</p>
			{/if}
			{#if projects.loading}
				{#each Array(6) as _}
					<Card class="p-5">
						<div class="flex items-center justify-between gap-3">
							<Skeleton class="h-5 w-20" />
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
			{:else}
				{#each pagedItems as project}
					<Card class="transition-all hover:border-ring/40 hover:shadow-md">
						<a href={`/trade-projects/${project.id}`} class="grid h-full gap-4 p-5 no-underline">
							<div class="flex items-center justify-between gap-3">
								<Badge variant={toneVariant(statusTone(project.risk))}>{project.risk} {t('risk')}</Badge>
								<strong class="text-2xl font-bold tracking-tight">{project.readiness}%</strong>
							</div>
							<h3 class="text-2xl font-bold tracking-tight">{project.name}</h3>
							<p class="text-sm text-muted-foreground">{project.product}</p>
							<div class="grid grid-cols-2 gap-2">
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Buyer')}<strong class="mt-1 block text-sm font-bold text-foreground">{project.buyer}</strong></div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Destination')}<strong class="mt-1 block text-sm font-bold text-foreground">{project.country}</strong></div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Stage')}<strong class="mt-1 block text-sm font-bold text-foreground">{project.stage}</strong></div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Value')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(project.value)}</strong></div>
							</div>
						</a>
					</Card>
				{/each}
			{/if}
		</CardContent>
	</Card>
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filtered?.length ?? 0} />

</AppShell>
