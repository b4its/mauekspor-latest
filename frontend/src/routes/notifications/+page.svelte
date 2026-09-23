<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { notifications as seedNotifications } from '$lib/data/trade';
	import { listNotifications, markNotificationRead, archiveNotification } from '$lib/api/notifications';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	const filters = ['All', 'Unread', 'Read', 'Archived'];
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
			error = 'Gagal menandai notifikasi.';
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
			error = 'Gagal menandai notifikasi.';
		}
	}

	async function handleArchive(id: string) {
		error = '';
		try {
			await archiveNotification(id);
			const item = notifications.items.find((n) => n.id === id);
			if (item) item.status = 'Archived';
		} catch {
			error = 'Gagal mengarsipkan notifikasi.';
		}
	}
</script>

<svelte:head>
	<title>Notifications | MauEkspor</title>
</svelte:head>

<AppShell title="Notifications" eyebrow="Operational alerts">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Alert center</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Catch the export signals that need action now.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Monitor critical blockers, shipment exceptions, payment events, and AI-generated updates from one notification center.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleMarkAll} disabled={marking}>{marked ? 'Marked read' : marking ? 'Marking...' : 'Mark all read'}</Button>
			<Badge variant="destructive">Unread {unread}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if marked}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Notifications marked as read.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Notifikasi ditandai dibaca di backend.
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search notification, module, severity..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-3">
		{#each filteredNotifications as item}
			<Card class="flex flex-col items-start justify-between gap-4 p-5 md:flex-row md:items-center">
				<div class="min-w-0">
					<Badge variant={toneVariant(statusTone(marked && item.status === 'Unread' ? 'Read' : item.status))}>{marked && item.status === 'Unread' ? 'Read' : item.status}</Badge>
					<strong class="mt-2.5 block text-xl font-bold tracking-tight">{item.title}</strong>
					<p class="mt-2 leading-relaxed text-muted-foreground">{item.description}</p>
				</div>
				<aside class="grid shrink-0 justify-items-start gap-2.5 md:min-w-[200px] md:justify-items-end">
					<Badge variant={toneVariant(statusTone(item.severity))}>{item.severity}</Badge>
					<small class="text-sm text-muted-foreground">{item.module} · {item.time}</small>
					<div class="flex flex-wrap gap-2">
						<Button variant="outline" size="sm" href={item.href}>Open</Button>
						{#if item.status === 'Unread'}
							<Button variant="outline" size="sm" onclick={() => handleMarkRead(item.id)}>Tandai dibaca</Button>
						{/if}
						{#if item.status !== 'Archived'}
							<Button variant="ghost" size="sm" onclick={() => handleArchive(item.id)}>Arsip</Button>
						{/if}
					</div>
				</aside>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No notification matched your search.</div>
		{/each}
	</div>
</AppShell>