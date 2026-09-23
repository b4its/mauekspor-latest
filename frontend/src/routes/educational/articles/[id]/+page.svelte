<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';

	let { data } = $props();

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.article.title} | MauEkspor</title>
</svelte:head>

<AppShell title="Educational" eyebrow="Article detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<div class="flex flex-wrap items-center gap-2.5">
				<Badge variant={toneVariant(statusTone(data.article.status))}>{data.article.status}</Badge>
				<Badge variant="secondary">{data.article.level}</Badge>
			</div>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{data.article.title}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.article.summary}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-2.5 p-0">
			<Badge>Read</Badge>
			<span class="font-bold text-muted-foreground">{data.article.readMinutes} minutes</span>
			{#each data.article.tags as tag}<Badge variant="outline">{tag}</Badge>{/each}
		</CardContent>
	</Card>

	<article class="max-w-3xl space-y-4 leading-relaxed text-muted-foreground">
		<Badge variant="secondary">Guide</Badge>
		<h2 class="text-xl font-bold text-foreground">{data.article.title}</h2>
		<p>{data.article.body}</p>
	</article>

	<div class="mt-5">
		<Button variant="outline" href="/educational">Back to educational</Button>
	</div>
</AppShell>
