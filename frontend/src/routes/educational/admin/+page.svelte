<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalArticles as seedArticles, educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalModules, publishEducationalModule } from '$lib/api/educational';
	import { listEducationalArticles, publishEducationalArticle } from '$lib/api/educational-articles';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	let modules = createRemoteList(listEducationalModules, seedModules);
	let articles = createRemoteList(listEducationalArticles, seedArticles);
	let modulePublishing = $state('');
	let articlePublishing = $state('');
	let error = $state('');

	$effect(() => {
		modules.load();
		articles.load();
	});

	async function publishModule(id: string) {
		error = '';
		modulePublishing = id;
		try {
			await publishEducationalModule(id);
			const module = modules.items.find((item) => item.id === id);
			if (module) module.status = 'Published';
		} catch {
			error = t('Gagal mempublikasikan modul.');
		} finally {
			modulePublishing = '';
		}
	}

	async function publishArticle(id: string) {
		error = '';
		articlePublishing = id;
		try {
			await publishEducationalArticle(id);
			const article = articles.items.find((item) => item.id === id);
			if (article) article.status = 'Published';
		} catch {
			error = t('Gagal mempublikasikan artikel.');
		} finally {
			articlePublishing = '';
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage_modules = $state(1);
	let paginationPageSize_modules = $state(5);
	let pagedItems_modules = $derived(paginate(modules.items ?? [], paginationPage_modules, paginationPageSize_modules));
	let paginationTotalPages_modules = $derived(calcTotalPages(modules.items?.length ?? 0, paginationPageSize_modules));

	let paginationPage_articles = $state(1);
	let paginationPageSize_articles = $state(5);
	let pagedItems_articles = $derived(paginate(articles.items ?? [], paginationPage_articles, paginationPageSize_articles));
	let paginationTotalPages_articles = $derived(calcTotalPages(articles.items?.length ?? 0, paginationPageSize_articles));

</script>

<svelte:head>
	<title>{t('Admin Edukasi')} | MauEkspor</title>
</svelte:head>

<AppShell title="Educational Admin" eyebrow={t('Content operations')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="outline">{t('Admin')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Moderate modules and articles before publishing.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					{t('Review, publish, and manage the learning content shown to exporters.')}
				</CardDescription>
			</div>
			<div class="flex flex-wrap gap-2.5">
				<Button variant="outline" href="/educational/admin/modules">{t('Modul')}</Button>
				<Button variant="outline" href="/educational/admin/articles">{t('Artikel')}</Button>
				<Button variant="outline" href="/educational">{t('Lihat katalog')}</Button>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>{t('Modul')}</CardTitle>
				<Badge variant="secondary">{modules.items.length} {t('total')}</Badge>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each pagedItems_modules as module}
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<div>
							<strong class="block text-sm font-bold">{module.title}</strong>
							<span class="mt-1 block text-xs font-semibold text-muted-foreground">{module.level} - {module.lessons} {t('pelajaran')}</span>
						</div>
						<div class="grid justify-items-end gap-2">
							<Badge variant={toneVariant(statusTone(module.status))}>{module.status}</Badge>
							<Button size="sm" variant={module.status === 'Published' ? 'outline' : 'default'} disabled={module.status === 'Published' || modulePublishing === module.id} onclick={() => publishModule(module.id)}>{modulePublishing === module.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>{t('Artikel')}</CardTitle>
				<Badge variant="secondary">{articles.items.length} {t('total')}</Badge>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each pagedItems_articles as article}
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<div>
							<strong class="block text-sm font-bold">{article.title}</strong>
							<span class="mt-1 block text-xs font-semibold text-muted-foreground">{article.readMinutes} min read - {article.level}</span>
						</div>
						<div class="grid justify-items-end gap-2">
							<Badge variant={toneVariant(statusTone(article.status))}>{article.status}</Badge>
							<Button variant="ghost" size="sm" disabled={article.status === 'Published' || articlePublishing === article.id} onclick={() => publishArticle(article.id)}>{articlePublishing === article.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>
	</div>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
	<Pagination bind:page={paginationPage_modules} bind:pageSize={paginationPageSize_modules} totalPages={paginationTotalPages_modules} totalItems={modules.items?.length ?? 0} />

	<Pagination bind:page={paginationPage_articles} bind:pageSize={paginationPageSize_articles} totalPages={paginationTotalPages_articles} totalItems={articles.items?.length ?? 0} />

</AppShell>