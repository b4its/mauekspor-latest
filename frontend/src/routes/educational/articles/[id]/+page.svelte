<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { fileDownloadUrl } from '$lib/api/files';
	import { deleteEducationalArticle } from '$lib/api/educational-articles';
	import { goto } from '$app/navigation';

	let { data } = $props();
	let error = $state('');
	let deleting = $state(false);

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus artikel ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteEducationalArticle(data.article.id);
			goto('/educational');
		} catch {
			error = t('Gagal menghapus artikel.');
		} finally {
			deleting = false;
		}
	}

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
				// Legacy: nama storage (tanpa file id) → gunakan fileId bila tersedia.
				? data.article.fileId
					? fileDownloadUrl(data.article.fileId)
					: null
				: data.article.fileUrl.startsWith('/files/')
					// Path backend "/files/{id}/download/" → prefix API base.
					? fileDownloadUrl(data.article.fileUrl.split('/files/')[1].split('/')[0])
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

<AppShell title="Educational" eyebrow={t('Article detail')}>
	<Card class="panel-hero p-6 md:p-8">
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
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{data.article.title}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.article.summary}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-2.5 p-0">
			<Badge>{t('Baca')}</Badge>
			<span class="font-bold text-muted-foreground">{data.article.readMinutes} {t('menit')}</span>
			{#each data.article.tags ?? [] as tag}<Badge variant="outline">{tag}</Badge>{/each}
			{#if fileUrl}
				<Button variant="outline" size="sm" href={fileUrl}>{t('Unduh file')}</Button>
			{/if}
			<Button variant="outline" size="sm" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</CardContent>
		{#if error}
			<p class="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}
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
		<Button variant="outline" href="/educational">{t('Kembali ke edukasi')}</Button>
	</div>
</AppShell>
