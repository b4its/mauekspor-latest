<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { knowledgeArticles } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { publishKnowledgeArticle } from '$lib/api/knowledge';

	const filters = ['All', 'Export Basics', 'Compliance', 'Logistics', 'Finance', 'Platform'];
	let activeFilter = $state('All');
	let query = $state('');
	let published = $state(false);
	let error = $state('');
	let publishedId = $state('');
	let filteredArticles = $derived(
		knowledgeArticles.filter(
			(article) =>
				(activeFilter === 'All' || article.category === activeFilter) &&
				[article.title, article.category, article.status, article.summary, ...article.steps].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let publishedCount = $derived(knowledgeArticles.filter((article) => article.status === 'Published').length + (published ? 1 : 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handlePublish() {
		error = '';
		const draft = knowledgeArticles.find((article) => article.status === 'Draft') ?? knowledgeArticles[0];
		try {
			await publishKnowledgeArticle(draft.id);
			published = true;
			publishedId = draft.id;
		} catch {
			error = 'Gagal mempublikasikan artikel.';
		}
	}
</script>

<svelte:head>
	<title>Knowledge Base | MauEkspor</title>
</svelte:head>

<AppShell title="Knowledge Base" eyebrow="Export operating playbooks">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Guided operations</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Keep export know-how close to the workflow.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">Publish practical playbooks for product readiness, HS review, Incoterms, shipment exceptions, finance, and platform usage.</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handlePublish}>{published ? 'Article published' : 'Publish article'}</Button>
			<Badge>Published {publishedCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if published}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Article published.</strong>
			<span class="block text-sm text-muted-foreground">Artikel dipublikasikan di backend.</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search article, step, category..." class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredArticles as article}
			<Card class="grid gap-4">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(published && article.id === publishedId ? 'Published' : article.status))}>{published && article.id === publishedId ? 'Published' : article.status}</Badge>
					<strong class="text-sm font-bold text-muted-foreground">{article.readTime}</strong>
				</div>
				<h3 class="text-2xl font-bold tracking-tight">{article.title}</h3>
				<p class="text-sm leading-relaxed text-muted-foreground">{article.summary}</p>
				<div class="grid grid-cols-2 gap-2">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Category<strong class="mt-1 block text-sm font-bold text-foreground">{article.category}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Updated<strong class="mt-1 block text-sm font-bold text-foreground">{article.updatedAt}</strong></div>
				</div>
				<ol class="m-0 list-decimal space-y-1.5 pl-5 font-bold text-muted-foreground">
					{#each article.steps as step}<li>{step}</li>{/each}
				</ol>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No article matched your search.</div>
		{/each}
	</div>
</AppShell>
