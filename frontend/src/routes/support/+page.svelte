<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { supportTickets as seedTickets } from '$lib/data/trade';
	import type { SupportTicket } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { listSupportTickets } from '$lib/api/support';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createSupportTicket, resolveSupportTicket, updateSupportTicket, deleteSupportTicket } from '$lib/api/support';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Bug', 'Question', 'Billing', 'Integration', 'Operations'];
	const categories = ['Bug', 'Question', 'Billing', 'Integration', 'Operations'];
	const priorities = ['Low', 'Medium', 'High', 'Critical'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let resolved = $state(false);
	let error = $state('');
	let message = $state('');
	let busyId = $state('');
	let resolvedId = $state('');
	let creating = $state(false);
	let showForm = $state(false);
	let editingId = $state('');
	let fSubject = $state('');
	let fCategory = $state<SupportTicket['category']>('Question');
	let fDescription = $state('');
	let fPriority = $state<SupportTicket['priority']>('Medium');
	let tickets = createRemoteList(listSupportTickets, seedTickets);
	let filteredTickets = $derived(
		tickets.items.filter(
			(ticket) =>
				(activeFilter === 'All' || ticket.category === activeFilter) &&
				[ticket.subject, ticket.category, ticket.status, ticket.priority, ticket.owner, ticket.description].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let openCount = $derived(tickets.items.filter((ticket) => ticket.status !== 'Resolved').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		tickets.load();
	});

	async function handleCreate() {
		error = '';
		if (!fSubject.trim()) {
			error = t('Subjek tiket wajib diisi.');
			return;
		}
		creating = true;
		try {
			if (editingId) {
				const res = await updateSupportTicket(editingId, { subject: fSubject.trim(), category: fCategory, description: fDescription.trim(), priority: fPriority });
				const idx = tickets.items.findIndex((tk) => tk.id === editingId);
				if (idx >= 0) tickets.items[idx] = { ...tickets.items[idx], ...res.data };
				message = `Tiket "${fSubject.trim()}" diperbarui.`;
			} else {
				await createSupportTicket({ subject: fSubject.trim(), category: fCategory, description: fDescription.trim() });
				created = true;
				message = `Tiket "${fSubject.trim()}" dibuat.`;
				await tickets.load();
			}
			showForm = false;
			editingId = '';
			fSubject = '';
			fDescription = '';
		} catch {
			error = t('Gagal membuat tiket.');
		} finally {
			creating = false;
		}
	}

	function openCreate() {
		editingId = '';
		fSubject = '';
		fCategory = 'Question';
		fDescription = '';
		fPriority = 'Medium';
		error = '';
		showForm = true;
	}

	function openEdit(ticket: { id: string; subject: string; category: string; description?: string; priority: string }) {
		editingId = ticket.id;
		fSubject = ticket.subject;
		fCategory = ticket.category as SupportTicket['category'];
		fDescription = ticket.description ?? '';
		fPriority = ticket.priority as SupportTicket['priority'];
		error = '';
		showForm = true;
	}

	async function handleResolve(ticketId: string) {
		error = '';
		try {
			await resolveSupportTicket(ticketId);
			resolvedId = ticketId;
			const idx = tickets.items.findIndex((tk) => tk.id === ticketId);
			if (idx >= 0) tickets.items[idx] = { ...tickets.items[idx], status: 'Resolved' };
		} catch {
			error = t('Gagal menyelesaikan tiket.');
		}
	}

	async function handleDelete(ticket: { id: string; subject: string }) {
		error = '';
		busyId = ticket.id;
		try {
			await deleteSupportTicket(ticket.id);
			const idx = tickets.items.findIndex((tk) => tk.id === ticket.id);
			if (idx >= 0) tickets.items.splice(idx, 1);
			message = `Tiket "${ticket.subject}" dihapus.`;
		} catch {
			error = t('Gagal menghapus tiket.');
		} finally {
			busyId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredTickets ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredTickets?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('Dukungan')} | MauEkspor</title>
</svelte:head>

<AppShell title="Support" eyebrow={t('Help desk and product support')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Meja dukungan')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Get help with export workflows, integrations, billing, and platform issues.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Track support tickets from creation to resolution while keeping each request tied to a clear category and owner.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Create ticket')}</Button>
			<Badge variant="outline">{t('Open')} {openCount}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<label class="grid gap-1 text-sm font-semibold">
					{t('Subjek')}
					<Input bind:value={fSubject} placeholder={t('Ringkas masalah Anda...')} />
				</label>
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kategori')}
						<select bind:value={fCategory} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each categories as category}
								<option value={category}>{category}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Prioritas')}
						<select bind:value={fPriority} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each priorities as priority}
								<option value={priority}>{priority}</option>
							{/each}
						</select>
					</label>
				</div>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Deskripsi')}
					<textarea bind:value={fDescription} rows="3" class="rounded-md border bg-background px-3 py-2 text-sm" placeholder={t('Jelaskan detail masalah...')}></textarea>
				</label>
				<Button class="w-fit" disabled={creating} onclick={handleCreate}>{creating ? t('Creating...') : editingId ? t('Simpan perubahan') : t('Simpan tiket')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if tickets.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{tickets.error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Support ticket created.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Tiket tersimpan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search ticket, owner, issue...')} class="w-[min(390px,100%)]" />
	</div>

	{#if tickets.loading}
		<div class="grid gap-3">
			{#each Array(5) as _}
				<Card class="p-5">
					<div class="flex flex-col items-stretch justify-between gap-4 md:flex-row md:items-center">
						<div class="min-w-0 flex-1">
							<Skeleton class="h-5 w-20" />
							<Skeleton class="mt-3 h-7 w-3/4" />
							<Skeleton class="mt-1 h-4 w-full" />
							<Skeleton class="mt-2 h-4 w-1/3" />
						</div>
						<aside class="grid justify-items-start gap-2 md:justify-items-end">
							<Skeleton class="h-6 w-16" />
							<Skeleton class="h-9 w-24" />
						</aside>
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-3">
			{#each pagedItems as ticket}
				<Card class="flex flex-col items-stretch justify-between gap-4 p-5 md:flex-row md:items-center">
					<div>
						<Badge variant={toneVariant(statusTone(resolved || resolvedId === ticket.id ? 'Resolved' : ticket.status))}>{resolved || resolvedId === ticket.id ? 'Resolved' : ticket.status}</Badge>
						<h3 class="mt-3 text-2xl font-bold tracking-tight">{ticket.subject}</h3>
						<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{ticket.description}</p>
						<small class="mt-2 block text-sm text-muted-foreground">{ticket.category} · {ticket.owner} · {ticket.createdAt}</small>
					</div>
					<aside class="grid justify-items-start gap-2 whitespace-nowrap md:justify-items-end">
						<strong class="text-xl font-bold tracking-tight">{ticket.priority}</strong>
						<Button variant="outline" size="sm" onclick={() => handleResolve(ticket.id)}>{resolvedId === ticket.id ? t('Resolved') : t('Resolve')}</Button>
						<div class="flex gap-2">
							<Button variant="outline" size="sm" disabled={busyId === ticket.id} onclick={() => openEdit(ticket)}>{t('Edit')}</Button>
							<Button variant="outline" size="sm" class="text-destructive" disabled={busyId === ticket.id} onclick={() => handleDelete(ticket)}>{t('Hapus')}</Button>
						</div>
					</aside>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No support ticket matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredTickets?.length ?? 0} />

</AppShell>
