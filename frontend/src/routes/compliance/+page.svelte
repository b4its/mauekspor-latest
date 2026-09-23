<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { complianceRequirements as seedRequirements, projects as seedProjects } from '$lib/data/trade';
	import { listComplianceRequirements } from '$lib/api/compliance';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Blocked', 'In Review', 'Evidence Uploaded', 'Verified'];
	let activeFilter = $state('All');
	let query = $state('');

	let complianceRequirements = createRemoteList(listComplianceRequirements, seedRequirements);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		complianceRequirements.load();
		projects.load();
	});

	let filteredRequirements = $derived(
		complianceRequirements.items.filter((item) => {
			const matchesFilter = activeFilter === 'All' || item.status === activeFilter;
			const matchesQuery = [item.title, item.category, item.owner, item.source, item.projectId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let criticalCount = $derived(complianceRequirements.items.filter((item) => item.severity === 'Critical').length);
	let verifiedCount = $derived(complianceRequirements.items.filter((item) => item.status === 'Verified').length);

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{t('Kepatuhan')} | MauEkspor</title>
</svelte:head>

<AppShell title="Compliance" eyebrow={t('Evidence-based export readiness')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Source-backed workflow')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Turn regulatory gaps into verified action items.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Track source, severity, owner, evidence, human verification, and confidence for each export requirement before documents or quotation are finalized.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Critical')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{criticalCount}</strong></CardContent>
			</Card>
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Verified')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{verifiedCount}</strong></CardContent>
			</Card>
		</CardContent>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search requirement, source, project...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredRequirements as item}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<a href={`/compliance/${item.id}`} class="block h-full p-5 no-underline">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(item.status))}>{item.status}</Badge>
						<span class={item.severity.toLowerCase() === 'critical' ? 'rounded-full bg-destructive/10 px-2.5 py-0.5 text-xs font-semibold text-destructive' : item.severity.toLowerCase() === 'major' ? 'rounded-full bg-orange-500/10 px-2.5 py-0.5 text-xs font-semibold text-orange-600' : 'rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary'}>{item.severity}</span>
					</div>
					<h3 class="mt-4 text-2xl font-bold tracking-tight">{item.title}</h3>
					<p class="mt-2 text-sm text-muted-foreground">{projectName(item.projectId)}</p>
					<div class="mt-4 grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Category')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.category}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.owner}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Due')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.due}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Confidence')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.confidence}%</strong></div>
					</div>
					<p class="mt-4 text-xs font-semibold text-muted-foreground">{t('Source: {item.source}')}</p>
				</a>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No compliance requirement matched your search.')}</div>
		{/each}
	</div>
</AppShell>