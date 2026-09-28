<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { projects, shipments as seedShipments } from '$lib/data/trade';
	import { listShipments, createShipment, updateShipmentMilestone, deleteShipment } from '$lib/api/shipments';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { syncFiltersToUrl } from '$lib/utils/urlFilters';

	import { page } from '$app/state';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';
	import { formatDate } from '$lib/utils/date';

	const filters = ['All', 'Booking Requested', 'Customs Submitted', 'Loaded', 'Exception'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let message = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let fForwarder = $state('');
	let fRoute = $state('');
	let fMode = $state('Ocean FCL');
	let fEta = $state('');
	let fProjectId = $state('');
	let fOrderId = $state('');
	let error = $state('');
	let paramProcessed = $state(false);

	// Konfirmasi terpusat untuk hapus pengiriman (pengganti window.confirm).
	const confirm = createConfirmController();

	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '' }, ['query', 'status']), 250);
		return () => clearTimeout(syncTimer);
	});

	let shipments = createRemoteList(listShipments, seedShipments);
	let remoteProjects = createRemoteList(listTradeProjects, projects);
	$effect(() => {
		shipments.load();
		remoteProjects.load();
	});

	$effect(() => {
		if (paramProcessed) return;
		const queryForwarder = page.url.searchParams.get('forwarder');
		const queryRoute = page.url.searchParams.get('route');
		const queryMode = page.url.searchParams.get('mode');
		const queryProjectId = page.url.searchParams.get('projectId');
		const queryOrderId = page.url.searchParams.get('orderId');
		const queryDestination = page.url.searchParams.get('destination');

		if (queryForwarder || queryRoute || queryProjectId || queryOrderId || queryDestination) {
			if (queryForwarder) fForwarder = queryForwarder;
			if (queryRoute) fRoute = queryRoute;
			else if (queryDestination) fRoute = `Jakarta → ${queryDestination}`;
			if (queryMode) fMode = queryMode;
			if (queryProjectId) fProjectId = queryProjectId;
			if (queryOrderId) fOrderId = queryOrderId;
			showForm = true;
			paramProcessed = true;
		}
	});

	let filteredShipments = $derived(
		shipments.items.filter((shipment) => {
			const matchesFilter = activeFilter === 'All' || shipment.status === activeFilter;
			const matchesQuery = [shipment.id, shipment.route, shipment.forwarder, shipment.mode, shipment.projectId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let exceptionCount = $derived(shipments.items.filter((shipment) => shipment.status === 'Exception').length);
	let averageProgress = $derived(Math.round(shipments.items.reduce((sum, shipment) => sum + shipment.progress, 0) / (shipments.items.length || 1)));

	function projectName(projectId: string) {
		return remoteProjects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}


	function openCreate() {
		fForwarder = '';
		fRoute = '';
		fMode = 'Ocean FCL';
		fEta = '';
		fProjectId = '';
		fOrderId = '';
		formError = '';
		showForm = true;
	}

	let actionId = $state('');

	async function handleCreate() {
		formError = '';
		if (!fForwarder.trim()) {
			formError = t('Forwarder wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await createShipment({
				forwarder: fForwarder.trim(),
				route: fRoute.trim(),
				mode: fMode,
				projectId: fProjectId.trim() || undefined,
				eta: fEta.trim()
			});
			if (res.data) {
				shipments.upsert(res.data);
			} else {
				await shipments.load();
			}
			message = `Pengiriman "${fForwarder.trim()}" dibuat.`;
			showForm = false;
		} catch {
			formError = t('Gagal membuat pengiriman.');
		} finally {
			saving = false;
		}
	}

	async function handleAdvance(shipment: { id: string; status: string; progress: number }) {
		error = '';
		actionId = shipment.id;
		try {
			const res = await updateShipmentMilestone(shipment.id, 'Milestone Update');
			if (res.data) {
				shipments.upsert(res.data);
			} else {
				await shipments.load();
			}
			message = `Milestone pengiriman ${shipment.id} diperbarui.`;
		} catch {
			error = t('Gagal memajukan milestone.');
		} finally {
			actionId = '';
		}
	}

	async function handleDelete(shipment: { id: string; route: string }) {
		error = '';
		actionId = shipment.id;
		try {
			await deleteShipment(shipment.id);
			shipments.remove(shipment.id);
			message = `Pengiriman ${shipment.id} dihapus.`;
		} catch {
			error = t('Gagal menghapus pengiriman.');
		} finally {
			actionId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredShipments ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredShipments?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Pengiriman')} | MauEkspor</title>
</svelte:head>

<AppShell title="Shipments" eyebrow={t('Logistics milestone tracking')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Forwarder operations')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Track bookings, customs, cargo movement, and delivery exceptions.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Coordinate cargo readiness, pickup, warehouse receipt, customs clearance, vessel departure, arrival, destination processing, and issue ownership.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Tambah pengiriman')}</Button>
			<Badge variant="secondary">{t('Avg progress')} {averageProgress}%</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				{#if fOrderId}
					<div class="rounded-md bg-primary/10 px-3 py-1.5 text-xs font-semibold text-primary">
						{t('Booking pengiriman untuk Pesanan')} #{fOrderId}
					</div>
				{/if}
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Forwarder')}
						<Input bind:value={fForwarder} placeholder="Samudera Logistics" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Route')}
						<Input bind:value={fRoute} placeholder="Jakarta → Osaka" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Mode')}
						<select bind:value={fMode} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['Ocean LCL', 'Ocean FCL', 'Air'] as mode}
								<option value={mode}>{mode}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('ETA')}
						<Input bind:value={fEta} placeholder="18 Sep 2026" />
					</label>
				</div>
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Proyek Ekspor')}
						<select bind:value={fProjectId} class="h-10 rounded-md border bg-background px-3 text-sm">
							<option value="">{t('Pilih proyek (opsional)')}</option>
							{#each remoteProjects.items as p}
								<option value={p.id}>{p.name} ({p.country})</option>
							{/each}
						</select>
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleCreate}>{saving ? t('Menyimpan...') : t('Simpan pengiriman')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if shipments.error}
		<p role="alert" class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{shipments.error}</p>
	{/if}

	{#if message}
		<p role="status" class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search"
			aria-label={t('Search route, forwarder, booking...')} placeholder={t('Search route, forwarder, booking...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Active shipments')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{shipments.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Exceptions')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{exceptionCount}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Average progress')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{averageProgress}%</strong></CardContent></Card>
	</div>

	{#if shipments.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-8 w-16" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-1 h-4 w-1/2" />
					<Skeleton class="mt-3 h-2 w-full" />
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
			{#each pagedItems as shipment}
				<Card class="flex flex-col justify-between transition-all hover:border-ring/40 hover:shadow-md">
					<div class="grid gap-3 p-5">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(shipment.status))}>{label(shipment.status)}</Badge>
							<strong class="text-2xl font-bold tracking-tight">{shipment.progress}%</strong>
						</div>
						<a href={`/shipments/${shipment.id}`} class="block no-underline hover:underline">
							<h3 class="text-2xl font-bold tracking-tight text-foreground">{shipment.route}</h3>
							<p class="text-sm text-muted-foreground">{projectName(shipment.projectId)}</p>
						</a>
						<Progress value={shipment.progress} />
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Forwarder')}<strong class="mt-1 block text-sm font-bold text-foreground">{shipment.forwarder}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Mode')}<strong class="mt-1 block text-sm font-bold text-foreground">{shipment.mode}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Booking')}<strong class="mt-1 block text-sm font-bold text-foreground">{shipment.bookingNo}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('ETA')}<strong class="mt-1 block text-sm font-bold text-foreground">{formatDate(shipment.eta)}</strong></div>
						</div>
						{#if shipment.exception}
							<div class="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-semibold text-destructive" role="alert">{shipment.exception}</div>
						{/if}
					</div>
					<div class="flex items-center justify-between border-t bg-muted/10 px-5 py-3">
						<a href={`/shipments/${shipment.id}`} class="text-xs font-semibold text-primary hover:underline">
							{t('Lihat detail')} &rarr;
						</a>
						<div class="flex items-center gap-1.5">
							{#if shipment.progress < 100}
								<Button
									variant="outline"
									size="sm"
									class="h-7 text-xs"
									disabled={actionId === shipment.id}
									onclick={() => handleAdvance(shipment)}
								>
									{actionId === shipment.id ? '...' : t('Maju milestone')}
								</Button>
							{/if}
							<Button
								variant="ghost"
								size="sm"
								class="h-7 text-xs text-destructive hover:bg-destructive/10"
								disabled={actionId === shipment.id}
								onclick={() =>
									confirm.ask({
										title: t('Hapus pengiriman'),
										description: t('Pengiriman ini akan dihapus permanen dari workspace.'),
										detail: `${shipment.route} · ${shipment.id}`,
										action: () => handleDelete(shipment)
									})}
							>
								{t('Hapus')}
							</Button>
						</div>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No shipment matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredShipments?.length ?? 0} />

	<ConfirmDialog
		bind:open={confirm.open}
		title={confirm.title}
		description={confirm.description}
		detail={confirm.detail}
		confirmLabel={confirm.label}
		loading={confirm.loading}
		onconfirm={confirm.run}
	/>
</AppShell>
