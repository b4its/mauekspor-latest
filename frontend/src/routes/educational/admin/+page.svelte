<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalArticles as seedArticles, educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalModules, publishEducationalModule } from '$lib/api/educational';
	import { listEducationalArticles, publishEducationalArticle } from '$lib/api/educational-articles';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { label } from '$lib/utils/labels';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';
	import { page } from '$app/state';
	import { syncFiltersToUrl } from '$lib/utils/urlFilters';

	let modules = createRemoteList(listEducationalModules, seedModules);
	let articles = createRemoteList(listEducationalArticles, seedArticles);
	let modulePublishing = $state('');
	let articlePublishing = $state('');
	let error = $state('');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let statusFilter = $state(page.url.searchParams.get('status') ?? 'All');
	const statusFilters = ['All', 'Published', 'Draft'];

	let filteredModules = $derived(
		modules.items.filter(
			(module) =>
				(statusFilter === 'All' || module.status === statusFilter) &&
				[module.title, module.level, module.summary].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let filteredArticles = $derived(
		articles.items.filter(
			(article) =>
				(statusFilter === 'All' || article.status === statusFilter) &&
				[article.title, article.level, article.summary].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);

	// Simpan pencarian & filter ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: statusFilter === 'All' ? '' : statusFilter };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '' }, ['query', 'status']), 250);
		return () => clearTimeout(syncTimer);
	});

	$effect(() => {
		modules.load();
		articles.load();
	});

	async function publishModule(id: string) {
		error = '';
		modulePublishing = id;
		try {
			const res = await publishEducationalModule(id);
			if (res.data) {
				modules.upsert(res.data);
			} else {
				const module = modules.items.find((item) => item.id === id);
				if (module) modules.upsert({ ...module, status: 'Published' });
			}
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
			const res = await publishEducationalArticle(id);
			if (res.data) {
				articles.upsert(res.data);
			} else {
				const article = articles.items.find((item) => item.id === id);
				if (article) articles.upsert({ ...article, status: 'Published' });
			}
		} catch {
			error = t('Gagal mempublikasikan artikel.');
		} finally {
			articlePublishing = '';
		}
	}

	let paginationPage_modules = $state(1);
	let paginationPageSize_modules = $state(5);
	let pagedItems_modules = $derived(paginate(filteredModules ?? [], paginationPage_modules, paginationPageSize_modules));
	let paginationTotalPages_modules = $derived(calcTotalPages(filteredModules?.length ?? 0, paginationPageSize_modules));

	let paginationPage_articles = $state(1);
	let paginationPageSize_articles = $state(5);
	let pagedItems_articles = $derived(paginate(filteredArticles ?? [], paginationPage_articles, paginationPageSize_articles));
	let paginationTotalPages_articles = $derived(calcTotalPages(filteredArticles?.length ?? 0, paginationPageSize_articles));

	// Reset ke halaman pertama saat pencarian/filter berubah.
	$effect(() => {
		query;
		statusFilter;
		paginationPage_modules = 1;
		paginationPage_articles = 1;
	});

</script>

<svelte:head>
	<title>{t('Admin Edukasi')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Educational Admin')} eyebrow={t('Content operations')}>
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

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each statusFilters as filter}
				<Button variant={statusFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (statusFilter = filter)}>{filter === 'All' ? t('Semua') : label(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search"
			aria-label={t('Cari modul atau artikel...')} placeholder={t('Cari modul atau artikel...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>{t('Modul')}</CardTitle>
				<Badge variant="secondary">{filteredModules.length} {t('total')}</Badge>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#if modules.loading}
					{#each Array(4) as _}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
							<div class="grid gap-2">
								<Skeleton class="h-4 w-40" />
								<Skeleton class="h-3 w-24" />
							</div>
							<Skeleton class="h-8 w-20" />
						</div>
					{/each}
				{:else}
					{#each pagedItems_modules as module}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
							<div>
								<strong class="block text-sm font-bold">{module.title}</strong>
								<span class="mt-1 block text-xs font-semibold text-muted-foreground">{module.level} - {module.lessons} {t('pelajaran')}</span>
							</div>
							<div class="grid justify-items-end gap-2">
								<Badge variant={toneVariant(statusTone(module.status))}>{label(module.status)}</Badge>
								<Button size="sm" variant={module.status === 'Published' ? 'outline' : 'default'} disabled={module.status === 'Published' || modulePublishing === module.id} onclick={() => publishModule(module.id)}>{modulePublishing === module.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
							</div>
						</div>
					{:else}
						<p class="text-sm text-muted-foreground">{t('Belum ada modul.')}</p>
					{/each}
				{/if}
			</CardContent>
			<CardContent class="p-0">
				<Pagination bind:page={paginationPage_modules} bind:pageSize={paginationPageSize_modules} totalPages={paginationTotalPages_modules} totalItems={filteredModules?.length ?? 0} />
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>{t('Artikel')}</CardTitle>
				<Badge variant="secondary">{filteredArticles.length} {t('total')}</Badge>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#if articles.loading}
					{#each Array(4) as _}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
							<div class="grid gap-2">
								<Skeleton class="h-4 w-40" />
								<Skeleton class="h-3 w-24" />
							</div>
							<Skeleton class="h-8 w-20" />
						</div>
					{/each}
				{:else}
					{#each pagedItems_articles as article}
						<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
							<div>
								<strong class="block text-sm font-bold">{article.title}</strong>
								<span class="mt-1 block text-xs font-semibold text-muted-foreground">{article.readMinutes} {t('min read')} - {article.level}</span>
							</div>
							<div class="grid justify-items-end gap-2">
								<Badge variant={toneVariant(statusTone(article.status))}>{label(article.status)}</Badge>
								<Button variant="ghost" size="sm" disabled={article.status === 'Published' || articlePublishing === article.id} onclick={() => publishArticle(article.id)}>{articlePublishing === article.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
							</div>
						</div>
					{:else}
						<p class="text-sm text-muted-foreground">{t('Belum ada artikel.')}</p>
					{/each}
				{/if}
			</CardContent>
			<CardContent class="p-0">
				<Pagination bind:page={paginationPage_articles} bind:pageSize={paginationPageSize_articles} totalPages={paginationTotalPages_articles} totalItems={filteredArticles?.length ?? 0} />
			</CardContent>
		</Card>
	</div>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{error}</p>{/if}

</AppShell>