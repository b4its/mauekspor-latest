<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalArticles as seedArticles, educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalArticles, publishEducationalArticle, createEducationalArticle, deleteEducationalArticle, updateEducationalArticle, uploadEducationalFile } from '$lib/api/educational-articles';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	let articles = createRemoteList(listEducationalArticles, seedArticles);
	let publishing = $state('');
	let deleting = $state('');
	let error = $state('');
	let newTitle = $state('');
	let newContent = $state('');
	let creating = $state(false);
	let editingId = $state('');
	let editTitle = $state('');
	let editContent = $state('');
	let savingEdit = $state(false);
	let uploadingId = $state('');
	let editError = $state('');

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
			error = t('Gagal mempublikasikan artikel.');
		} finally {
			publishing = '';
		}
	}

	async function createArticle() {
		error = '';
		if (newTitle.trim().length < 3) {
			error = t('Judul artikel minimal 3 karakter.');
			return;
		}
		creating = true;
		try {
			const created = (await createEducationalArticle({ title: newTitle, content: newContent, order_index: articles.items.length + 1 })).data;
			articles.items.unshift(created);
			newTitle = '';
			newContent = '';
		} catch {
			error = t('Gagal membuat artikel.');
		} finally {
			creating = false;
		}
	}

	async function removeArticle(id: string) {
		if (!confirm(t('Hapus artikel ini?'))) return;
		error = '';
		deleting = id;
		try {
			await deleteEducationalArticle(id);
			const idx = articles.items.findIndex((a) => a.id === id);
			if (idx >= 0) articles.items.splice(idx, 1);
		} catch {
			error = t('Gagal menghapus artikel.');
		} finally {
			deleting = '';
		}
	}

	async function saveArticle(id: string) {
		editError = '';
		if (editTitle.trim().length < 3) {
			editError = t('Judul artikel minimal 3 karakter.');
			return;
		}
		savingEdit = true;
		try {
			const updated = (await updateEducationalArticle(id, { title: editTitle.trim(), content: editContent })).data;
			const idx = articles.items.findIndex((a) => a.id === id);
			if (idx >= 0) articles.items[idx] = updated;
			editingId = '';
		} catch {
			editError = t('Gagal menyimpan artikel.');
		} finally {
			savingEdit = false;
		}
	}

	async function handleUploadFile(id: string, event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		error = '';
		uploadingId = id;
		try {
			const updated = (await uploadEducationalFile(id, file)).data;
			const idx = articles.items.findIndex((a) => a.id === id);
			if (idx >= 0) articles.items[idx] = updated;
		} catch {
			error = t('Gagal mengunggah file artikel.');
		} finally {
			uploadingId = '';
			input.value = '';
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
	<title>{t('Admin Artikel Edukasi')} | MauEkspor</title>
</svelte:head>

<AppShell title="Educational Admin" eyebrow={t('Manage articles')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="outline">{t('Admin')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Review and publish articles.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					{t('Artikel mendukung eksportir dengan panduan cara-melakukan yang fokus dan berpasangan dengan setiap modul.')}
				</CardDescription>
			</div>
			<Button variant="outline" href="/educational/admin">{t('Beranda admin')}</Button>
		</div>
	</Card>

	<Card class="mt-4">
		<CardHeader class="flex-row items-center justify-between gap-3">
			<CardTitle>{t('Artikel')}</CardTitle>
			<Badge variant="secondary">{articles.items.length} {t('total')}</Badge>
		</CardHeader>
		<CardContent class="grid gap-3">
			<form class="grid gap-2" onsubmit={(event) => { event.preventDefault(); createArticle(); }}>
				<Input placeholder={t('Judul artikel baru...')} bind:value={newTitle} />
				<Textarea placeholder={t('Konten (Markdown)...')} bind:value={newContent} rows={3} />
				<Button type="submit" disabled={creating} class="w-fit">{creating ? t('Membuat...') : t('Buat artikel')}</Button>
			</form>
			{#each articles.items as article}
				<div class="rounded-lg border bg-muted/30 p-3.5">
					{#if editingId === article.id}
						<div class="grid gap-2">
							<Input placeholder={t('Judul artikel...')} bind:value={editTitle} />
							<Textarea placeholder={t('Konten (Markdown)...')} bind:value={editContent} rows={3} />
							{#if editError}
								<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{editError}</p>
							{/if}
							<div class="flex gap-2">
								<Button size="sm" disabled={savingEdit} onclick={() => saveArticle(article.id)}>{savingEdit ? t('Menyimpan...') : t('Simpan')}</Button>
								<Button size="sm" variant="ghost" onclick={() => (editingId = '')}>{t('Batal')}</Button>
							</div>
						</div>
					{:else}
						<div class="flex items-center justify-between gap-3">
							<div>
								<strong class="block text-sm font-bold">{article.title}</strong>
								<span class="mt-1 block text-xs font-semibold text-muted-foreground">{article.readMinutes} min read - {article.level} - {article.tags.join(' · ')}</span>
							</div>
							<div class="grid justify-items-end gap-2">
								<Badge variant={toneVariant(statusTone(article.status))}>{article.status}</Badge>
								<div class="flex items-center gap-2">
									<Button variant="link" size="sm" href={`/educational/articles/${article.id}`}>{t('Lihat')}</Button>
									<Button size="sm" variant="outline" onclick={() => {
										editingId = article.id;
										editTitle = article.title;
										editContent = article.content ?? '';
									}}>{t('Ubah')}</Button>
									<label class="cursor-pointer text-xs font-bold text-muted-foreground hover:underline" title={t('Unggah file')}>
										{uploadingId === article.id ? t('Mengunggah...') : t('Unggah file')}
										<input type="file" class="hidden" disabled={uploadingId !== ''} onchange={(e) => handleUploadFile(article.id, e)} />
									</label>
									<Button size="sm" variant={article.status === 'Published' ? 'outline' : 'default'} disabled={article.status === 'Published' || publishing === article.id} onclick={() => publishArticle(article.id)}>{publishing === article.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
									<Button size="sm" variant="destructive" disabled={deleting === article.id} onclick={() => removeArticle(article.id)}>{deleting === article.id ? '...' : t('Hapus')}</Button>
								</div>
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</CardContent>
	</Card>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
</AppShell>