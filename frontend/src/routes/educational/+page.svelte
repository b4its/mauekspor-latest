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
	import { statusTone } from '$lib/utils/format';

	import GraduationCapIcon from '@lucide/svelte/icons/graduation-cap';
	import BookOpenIcon from '@lucide/svelte/icons/book-open';
	import PlayCircleIcon from '@lucide/svelte/icons/play-circle';

	const levelFilters = ['All', 'Beginner', 'Intermediate', 'Advanced'];
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

	function lessonCount(moduleId: string) {
		return educationalLessons.filter((lesson) => lesson.moduleId === moduleId).length;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Educational | MauEkspor</title>
</svelte:head>

<AppShell title="Educational" eyebrow="Export learning platform">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">
					<GraduationCapIcon class="size-3.5" />
					Learning path
				</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Belajar proses ekspor sambil Anda mengirim.
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					Kursus singkat dan artikel yang memetakan langsung ke alur kerja di workspace ini.
				</CardDescription>
			</div>
			<Button href="/educational/admin">Kelola modul</Button>
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
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Cari modul atau artikel..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredModules as module}
			<a href={`/educational/modules/${module.id}`} class="block no-underline">
				<Card class="grid h-full gap-3 p-5 shadow-sm transition-transform hover:-translate-y-1">
					<div class="flex items-center justify-between gap-2">
						<Badge variant={toneVariant(statusTone(module.status))}>{module.status}</Badge>
						<strong class="text-2xl font-bold tracking-tight">{module.completion}%</strong>
					</div>
					<h3 class="text-xl font-bold tracking-tight">{module.title}</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">{module.summary}</p>
					<div class="grid gap-2.5 sm:grid-cols-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Level <strong class="mt-1 block text-sm font-bold text-foreground">{module.level}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							Pelajaran <strong class="mt-1 block text-sm font-bold text-foreground">{lessonCount(module.id)}</strong>
						</div>
					</div>
					<Progress value={module.completion} />
					<span class="inline-flex items-center gap-1.5 text-sm font-bold text-primary">
						<PlayCircleIcon class="size-4" />
						{module.completion > 0 ? 'Lanjutkan belajar' : 'Mulai belajar'}
					</span>
				</Card>
			</a>
		{:else}
			<div class="grid place-items-center rounded-xl border border-dashed bg-muted/20 p-10 text-sm font-semibold text-muted-foreground md:col-span-2 xl:col-span-3">
				No module matched your filter.
			</div>
		{/each}
	</div>

	<Card class="mt-4">
		<CardHeader class="flex-row items-center justify-between gap-3">
			<CardTitle class="flex items-center gap-2">
				<BookOpenIcon class="size-4 text-muted-foreground" />
				Artikel
			</CardTitle>
			<Badge variant="secondary">{articles.items.length} published</Badge>
		</CardHeader>
		<CardContent class="grid gap-2">
			{#each articles.items as article}
				<a class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5 no-underline transition-colors hover:bg-muted/60" href={`/educational/articles/${article.id}`}>
					<div>
						<strong class="block text-sm font-bold">{article.title}</strong>
						<span class="mt-1 block text-xs font-semibold text-muted-foreground">{article.summary}</span>
					</div>
					<div class="grid justify-items-end gap-1.5">
						<Badge variant={toneVariant(statusTone(article.status))}>{article.status}</Badge>
						<small class="text-xs font-semibold text-muted-foreground">{article.readMinutes} min read</small>
					</div>
				</a>
			{/each}
		</CardContent>
	</Card>
</AppShell>