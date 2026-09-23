<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { automationRules } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { runAutomation, activateAutomation } from '$lib/api/automations';

	const filters = ['All', 'Compliance', 'Documents', 'Payments', 'Shipments', 'Reports'];
	let activeFilter = $state('All');
	let query = $state('');
	let activated = $state(false);
	let run = $state(false);
	let error = $state('');
	let runRuleId = $state('');
	let activeRuleId = $state('');
	let filteredRules = $derived(
		automationRules.filter(
			(rule) =>
				(activeFilter === 'All' || rule.module === activeFilter) &&
				[rule.name, rule.module, rule.status, rule.trigger, rule.action, rule.description].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let activeCount = $derived(automationRules.filter((rule) => rule.status === 'Active').length + (activated ? 1 : 0));
	let totalRuns = $derived(automationRules.reduce((sum, rule) => sum + rule.runs, 0) + (run ? 1 : 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleRun() {
		error = '';
		try {
			await runAutomation(automationRules[0]?.id ?? 'a-001');
			run = true;
			runRuleId = automationRules[0]?.id ?? 'a-001';
		} catch {
			error = 'Gagal menjalankan rule.';
		}
	}

	async function handleActivate(ruleId: string) {
		error = '';
		try {
			await activateAutomation(ruleId);
			activeRuleId = ruleId;
			activated = true;
		} catch {
			error = 'Gagal mengaktifkan rule.';
		}
	}
</script>

<svelte:head>
	<title>Automations | MauEkspor</title>
</svelte:head>

<AppShell title="Automations" eyebrow="Workflow rules">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Rules engine</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Automate repetitive export operations without losing control.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Create rules for compliance blockers, document validation, payment reminders, shipment exceptions, and recurring reports.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleRun}>{run ? 'Rule run' : 'Run rule'}</Button>
			<Badge variant="secondary">Active {activeCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if run}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Automation executed.</strong>
			<span class="block text-sm text-muted-foreground">Rule dijalankan di backend.</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search automation, trigger, action..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Rules</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{automationRules.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Active</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{activeCount}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Total runs</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{totalRuns}</strong></CardContent></Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredRules as rule}
			<Card class="grid gap-4">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(activated && rule.status === 'Draft' ? 'Active' : rule.status))}>{activated ? 'Active' : rule.status}</Badge>
					<strong class="text-sm font-bold text-muted-foreground">{rule.module}</strong>
				</div>
				<h3 class="text-2xl font-bold tracking-tight">{rule.name}</h3>
				<p class="text-sm leading-relaxed text-muted-foreground">{rule.description}</p>
				<div class="grid grid-cols-2 gap-2">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">When<strong class="mt-1 block text-sm font-bold text-foreground">{rule.trigger}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Then<strong class="mt-1 block text-sm font-bold text-foreground">{rule.action}</strong></div>
				</div>
				<div class="grid grid-cols-2 gap-2">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Runs<strong class="mt-1 block text-sm font-bold text-foreground">{rule.runs + (run ? 1 : 0)}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Last run<strong class="mt-1 block text-sm font-bold text-foreground">{run ? 'Just now' : rule.lastRun}</strong></div>
				</div>
				<Button variant="outline" onclick={() => handleActivate(rule.id)}>{activeRuleId === rule.id ? 'Active' : 'Activate'}</Button>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No automation matched your search.</div>
		{/each}
	</div>
</AppShell>
