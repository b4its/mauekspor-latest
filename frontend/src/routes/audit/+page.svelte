<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { auditEvents } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listAuditEvents, exportAuditTrail } from '$lib/api/audit';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Info', 'Warning', 'Critical'];
	let activeFilter = $state('All');
	let query = $state('');
	let exported = $state(false);
	let exporting = $state(false);
	let error = $state('');

	let events = createRemoteList(listAuditEvents, auditEvents);
	$effect(() => {
		events.load();
	});

	let filteredEvents = $derived(
		events.items.filter(
			(event) =>
				(activeFilter === 'All' || event.severity === activeFilter) &&
				[event.actor, event.action, event.module, event.entity, event.detail].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleExport() {
		error = '';
		exporting = true;
		try {
			await exportAuditTrail();
			exported = true;
		} catch {
			error = t('Gagal mengekspor audit trail.');
		} finally {
			exporting = false;
		}
	}

	const csvUrl = `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}/audit/export.csv`;
</script>

<svelte:head>
	<title>{t('Log Audit')} | MauEkspor</title>
</svelte:head>

<AppShell title="Audit Log" eyebrow={t('Traceability and governance')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Governance')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Trace important operational and AI-assisted export actions.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Keep a searchable event trail for compliance, document approvals, supplier risk, payment reminders, and AI-generated insights.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleExport} disabled={exporting}>{exported ? t('Audit exported') : exporting ? t('Exporting...') : t('Export audit trail')}</Button>
			<Button variant="outline" href={csvUrl}>{t('Download CSV')}</Button>
			<Badge variant="outline">{t('Events')} {events.items.length}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if events.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{events.error}</p>
	{/if}

	{#if exported}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Audit export prepared.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Export dijalankan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search actor, module, entity...')} class="w-[min(390px,100%)]" />
	</div>

	{#if events.loading}
		<div class="grid gap-4">
			{#each Array(5) as _}
				<Card>
					<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
						<div class="grid gap-1">
							<Skeleton class="h-5 w-16" />
							<Skeleton class="mt-2 h-6 w-48" />
							<Skeleton class="mt-1 h-4 w-full" />
						</div>
						<aside class="grid justify-items-end gap-1">
							<Skeleton class="h-4 w-24" />
							<Skeleton class="h-4 w-20" />
							<Skeleton class="h-3 w-32" />
						</aside>
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4">
			{#each filteredEvents as event}
				<Card>
					<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
						<div class="grid gap-1">
							<Badge variant={toneVariant(statusTone(event.severity))} class="w-fit">{event.severity}</Badge>
							<strong class="mt-2 text-lg font-bold tracking-tight">{event.action}</strong>
							<p class="text-sm text-muted-foreground">{event.detail}</p>
						</div>
						<aside class="grid justify-items-end gap-1 whitespace-nowrap">
							<span class="text-xs text-muted-foreground">{event.time}</span>
							<strong class="text-sm font-bold">{event.actor}</strong>
							<small class="text-xs text-muted-foreground">{event.module} · {event.entity}</small>
						</aside>
					</CardContent>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No audit event matched your search.')}</div>
			{/each}
		</div>
	{/if}
</AppShell>