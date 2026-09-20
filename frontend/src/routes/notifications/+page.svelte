<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { notifications as seedNotifications } from '$lib/data/trade';
	import { listNotifications, markNotificationRead, archiveNotification } from '$lib/api/notifications';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Unread', 'Read', 'Archived'];

	function trStatus(s: string) {
		return t(s === 'All' ? 'Semua' : s === 'Unread' ? 'Belum dibaca' : s === 'Read' ? 'Dibaca' : 'Diarsipkan');
	}

	function trFilter(f: string) {
		return t(f === 'All' ? 'Semua' : f === 'Unread' ? 'Belum dibaca' : f === 'Read' ? 'Dibaca' : 'Diarsipkan');
	}
	let activeFilter = $state('All');
	let query = $state('');
	let marked = $state(false);
	let marking = $state(false);
	let error = $state('');

	let notifications = createRemoteList(listNotifications, seedNotifications);
	$effect(() => {
		notifications.load();
	});

	let filteredNotifications = $derived(
		notifications.items.filter(
			(item) =>
				(activeFilter === 'All' || item.status === activeFilter) &&
				[item.title, item.description, item.module, item.severity].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let unread = $derived(notifications.items.filter((item) => item.status === 'Unread').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleMarkAll() {
		error = '';
		marking = true;
		try {
			const unreadItems = notifications.items.filter((item) => item.status === 'Unread');
			for (const item of unreadItems) {
				await markNotificationRead(item.id);
			}
			marked = true;
		} catch {
			error = t('Gagal menandai notifikasi.');
		} finally {
			marking = false;
		}
	}

	async function handleMarkRead(id: string) {
		error = '';
		try {
			await markNotificationRead(id);
			const item = notifications.items.find((n) => n.id === id);
			if (item) item.status = 'Read';
		} catch {
			error = t('Gagal menandai notifikasi.');
		}
	}

	async function handleArchive(id: string) {
		error = '';
		try {
			await archiveNotification(id);
			const item = notifications.items.find((n) => n.id === id);
			if (item) item.status = 'Archived';
		} catch {
			error = t('Gagal mengarsipkan notifikasi.');
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(20);
	let pagedItems = $derived(paginate(filteredNotifications ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredNotifications?.length ?? 0, paginationPageSize));

	$effect(() => {
		activeFilter;
		query;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Notifications')} | MauEkspor</title>
</svelte:head>

<AppShell title="Notifications" eyebrow={t('Operational alerts')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Pusat alert')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Tangkap sinyal ekspor yang butuh tindakan sekarang.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Pantau blocker kritis, pengecualian pengiriman, peristiwa pembayaran, dan pembaruan buatan AI dari satu pusat notifikasi.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleMarkAll} disabled={marking}>{marked ? t('Ditandai dibaca') : marking ? t('Menandai...') : t('Mark all read')}</Button>
			<Badge variant="destructive">{t('Belum dibaca')} {unread}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if notifications.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{notifications.error}</p>
	{/if}

	{#if marked}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Notifikasi ditandai dibaca.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Notifikasi ditandai dibaca di backend.')}
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{trFilter(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari notifikasi, modul, tingkat keparahan...')} class="w-[min(390px,100%)]" />
	</div>

	{#if notifications.loading}
		<div class="grid gap-3">
			{#each Array(5) as _}
				<Card class="flex flex-col items-start justify-between gap-4 p-5 md:flex-row md:items-center">
					<div class="min-w-0">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="mt-2.5 h-6 w-3/4" />
						<Skeleton class="mt-2 h-4 w-full" />
					</div>
					<aside class="grid shrink-0 justify-items-start gap-2.5 md:min-w-[200px] md:justify-items-end">
						<Skeleton class="h-5 w-16 rounded-full" />
						<Skeleton class="h-4 w-24" />
						<div class="flex flex-wrap gap-2">
							<Skeleton class="h-9 w-16" />
							<Skeleton class="h-9 w-24" />
							<Skeleton class="h-9 w-16" />
						</div>
					</aside>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-3">
			{#each pagedItems as item}
				<Card class="flex flex-col items-start justify-between gap-4 p-5 md:flex-row md:items-center">
					<div class="min-w-0">
						<Badge variant={toneVariant(statusTone(marked && item.status === 'Unread' ? 'Read' : item.status))}>{marked && item.status === 'Unread' ? t('Dibaca') : trStatus(item.status)}</Badge>
						<strong class="mt-2.5 block text-xl font-bold tracking-tight">{item.title}</strong>
						<p class="mt-2 leading-relaxed text-muted-foreground">{item.description}</p>
					</div>
					<aside class="grid shrink-0 justify-items-start gap-2.5 md:min-w-[200px] md:justify-items-end">
						<Badge variant={toneVariant(statusTone(item.severity))}>{item.severity}</Badge>
						<small class="text-sm text-muted-foreground">{item.module} · {item.time}</small>
						<div class="flex flex-wrap gap-2">
							<Button variant="outline" size="sm" href={item.href}>{t('Buka')}</Button>
							{#if item.status === 'Unread'}
								<Button variant="outline" size="sm" onclick={() => handleMarkRead(item.id)}>{t('Tandai dibaca')}</Button>
							{/if}
							{#if item.status !== 'Archived'}
								<Button variant="ghost" size="sm" onclick={() => handleArchive(item.id)}>{t('Arsip')}</Button>
							{/if}
						</div>
					</aside>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada notifikasi yang cocok dengan pencarian.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredNotifications?.length ?? 0} />

</AppShell>