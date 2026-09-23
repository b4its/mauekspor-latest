<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { templates } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { useTemplate } from '$lib/api/templates';

	const filters = ['All', 'Document', 'Email', 'Workflow', 'Catalog'];
	let activeFilter = $state('All');
	let query = $state('');
	let used = $state(false);
	let error = $state('');
	let usedId = $state('');
	let filteredTemplates = $derived(
		templates.filter(
			(item) =>
				(activeFilter === 'All' || item.category === activeFilter) &&
				[item.title, item.category, item.status, item.description, item.usedBy, ...item.fields].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let readyCount = $derived(templates.filter((item) => item.status === 'Ready').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleUse(templateId: string) {
		error = '';
		try {
			await useTemplate(templateId);
			used = true;
			usedId = templateId;
		} catch {
			error = 'Gagal menerapkan template.';
		}
	}
</script>

<svelte:head>
	<title>Templates | MauEkspor</title>
</svelte:head>

<AppShell title="Templates" eyebrow="Reusable export assets">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Template library</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Standardize export documents, emails, workflows, and catalogs.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Use controlled templates to reduce manual work, keep evidence consistent, and speed up RFQ-to-shipment execution.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={() => handleUse(templates[0]?.id ?? 't-001')}>{used ? 'Template used' : 'Use template'}</Button>
			<Badge>Ready {readyCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if used}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Template applied.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Template diterapkan di backend.
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search template, field, module..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredTemplates as template}
			<Card class="gap-4">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(template.status))}>{template.status}</Badge>
					<strong class="text-sm font-bold text-muted-foreground">{template.category}</strong>
				</div>
				<CardHeader class="p-0">
					<CardTitle class="text-xl font-bold tracking-tight">{template.title}</CardTitle>
					<CardDescription class="leading-relaxed">{template.description}</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-3 p-0">
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Used by <strong class="mt-1 block text-sm font-bold text-foreground">{template.usedBy}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Updated <strong class="mt-1 block text-sm font-bold text-foreground">{template.updatedAt}</strong>
						</div>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each template.fields as field}
							<span class="rounded-full border bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">{field}</span>
						{/each}
					</div>
				</CardContent>
				<Button variant="outline" onclick={() => handleUse(template.id)}>{usedId === template.id ? 'Applied' : 'Apply'}</Button>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No template matched your search.</div>
		{/each}
	</div>
</AppShell>