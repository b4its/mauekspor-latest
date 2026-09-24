<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { knowledgeArticles as seedArticles } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { listKnowledgeArticles, publishKnowledgeArticle, createKnowledgeArticle, updateKnowledgeArticle, deleteKnowledgeArticle } from '$lib/api/knowledge';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Export Basics', 'Compliance', 'Logistics', 'Finance', 'Platform'];
	const categories = ['Export Basics', 'Compliance', 'Logistics', 'Finance', 'Platform'];
	let activeFilter = $state('All');
	let query = $state('');
	let published = $state(false);
	let articles = createRemoteList(listKnowledgeArticles, seedArticles);
	let error = $state('');
	let message = $state('');
	let publishedId = $state('');
	let busyId = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let editingId = $state('');
	let fTitle = $state('');
	let fCategory = $state('Export Basics');
	let fSummary = $state('');
	let fSteps = $state('');
	let fReadTime = $state('5 min');
	let filteredArticles = $derived(
		articles.items.filter(
			(article) =>
				(activeFilter === 'All' || article.category === activeFilter) &&
				[article.title, article.category, article.status, article.summary, ...(article.steps ?? [])].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let publishedCount = $derived(articles.items.filter((article) => article.status === 'Published').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		articles.load();
	});

	async function handlePublish(id?: string) {
		error = '';
		const target = id ? articles.items.find((article) => article.id === id) : (articles.items.find((article) => article.status === 'Draft') ?? articles.items[0]);
		if (!target) return;
		busyId = target.id;
		try {
			const res = await publishKnowledgeArticle(target.id);
			if (res.data) articles.upsert(res.data);
			else articles.upsert({ ...target, status: 'Published' });
			message = `Artikel "${target.title}" dipublikasikan.`;
		} catch {
			error = t('Gagal mempublikasikan artikel.');
		} finally {
			busyId = '';
		}
	}

	function resetForm() {
		editingId = '';
		fTitle = '';
		fCategory = 'Export Basics';
		fSummary = '';
		fSteps = '';
		fReadTime = '5 min';
	}

	function openCreate() {
		resetForm();
		formError = '';
		showForm = true;
	}

	function openEdit(article: { id: string; title: string; category: string; summary?: string; steps?: string[]; readTime?: string }) {
		editingId = article.id;
		fTitle = article.title;
		fCategory = article.category;
		fSummary = article.summary ?? '';
		fSteps = (article.steps ?? []).join('\n');
		fReadTime = article.readTime ?? '5 min';
		formError = '';
		showForm = true;
	}

	async function handleSave() {
		formError = '';
		if (!fTitle.trim()) {
			formError = t('Judul artikel wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload = {
				title: fTitle.trim(),
				category: fCategory,
				summary: fSummary.trim(),
				steps: fSteps.split('\n').map((s) => s.trim()).filter(Boolean),
				readTime: fReadTime.trim() || '5 min'
			};
			if (editingId) {
				const res = await updateKnowledgeArticle(editingId, payload);
				if (res.data) articles.upsert(res.data);
				message = `Artikel "${payload.title}" diperbarui.`;
			} else {
				const res = await createKnowledgeArticle(payload);
				if (res.data) articles.upsert(res.data);
				message = `Artikel "${payload.title}" dibuat.`;
			}
			showForm = false;
			resetForm();
		} catch {
			formError = t('Gagal menyimpan artikel.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete(article: { id: string; title: string }) {
		if (!confirm(`Hapus artikel "${article.title}"?`)) return;
		error = '';
		busyId = article.id;
		try {
			await deleteKnowledgeArticle(article.id);
			articles.remove(article.id);
			message = `Artikel "${article.title}" dihapus.`;
		} catch {
			error = t('Gagal menghapus artikel.');
		} finally {
			busyId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredArticles ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredArticles?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('Basis Pengetahuan')} | MauEkspor</title>
</svelte:head>

<AppShell title="Knowledge Base" eyebrow={t('Export operating playbooks')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Operasi terpandu')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Keep export know-how close to the workflow.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Publish practical playbooks for product readiness, HS review, Incoterms, shipment exceptions, finance, and platform usage.')}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={() => handlePublish()}>{published ? t('Article published') : t('Publish article')}</Button>
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Buat artikel')}</Button>
			<Badge>{t('Published')} {publishedCount}</Badge>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={fTitle} placeholder={t('Contoh: Panduan HS Code')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kategori')}
						<select bind:value={fCategory} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each categories as category}
								<option value={category}>{category}</option>
							{/each}
						</select>
					</label>
				</div>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Ringkasan')}
					<Input bind:value={fSummary} placeholder={t('Ringkasan singkat...')} />
				</label>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Langkah (satu per baris)')}
					<textarea bind:value={fSteps} rows="3" class="rounded-md border bg-background px-3 py-2 text-sm" placeholder={t('Langkah 1\nLangkah 2')}></textarea>
				</label>
				<label class="grid gap-1 text-sm font-semibold">
					{t('Waktu baca')}
					<Input bind:value={fReadTime} placeholder="5 min" />
				</label>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleSave}>{saving ? t('Menyimpan...') : editingId ? t('Simpan perubahan') : t('Simpan artikel')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if articles.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{articles.error}</p>
	{/if}

	{#if published}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Article published.')}</strong>
			<span class="block text-sm text-muted-foreground">{t('Artikel dipublikasikan di backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search article, step, category...')} class="w-[min(390px,100%)]" />
	</div>

	{#if articles.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-24" />
						<Skeleton class="h-5 w-16" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-full" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<div class="mt-3 space-y-1.5 pl-5">
						<Skeleton class="h-4 w-5/6" />
						<Skeleton class="h-4 w-2/3" />
						<Skeleton class="h-4 w-3/4" />
					</div>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as article}
				<Card class="grid gap-4">
					<div class="flex items-center justify-between gap-3">
						<Badge variant={toneVariant(statusTone(article.status))}>{article.status}</Badge>
						<strong class="text-sm font-bold text-muted-foreground">{article.readTime}</strong>
					</div>
					<h3 class="text-2xl font-bold tracking-tight">{article.title}</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">{article.summary}</p>
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Category')}<strong class="mt-1 block text-sm font-bold text-foreground">{article.category}</strong></div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Updated')}<strong class="mt-1 block text-sm font-bold text-foreground">{article.updatedAt}</strong></div>
					</div>
					<ol class="m-0 list-decimal space-y-1.5 pl-5 font-bold text-muted-foreground">
						{#each article.steps as step}<li>{step}</li>{/each}
					</ol>
					<div class="grid grid-cols-3 gap-2">
						{#if article.status !== 'Published'}
							<Button variant="outline" disabled={busyId === article.id} onclick={() => handlePublish(article.id)}>{t('Publish')}</Button>
						{:else}
							<div></div>
						{/if}
						<Button variant="outline" disabled={busyId === article.id} onclick={() => openEdit(article)}>{t('Edit')}</Button>
						<Button variant="outline" class="text-destructive" disabled={busyId === article.id} onclick={() => handleDelete(article)}>{t('Hapus')}</Button>
					</div>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No article matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredArticles?.length ?? 0} />

</AppShell>
