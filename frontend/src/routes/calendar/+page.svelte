<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { calendarEvents as seedCalendarEvents, projects as seedProjects } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { listCalendarEvents } from '$lib/api/calendar';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createCalendarEvent, markCalendarEventDone } from '$lib/api/calendar';

	const filters = ['All', 'Compliance', 'Payment', 'Shipment', 'Buyer', 'Supplier'];
	let activeFilter = $state('All');
	let query = $state('');
	let events = createRemoteList(listCalendarEvents, seedCalendarEvents);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	let created = $state(false);
	let creating = $state(false);
	let done = $state(false);
	let error = $state('');
	let doneEventId = $state('');
	let filteredEvents = $derived(
		events.items.filter(
			(event) =>
				(activeFilter === 'All' || event.type === activeFilter) &&
				[event.title, event.type, event.status, event.owner, event.description].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let dueSoon = $derived(events.items.filter((event) => event.status === 'Due Soon' || event.status === 'Blocked').length);
	function projectName(id: string) {
		return projects.items.find((project) => project.id === id)?.name ?? id;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		events.load();
		projects.load();
	});

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			await createCalendarEvent({
				title: 'Follow-up: buyer meeting',
				date: new Date().toISOString().slice(0, 10),
				type: 'Buyer',
				projectId: projects.items[0]?.id ?? 'p-001'
			});
			created = true;
		} catch {
			error = t('Gagal membuat event kalender.');
		} finally {
			creating = false;
		}
	}

	async function handleDone(eventId: string) {
		error = '';
		try {
			await markCalendarEventDone(eventId);
			doneEventId = eventId;
		} catch {
			error = t('Gagal menandai event selesai.');
		}
	}
</script>

<svelte:head>
	<title>{t('Kalender')} | MauEkspor</title>
</svelte:head>

<AppShell title="Calendar" eyebrow={t('Trade milestone schedule')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Kalender milestone')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Keep every export deadline visible before it becomes a blocker.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Track compliance deadlines, shipment events, payment follow-ups, buyer meetings, and supplier evidence audits in one calendar view.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? t('Event created') : creating ? t('Creating...') : t('Create event')}</Button>
			<Badge variant="destructive">{t('Needs action')} {dueSoon}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Calendar event created.')}</strong>
			<span class="block text-sm text-muted-foreground">
				{t('Event tersimpan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search event, owner, status...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4">
		{#each filteredEvents as event}
			<Card>
				<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
					<div class="grid min-w-32 place-items-center gap-1 rounded-lg border bg-muted/40 p-3 text-center">
						<strong class="text-base font-bold tracking-tight">{event.date}</strong>
						<span class="text-xs text-muted-foreground">{event.time}</span>
					</div>
					<div class="min-w-0 flex-1">
						<Badge variant={toneVariant(statusTone(done || doneEventId === event.id ? 'Done' : event.status))}>{done || doneEventId === event.id ? 'Done' : event.status}</Badge>
						<h3 class="mt-2 text-lg font-bold tracking-tight">{event.title}</h3>
						<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{event.description}</p>
						<small class="block text-xs text-muted-foreground">{event.type} · {projectName(event.projectId)} · {event.owner}</small>
					</div>
					<Button variant="outline" onclick={() => handleDone(event.id)}>{t('Mark done')}</Button>
				</CardContent>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
				{t('No calendar event matched your search.')}
			</div>
		{/each}
	</div>
</AppShell>