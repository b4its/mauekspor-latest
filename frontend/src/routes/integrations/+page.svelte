<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { integrations } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listIntegrations, connectIntegration, syncIntegration, disconnectIntegration, createIntegration, updateIntegration, deleteIntegration } from '$lib/api/integrations';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Logistics', 'Finance', 'Compliance', 'Commerce', 'AI'];
	const categories = ['Logistics', 'Finance', 'Compliance', 'Commerce', 'AI'];

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
	let message = $state('');
	let connectedId = $state('');
	let busyId = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let editingId = $state('');
	let fName = $state('');
	let fCategory = $state('Logistics');
	let fDescription = $state('');
	let fScopes = $state('');

	let items = createRemoteList(listIntegrations, integrations);
	$effect(() => {
		items.load();
	});

	let filteredIntegrations = $derived(
		items.items.filter(
			(item) =>
				(activeFilter === 'All' || item.category === activeFilter) &&
				[item.name, item.category, item.status, item.description, ...(item.scopes ?? [])].join(' ').toLowerCase().includes(query.trim().toLowerCase())
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

	function resetForm() {
		editingId = '';
		fName = '';
		fCategory = 'Logistics';
		fDescription = '';
		fScopes = '';
	}

	function openCreate() {
		resetForm();
		formError = '';
		showForm = true;
	}

	function openEdit(item: { id: string; name: string; category: string; description?: string; scopes?: string[] }) {
		editingId = item.id;
		fName = item.name;
		fCategory = item.category;
		fDescription = item.description ?? '';
		fScopes = (item.scopes ?? []).join(', ');
		formError = '';
		showForm = true;
	}

	async function handleSave() {
		formError = '';
		if (!fName.trim()) {
			formError = t('Nama integrasi wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload = {
				name: fName.trim(),
				category: fCategory,
				description: fDescription.trim(),
				scopes: fScopes.split(',').map((s) => s.trim()).filter(Boolean)
			};
			if (editingId) {
				await updateIntegration(editingId, payload);
				message = `Integrasi "${payload.name}" diperbarui.`;
			} else {
				await createIntegration(payload);
				message = `Integrasi "${payload.name}" dibuat.`;
			}
			await items.load();
			showForm = false;
			resetForm();
		} catch {
			formError = t('Gagal menyimpan integrasi.');
		} finally {
			saving = false;
		}
	}

	async function handleDisconnect(itemId: string) {
		error = '';
		busyId = itemId;
		try {
			await disconnectIntegration(itemId);
			connectedId = '';
			const idx = items.items.findIndex((i) => i.id === itemId);
			if (idx >= 0) items.items[idx] = { ...items.items[idx], status: 'Disconnected' };
			message = t('Integrasi diputus.');
		} catch {
			error = t('Gagal memutus integrasi.');
		} finally {
			busyId = '';
		}
	}

	async function handleDelete(item: { id: string; name: string }) {
		error = '';
		busyId = item.id;
		try {
			await deleteIntegration(item.id);
			const idx = items.items.findIndex((i) => i.id === item.id);
			if (idx >= 0) items.items.splice(idx, 1);
			message = `Integrasi "${item.name}" dihapus.`;
		} catch {
			error = t('Gagal menghapus integrasi.');
		} finally {
			busyId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
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
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Tambah integrasi')}</Button>
			<Badge variant="secondary">{t('Terhubung')} {connectedCount}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nama integrasi')}
						<Input bind:value={fName} placeholder="Forwarder Rate Gateway" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kategori')}
						<select bind:value={fCategory} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each categories as category}
								<option value={category}>{trCat(category)}</option>
							{/each}
						</select>
					</label>
				</div>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Deskripsi')}
					<Input bind:value={fDescription} placeholder={t('Deskripsi singkat integrasi...')} />
				</label>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Lingkup (dipisah koma)')}
					<Input bind:value={fScopes} placeholder="Rates, Bookings" />
				</label>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleSave}>{saving ? t('Menyimpan...') : editingId ? t('Simpan perubahan') : t('Simpan integrasi')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
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
					{#if item.status === 'Connected' || connectedId === item.id}
						<Button variant="outline" disabled={busyId === item.id} onclick={() => handleDisconnect(item.id)}>{t('Putuskan')}</Button>
					{/if}
					<div class="grid grid-cols-2 gap-2">
						<Button variant="outline" disabled={busyId === item.id} onclick={() => openEdit(item)}>{t('Edit')}</Button>
						<Button variant="outline" class="text-destructive" disabled={busyId === item.id} onclick={() => handleDelete(item)}>{t('Hapus')}</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada integrasi yang cocok dengan pencarian.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredIntegrations?.length ?? 0} />

</AppShell>