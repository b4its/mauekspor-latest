<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { fileDownloadUrl } from '$lib/api/files';

	let { data } = $props();

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	// Konten: backend `content` (markdown) atau fallback `body`
	let content = $derived((data.article.content || data.article.body || '') as string);
	let paragraphs = $derived(content.split(/\n{2,}/).filter((p: string) => p.trim()));

	// Video embed (YouTube / Vimeo)
	function getEmbedUrl(url: string): string | null {
		const yt = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([\w-]{6,})/);
		if (yt) return `https://www.youtube.com/embed/${yt[1]}`;
		const vimeo = url.match(/vimeo\.com\/(\d+)/);
		if (vimeo) return `https://player.vimeo.com/video/${vimeo[1]}`;
		return null;
	}

	let embedUrl = $derived(data.article.videoUrl ? getEmbedUrl(data.article.videoUrl) : null);
	let fileUrl = $derived(
		data.article.fileUrl
			? data.article.fileUrl.startsWith('/files/storage/')
				? fileDownloadUrl(data.article.fileUrl.split('/files/storage/')[1])
				: data.article.fileUrl
			: null
	);

	function renderInline(text: string): string {
		return text
			.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
			.replace(/\*(.+?)\*/g, '<em>$1</em>')
			.replace(/`(.+?)`/g, '<code class="rounded bg-muted px-1 py-0.5 font-mono text-xs">$1</code>');
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
				{#if data.article.videoUrl}
					<Badge variant="outline">Video</Badge>
				{/if}
				{#if data.article.fileUrl}
					<Badge variant="outline">File</Badge>
				{/if}
			</div>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{data.article.title}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.article.summary}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-2.5 p-0">
			<Badge>Read</Badge>
			<span class="font-bold text-muted-foreground">{data.article.readMinutes} minutes</span>
			{#each data.article.tags ?? [] as tag}<Badge variant="outline">{tag}</Badge>{/each}
			{#if fileUrl}
				<Button variant="outline" size="sm" href={fileUrl}>Download file</Button>
			{/if}
		</CardContent>
	</Card>

	{#if embedUrl}
		<div class="overflow-hidden rounded-xl border shadow-sm">
			<iframe src={embedUrl} class="aspect-video w-full" title={data.article.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
		</div>
	{/if}

	<article class="max-w-3xl space-y-4 leading-relaxed text-muted-foreground">
		{#each paragraphs as paragraph}
			{#if /^#\s+/.test(paragraph)}
				<h2 class="text-xl font-bold text-foreground">{@html renderInline(paragraph.replace(/^#\s+/, ''))}</h2>
			{:else if /^-\s+/.test(paragraph)}
				<ul class="grid gap-1.5">
					{#each paragraph.split('\n') as line}
						{@const item = line.replace(/^-\s+/, '')}
						<li class="flex items-start gap-2"><span class="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary"></span><span>{@html renderInline(item)}</span></li>
					{/each}
				</ul>
			{:else}
				<p>{@html renderInline(paragraph)}</p>
			{/if}
		{/each}
	</article>

	<div class="mt-5">
		<Button variant="outline" href="/educational">Back to educational</Button>
	</div>
</AppShell>
