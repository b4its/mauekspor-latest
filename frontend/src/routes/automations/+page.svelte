<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { automationRules as seedRules } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listAutomations, runAutomation, activateAutomation } from '$lib/api/automations';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Compliance', 'Documents', 'Payments', 'Shipments', 'Reports'];
	let activeFilter = $state('All');
	let query = $state('');
	let rules = createRemoteList(listAutomations, seedRules);
	let error = $state('');
	let message = $state('');
	let busyId = $state('');
	let justRan = $state('');
	let justActivated = $state('');

	$effect(() => {
		rules.load();
	});

	let filteredRules = $derived(
		rules.items.filter(
			(rule) =>
				(activeFilter === 'All' || rule.module === activeFilter) &&
				[rule.name, rule.module, rule.status, rule.trigger, rule.action, rule.description]
					.join(' ')
					.toLowerCase()
					.includes(query.trim().toLowerCase())
		)
	);
	let activeCount = $derived(rules.items.filter((rule) => rule.status === 'Active').length);
	let totalRuns = $derived(rules.items.reduce((sum, rule) => sum + rule.runs, 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleRun(ruleId: string) {
		error = '';
		message = '';
		busyId = ruleId;
		try {
			const res = await runAutomation(ruleId);
			justRan = ruleId;
			justActivated = '';
			// Update rule lokal dengan hasil backend (mutasi index $state)
			const idx = rules.items.findIndex((r) => r.id === ruleId);
			if (idx >= 0) rules.items[idx] = { ...rules.items[idx], ...res.data, lastRun: res.data.lastRun ?? 'now' };
			message = `Rule "${res.data.name}" dijalankan — total ${res.data.runs} kali.`;
		} catch {
			error = t('Gagal menjalankan rule.');
		} finally {
			busyId = '';
		}
	}

	async function handleActivate(ruleId: string) {
		error = '';
		message = '';
		busyId = ruleId;
		try {
			const res = await activateAutomation(ruleId);
			justActivated = ruleId;
			justRan = '';
			const idx = rules.items.findIndex((r) => r.id === ruleId);
			if (idx >= 0) rules.items[idx] = { ...rules.items[idx], ...res.data, status: res.data.status ?? 'Active' };
			message = `Rule "${res.data.name}" kini Active.`;
		} catch {
			error = t('Gagal mengaktifkan rule.');
		} finally {
			busyId = '';
		}
	}
</script>

<svelte:head>
	<title>{t('Automations')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Automations')} eyebrow={t('Workflow rules')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Mesin aturan')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Otomatiskan operasi ekspor berulang tanpa kehilangan kendali.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Buat aturan untuk blocker kepatuhan, validasi dokumen, pengingat pembayaran, pengecualian pengiriman, dan laporan berulang.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Badge variant="secondary">Active {activeCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if rules.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{rules.error}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari aturan, pemicu, aksi...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Aturan')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{rules.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Active')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{activeCount}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total run')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{totalRuns}</strong></CardContent></Card>
	</div>

	{#if rules.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-5 w-16" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-full" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<div class="mt-2 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-9 w-full rounded-lg" />
						<Skeleton class="h-9 w-full rounded-lg" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each filteredRules as rule}
				<Card class="grid gap-4">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(justActivated === rule.id ? 'Active' : rule.status))}>{justActivated === rule.id ? 'Active' : rule.status}</Badge>
						<strong class="text-sm font-bold text-muted-foreground">{rule.module}</strong>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{rule.name}</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">{rule.description}</p>
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Ketika')}<strong class="mt-1 block text-sm font-bold text-foreground">{rule.trigger}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Lalu')}<strong class="mt-1 block text-sm font-bold text-foreground">{rule.action}</strong></div>
					</div>
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Runs')}<strong class="mt-1 block text-sm font-bold text-foreground">{rule.runs}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Run terakhir')}<strong class="mt-1 block text-sm font-bold text-foreground">{rule.lastRun}</strong></div>
					</div>
					<div class="grid grid-cols-2 gap-2">
						<Button variant="outline" disabled={busyId === rule.id} onclick={() => handleRun(rule.id)}>
							{busyId === rule.id ? '...' : 'Run'}
						</Button>
						<Button variant={rule.status === 'Active' || justActivated === rule.id ? 'secondary' : 'outline'} disabled={busyId === rule.id} onclick={() => handleActivate(rule.id)}>
							{rule.status === 'Active' || justActivated === rule.id ? 'Active' : 'Activate'}
						</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada aturan yang cocok dengan pencarian.')}</div>
			{/each}
		</div>
	{/if}
</AppShell>
