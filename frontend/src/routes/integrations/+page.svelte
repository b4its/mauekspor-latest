<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { integrations } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listIntegrations, connectIntegration, syncIntegration } from '$lib/api/integrations';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Logistics', 'Finance', 'Compliance', 'Commerce', 'AI'];

	function trCat(x: string) {
		return t(x === 'All' ? 'Semua' : x === 'Logistics' ? 'Logistik' : x === 'Finance' ? 'Keuangan' : x === 'Compliance' ? 'Kepatuhan' : x === 'Commerce' ? 'Commerce' : 'Kecerdasan buatan');
	}

	function trStatus(s: string) {
		return t(s === 'Connected' ? 'Terhubung' : s === 'Needs Auth' ? 'Butuh otorisasi' : 'Terputus');
	}
	let activeFilter = $state('All');
	let query = $state('');
	let synced = $state(false);
	let syncing = $state(false);
	let connected = $state(false);
	let error = $state('');
	let connectedId = $state('');

	let items = createRemoteList(listIntegrations, integrations);
	$effect(() => {
		items.load();
	});

	let filteredIntegrations = $derived(
		items.items.filter(
			(item) =>
				(activeFilter === 'All' || item.category === activeFilter) &&
				[item.name, item.category, item.status, item.description, ...item.scopes].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let connectedCount = $derived(items.items.filter((item) => item.status === 'Connected').length + (connected ? 1 : 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleSync() {
		error = '';
		syncing = true;
		try {
			const connected = items.items.find((item) => item.status === 'Connected') ?? items.items[0];
			if (connected) await syncIntegration(connected.id);
			synced = true;
		} catch {
			error = t('Gagal sinkronisasi.');
		} finally {
			syncing = false;
		}
	}

	async function handleConnect(itemId: string) {
		error = '';
		try {
			await connectIntegration(itemId);
			connectedId = itemId;
		} catch {
			error = t('Gagal menghubungkan integrasi.');
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
	let pagedItems = $derived(paginate(filteredIntegrations ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredIntegrations?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('Integrasi')} | MauEkspor</title>
</svelte:head>

<AppShell title="Integrations" eyebrow={t('Sistem dagang yang terhubung')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Pusat integrasi')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Hubungkan MauEkspor dengan sistem logistik, keuangan, kepatuhan, commerce, dan AI.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Jaga tarif, tonggak pembayaran, referensi regulasi, dan alur kerja AI tetap sinkron dengan sistem operasi ekspor.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleSync} disabled={syncing}>{synced ? t('Tersinkronisasi') : syncing ? t('Menyinkronkan...') : t('Sinkronkan yang terhubung')}</Button>
			<Badge variant="secondary">{t('Terhubung')} {connectedCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if items.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{items.error}</p>
	{/if}

	{#if synced}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Integrasi tersinkronisasi.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Sinkronisasi dijalankan di backend.')}
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{trCat(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari integrasi, lingkup, status...')} class="w-[min(390px,100%)]" />
	</div>

	{#if items.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-5 w-16" />
					</div>
					<Skeleton class="mt-4 h-6 w-3/4" />
					<Skeleton class="mt-2 h-4 w-full" />
					<Skeleton class="mt-2 h-4 w-2/3" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<div class="mt-3 flex flex-wrap gap-2">
						<Skeleton class="h-5 w-16 rounded-full" />
						<Skeleton class="h-5 w-20 rounded-full" />
						<Skeleton class="h-5 w-14 rounded-full" />
					</div>
					<Skeleton class="mt-4 h-9 w-full rounded-lg" />
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as item}
				<Card class="gap-4">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone((connected || connectedId === item.id) && item.status === 'Needs Auth' ? 'Connected' : item.status))}>{(connected || connectedId === item.id) && item.status === 'Needs Auth' ? t('Terhubung') : trStatus(item.status)}</Badge>
						<strong class="text-sm font-bold text-muted-foreground">{trCat(item.category)}</strong>
					</div>
					<CardHeader class="p-0">
						<CardTitle class="text-xl font-bold tracking-tight">{item.name}</CardTitle>
						<CardDescription class="leading-relaxed">{item.description}</CardDescription>
					</CardHeader>
					<CardContent class="grid gap-3 p-0">
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Sinkronisasi terakhir')} <strong class="mt-1 block text-sm font-bold text-foreground">{connected && item.status === 'Needs Auth' ? t('Baru saja') : item.lastSync}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Lingkup')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.scopes.length}</strong>
							</div>
						</div>
						<div class="flex flex-wrap gap-2">
							{#each item.scopes as scope}
								<span class="rounded-full border bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">{scope}</span>
							{/each}
						</div>
					</CardContent>
					<Button variant="outline" onclick={() => handleConnect(item.id)}>{(connected || connectedId === item.id) && item.status === 'Needs Auth' ? t('Terhubung') : item.status === 'Connected' ? t('Hubungkan ulang') : t('Hubungkan')}</Button>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada integrasi yang cocok dengan pencarian.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredIntegrations?.length ?? 0} />

</AppShell>