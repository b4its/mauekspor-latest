<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalArticles as seedArticles, educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalArticles, publishEducationalArticle, createEducationalArticle, deleteEducationalArticle } from '$lib/api/educational-articles';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	let articles = createRemoteList(listEducationalArticles, seedArticles);
	let publishing = $state('');
	let deleting = $state('');
	let error = $state('');
	let newTitle = $state('');
	let newContent = $state('');
	let creating = $state(false);

	$effect(() => {
		articles.load();
	});

	async function publishArticle(id: string) {
		error = '';
		publishing = id;
		try {
			await publishEducationalArticle(id);
			const article = articles.items.find((item) => item.id === id);
			if (article) article.status = 'Published';
		} catch {
			error = 'Gagal mempublikasikan artikel.';
		} finally {
			publishing = '';
		}
	}

	async function createArticle() {
		error = '';
		if (newTitle.trim().length < 3) {
			error = 'Judul artikel minimal 3 karakter.';
			return;
		}
		creating = true;
		try {
			const created = (await createEducationalArticle({ title: newTitle, content: newContent, order_index: articles.items.length + 1 })).data;
			articles.items.unshift(created);
			newTitle = '';
			newContent = '';
		} catch {
			error = 'Gagal membuat artikel.';
		} finally {
			creating = false;
		}
	}

	async function removeArticle(id: string) {
		if (!confirm('Hapus artikel ini?')) return;
		error = '';
		deleting = id;
		try {
			await deleteEducationalArticle(id);
			const idx = articles.items.findIndex((a) => a.id === id);
			if (idx >= 0) articles.items.splice(idx, 1);
		} catch {
			error = 'Gagal menghapus artikel.';
		} finally {
			deleting = '';
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Educational Articles Admin | MauEkspor</title>
</svelte:head>

<AppShell title="Educational Admin" eyebrow="Manage articles">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="outline">Admin</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Review and publish articles.
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					Articles support exporters with focused how-to guidance that pairs with each module.
				</CardDescription>
			</div>
			<Button variant="outline" href="/educational/admin">Admin home</Button>
		</div>
	</Card>

	<Card class="mt-4">
		<CardHeader class="flex-row items-center justify-between gap-3">
			<CardTitle>Articles</CardTitle>
			<Badge variant="secondary">{articles.items.length} total</Badge>
		</CardHeader>
		<CardContent class="grid gap-3">
			<form class="grid gap-2" onsubmit={(event) => { event.preventDefault(); createArticle(); }}>
				<Input placeholder="Judul artikel baru..." bind:value={newTitle} />
				<Textarea placeholder="Konten (Markdown)..." bind:value={newContent} rows={3} />
				<Button type="submit" disabled={creating} class="w-fit">{creating ? 'Membuat...' : 'Buat artikel'}</Button>
			</form>
			{#each articles.items as article}
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<div>
						<strong class="block text-sm font-bold">{article.title}</strong>
						<span class="mt-1 block text-xs font-semibold text-muted-foreground">{article.readMinutes} min read - {article.level} - {article.tags.join(' · ')}</span>
					</div>
					<div class="grid justify-items-end gap-2">
						<Badge variant={toneVariant(statusTone(article.status))}>{article.status}</Badge>
						<div class="flex items-center gap-2">
							<Button variant="link" size="sm" href={`/educational/articles/${article.id}`}>View</Button>
							<Button size="sm" variant={article.status === 'Published' ? 'outline' : 'default'} disabled={article.status === 'Published' || publishing === article.id} onclick={() => publishArticle(article.id)}>{publishing === article.id ? 'Publishing...' : 'Publish'}</Button>
							<Button size="sm" variant="destructive" disabled={deleting === article.id} onclick={() => removeArticle(article.id)}>{deleting === article.id ? '...' : 'Hapus'}</Button>
						</div>
					</div>
				</div>
			{/each}
		</CardContent>
	</Card>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
</AppShell>