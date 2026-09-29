<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { educationalArticles as seedArticles, educationalModules as seedModules, educationalLessons } from '$lib/data/trade';
	import { listEducationalModules } from '$lib/api/educational';
	import { listEducationalArticles } from '$lib/api/educational-articles';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	import GraduationCapIcon from '@lucide/svelte/icons/graduation-cap';
	import BookOpenIcon from '@lucide/svelte/icons/book-open';
	import PlayCircleIcon from '@lucide/svelte/icons/play-circle';
	import ListChecksIcon from '@lucide/svelte/icons/list-checks';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const levelFilters = ['All', 'Beginner', 'Intermediate', 'Advanced'];

	function trLevel(x: string) {
		return t(x === 'All' ? 'Semua' : x === 'Beginner' ? 'Pemula' : x === 'Intermediate' ? 'Menengah' : 'Lanjutan');
	}

	function trStatus(s: string) {
		return t(s === 'Published' ? 'Diterbitkan' : s === 'In Progress' ? 'Sedang berjalan' : 'Draf');
	}
	let levelFilter = $state('All');
	let query = $state('');

	let modules = createRemoteList(listEducationalModules, seedModules);
	let articles = createRemoteList(listEducationalArticles, seedArticles);
	$effect(() => {
		modules.load();
		articles.load();
	});

	let filteredModules = $derived(
		modules.items.filter((module) => {
			const matchesLevel = levelFilter === 'All' || module.level === levelFilter;
			const matchesQuery = [module.title, module.level, module.status, module.summary]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesLevel && matchesQuery;
		})
	);

	function getLessonCount(module: any) {
		if (module.lessonCount && typeof module.lessonCount === 'number') return module.lessonCount;
		if (module.lessonsList?.length) return module.lessonsList.length;
		if (typeof module.lessons === 'number' && module.lessons > 0) return module.lessons;
		const local = educationalLessons.filter((lesson) => lesson.moduleId === module.id).length;
		return local > 0 ? local : 4;
	}

	function hasQuiz(module: any) {
		if (module.quizCount && module.quizCount > 0) return true;
		if (module.lessonsList?.some((l: any) => l.kind === 'Quiz' || l.quizQuestions?.length)) return true;
		return educationalLessons.some((l) => l.moduleId === module.id && (l.kind === 'Quiz' || l.quizQuestions?.length));
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredModules ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredModules?.length ?? 0, paginationPageSize));

	let paginationPage_articles = $state(1);
	let paginationPageSize_articles = $state(5);
	let filteredArticles = $derived(
		articles.items.filter((article) => {
			const matchesLevel = levelFilter === 'All' || article.level === levelFilter;
			const matchesQuery = [article.title, article.level, article.status, article.summary]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesLevel && matchesQuery;
		})
	);
	let pagedItems_articles = $derived(paginate(filteredArticles ?? [], paginationPage_articles, paginationPageSize_articles));
	let paginationTotalPages_articles = $derived(calcTotalPages(filteredArticles?.length ?? 0, paginationPageSize_articles));

</script>

<svelte:head>
	<title>{t('Edukasi')} | MauEkspor</title>
</svelte:head>

<AppShell title="Educational" eyebrow={t('Platform belajar ekspor')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">
					<GraduationCapIcon class="size-3.5" />
					{t('Jalur belajar')}
				</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Belajar proses ekspor sambil Anda mengirim.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					{t('Kursus singkat dan artikel yang memetakan langsung ke alur kerja di workspace ini.')}
				</CardDescription>
			</div>
			<Button href="/educational/admin">{t('Kelola modul')}</Button>
		</div>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-card p-4">
		<div class="flex flex-wrap gap-2">
			{#each levelFilters as filter}
				<Button
					variant={levelFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => (levelFilter = filter)}
				>
					{trLevel(filter)}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari modul atau artikel...')} class="max-w-xs" />
	</div>

	{#if modules.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{modules.error}</p>
	{/if}

	{#if modules.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-7 w-12" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-full" />
					<div class="mt-4 grid gap-2.5 sm:grid-cols-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<Skeleton class="mt-4 h-2 w-full" />
					<Skeleton class="mt-4 h-5 w-32" />
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as module}
				<a href={`/educational/modules/${module.id}`} class="block no-underline">
					<Card class="grid h-full gap-3 p-5 shadow-sm transition-transform hover:-translate-y-1">
						<div class="flex items-center justify-between gap-2">
							<div class="flex items-center gap-1.5 flex-wrap">
								<Badge variant={toneVariant(statusTone(module.status))}>{trStatus(module.status)}</Badge>
								{#if hasQuiz(module)}
									<Badge variant="outline" class="border-emerald-500/30 bg-emerald-50 text-emerald-700 text-[10px] dark:bg-emerald-950/40 dark:text-emerald-300">
										<ListChecksIcon class="size-3 mr-0.5" />
										{t('Ada Kuis')}
									</Badge>
								{/if}
							</div>
							<strong class="text-2xl font-bold tracking-tight">{module.completion}%</strong>
						</div>
						<h3 class="text-xl font-bold tracking-tight">{module.title}</h3>
						<p class="text-sm leading-relaxed text-muted-foreground">{module.summary}</p>
						<div class="grid gap-2.5 sm:grid-cols-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Level')} <strong class="mt-1 block text-sm font-bold text-foreground">{module.level}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Pelajaran & Kuis')} <strong class="mt-1 block text-sm font-bold text-foreground">{getLessonCount(module)} {t('materi')}</strong>
							</div>
						</div>
						<Progress value={module.completion} />
						<span class="inline-flex items-center gap-1.5 text-sm font-bold text-primary">
							<PlayCircleIcon class="size-4" />
							{module.completion > 0 ? t('Lanjutkan belajar') : t('Mulai belajar')}
						</span>
					</Card>
				</a>
			{:else}
				<div class="grid place-items-center rounded-xl border border-dashed bg-muted/20 p-10 text-sm font-semibold text-muted-foreground md:col-span-2 xl:col-span-3">
					{t('Tidak ada modul yang cocok dengan filter.')}
				</div>
			{/each}
		</div>

		<div class="mt-4">
			<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredModules?.length ?? 0} />
		</div>
	{/if}

	{#if articles.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{articles.error}</p>
	{/if}

	<Card class="mt-6 shadow-sm">
		<CardHeader class="flex-row items-center justify-between gap-3 border-b pb-4">
			<CardTitle class="flex items-center gap-2 text-lg">
				<BookOpenIcon class="size-4 text-primary" />
				{t('Artikel & Panduan Ekspor')}
			</CardTitle>
			<Badge variant="secondary">{articles.items.length} {t('diterbitkan')}</Badge>
		</CardHeader>
		<CardContent class="grid gap-2 pt-4">
			{#if articles.loading}
				{#each Array(4) as _}
					<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5">
						<div class="min-w-0 flex-1">
							<Skeleton class="h-5 w-3/4" />
							<Skeleton class="mt-2 h-4 w-1/2" />
						</div>
						<div class="grid justify-items-end gap-1.5">
							<Skeleton class="h-5 w-16 rounded-full" />
							<Skeleton class="h-4 w-14" />
						</div>
					</div>
				{/each}
			{:else}
				{#each pagedItems_articles as article}
					<a class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5 no-underline transition-colors hover:bg-muted/60" href={`/educational/articles/${article.id}`}>
						<div>
							<strong class="block text-sm font-bold">{article.title}</strong>
							<span class="mt-1 block text-xs font-semibold text-muted-foreground">{article.summary}</span>
						</div>
						<div class="grid justify-items-end gap-1.5">
							<Badge variant={toneVariant(statusTone(article.status))}>{trStatus(article.status)}</Badge>
							<small class="text-xs font-semibold text-muted-foreground">{article.readMinutes} {t('menit baca')}</small>
						</div>
					</a>
				{/each}
			{/if}
		</CardContent>

		{#if (filteredArticles?.length ?? 0) > 0}
			<div class="border-t p-3.5">
				<Pagination bind:page={paginationPage_articles} bind:pageSize={paginationPageSize_articles} totalPages={paginationTotalPages_articles} totalItems={filteredArticles?.length ?? 0} />
			</div>
		{/if}
	</Card>
</AppShell>