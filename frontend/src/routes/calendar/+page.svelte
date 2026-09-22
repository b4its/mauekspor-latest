<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { calendarEvents as seedCalendarEvents, projects as seedProjects } from '$lib/data/trade';
	import type { CalendarEvent } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { listCalendarEvents } from '$lib/api/calendar';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createCalendarEvent, markCalendarEventDone, updateCalendarEvent, deleteCalendarEvent } from '$lib/api/calendar';

	const filters = ['All', 'Compliance', 'Payment', 'Shipment', 'Buyer', 'Supplier'];
	const types = ['Compliance', 'Payment', 'Shipment', 'Buyer', 'Supplier'];
	let activeFilter = $state('All');
	let query = $state('');
	let events = createRemoteList(listCalendarEvents, seedCalendarEvents);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	let created = $state(false);
	let creating = $state(false);
	let done = $state(false);
	let error = $state('');
	let message = $state('');
	let busyId = $state('');
	let doneEventId = $state('');
	let showForm = $state(false);
	let editingId = $state('');
	let fTitle = $state('');
	let fDate = $state('');
	let fTime = $state('09:00');
	let fType = $state<CalendarEvent['type']>('Buyer');
	let fProjectId = $state('');
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
		if (!fTitle.trim() || !fDate) {
			error = t('Judul dan tanggal wajib diisi.');
			return;
		}
		creating = true;
		try {
			const payload = {
				title: fTitle.trim(),
				date: fDate,
				time: fTime,
				type: fType,
				projectId: fProjectId || (projects.items[0]?.id ?? '')
			};
			if (editingId) {
				await updateCalendarEvent(editingId, payload);
				message = `Event "${payload.title}" diperbarui.`;
			} else {
				await createCalendarEvent(payload as Parameters<typeof createCalendarEvent>[0]);
				created = true;
				message = `Event "${payload.title}" dibuat.`;
			}
			await events.load();
			showForm = false;
			editingId = '';
			fTitle = '';
		} catch {
			error = t('Gagal membuat event kalender.');
		} finally {
			creating = false;
		}
	}

	function openCreate() {
		editingId = '';
		fTitle = '';
		fDate = new Date().toISOString().slice(0, 10);
		fTime = '09:00';
		fType = 'Buyer';
		fProjectId = projects.items[0]?.id ?? '';
		error = '';
		showForm = true;
	}

	function openEdit(event: { id: string; title: string; date: string; time?: string; type: string; projectId: string }) {
		editingId = event.id;
		fTitle = event.title;
		fDate = event.date;
		fTime = event.time ?? '09:00';
		fType = event.type as CalendarEvent['type'];
		fProjectId = event.projectId;
		error = '';
		showForm = true;
	}

	async function handleDelete(event: { id: string; title: string }) {
		error = '';
		busyId = event.id;
		try {
			await deleteCalendarEvent(event.id);
			const idx = events.items.findIndex((e) => e.id === event.id);
			if (idx >= 0) events.items.splice(idx, 1);
			message = `Event "${event.title}" dihapus.`;
		} catch {
			error = t('Gagal menghapus event.');
		} finally {
			busyId = '';
		}
	}

	async function handleDone(eventId: string) {
		error = '';
		try {
			await markCalendarEventDone(eventId);
			doneEventId = eventId;
			const idx = events.items.findIndex((e) => e.id === eventId);
			if (idx >= 0) events.items[idx] = { ...events.items[idx], status: 'Done' };
		} catch {
			error = t('Gagal menandai event selesai.');
		}
	}
</script>

<svelte:head>
	<title>{t('Kalender')} | MauEkspor</title>
</svelte:head>

<AppShell title="Calendar" eyebrow={t('Trade milestone schedule')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Kalender milestone')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Keep every export deadline visible before it becomes a blocker.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Track compliance deadlines, shipment events, payment follow-ups, buyer meetings, and supplier evidence audits in one calendar view.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create event')}</Button>
			<Badge variant="destructive">{t('Needs action')} {dueSoon}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<label class="grid gap-1 text-sm font-semibold">
					{t('Judul')}
					<Input bind:value={fTitle} placeholder={t('Contoh: Follow-up buyer meeting')} />
				</label>
				<div class="grid gap-2 sm:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tanggal')}
						<Input type="date" bind:value={fDate} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Waktu')}
						<Input type="time" bind:value={fTime} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tipe')}
						<select bind:value={fType} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each types as type}
								<option value={type}>{type}</option>
							{/each}
						</select>
					</label>
				</div>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Proyek')}
					<select bind:value={fProjectId} class="h-10 rounded-md border bg-background px-3 text-sm">
						{#each projects.items as project}
							<option value={project.id}>{project.name}</option>
						{/each}
					</select>
				</label>
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : editingId ? t('Simpan perubahan') : t('Simpan event')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if events.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{events.error}</p>
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

	{#if events.loading}
		<div class="grid gap-4">
			{#each Array(5) as _}
				<Card>
					<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
						<div class="grid min-w-32 place-items-center gap-1 rounded-lg border bg-muted/40 p-3 text-center">
							<Skeleton class="h-5 w-20" />
							<Skeleton class="h-4 w-14" />
						</div>
						<div class="min-w-0 flex-1">
							<Skeleton class="h-5 w-24" />
							<Skeleton class="mt-2 h-6 w-3/4" />
							<Skeleton class="mt-1 h-4 w-full" />
							<Skeleton class="mt-1 h-4 w-1/2" />
						</div>
						<Skeleton class="h-9 w-24" />
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else}
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
						<div class="flex flex-col gap-2">
							<Button variant="outline" disabled={busyId === event.id} onclick={() => handleDone(event.id)}>{t('Mark done')}</Button>
							<Button variant="outline" disabled={busyId === event.id} onclick={() => openEdit(event)}>{t('Edit')}</Button>
							<Button variant="outline" class="text-destructive" disabled={busyId === event.id} onclick={() => handleDelete(event)}>{t('Hapus')}</Button>
						</div>
					</CardContent>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
					{t('No calendar event matched your search.')}
				</div>
			{/each}
		</div>
	{/if}
</AppShell>