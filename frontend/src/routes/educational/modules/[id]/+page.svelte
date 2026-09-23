<script lang="ts">
	import { untrack } from 'svelte';
	import { t } from '$lib/i18n.svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';

	import PlayCircleIcon from '@lucide/svelte/icons/play-circle';
	import BookOpenIcon from '@lucide/svelte/icons/book-open';
	import ListChecksIcon from '@lucide/svelte/icons/list-checks';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';
	import CircleIcon from '@lucide/svelte/icons/circle';
	import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import GraduationCapIcon from '@lucide/svelte/icons/graduation-cap';

	let { data } = $props();

	const initialLessons = $state.snapshot(untrack(() => data.lessons));
	let lessons = $state(initialLessons.map((lesson) => ({ ...lesson })));
	let initialIndex = initialLessons.findIndex((lesson) => !lesson.completed);
	let activeIndex = $state(initialIndex === -1 ? 0 : initialIndex);

	let activeLesson = $derived(lessons[activeIndex]);
	let completedCount = $derived(lessons.filter((lesson) => lesson.completed).length);
	let progressPercent = $derived(lessons.length ? Math.round((completedCount / lessons.length) * 100) : 0);

	const kindIcon: Record<string, typeof PlayCircleIcon> = {
		Video: PlayCircleIcon,
		Reading: BookOpenIcon,
		Quiz: ListChecksIcon
	};

	function selectLesson(index: number) {
		activeIndex = index;
	}

	function toggleComplete(index: number) {
		lessons[index].completed = !lessons[index].completed;
	}

	function markCompleteAndNext() {
		lessons[activeIndex].completed = true;
		if (activeIndex < lessons.length - 1) {
			activeIndex += 1;
		}
	}
</script>

<svelte:head>
	<title>{data.module.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.module.title} eyebrow={t('Learning module')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 p-5 shadow-sm sm:p-6">
		<div class="flex flex-wrap items-end justify-between gap-4">
			<div class="min-w-0">
				<div class="flex flex-wrap items-center gap-2">
					<Badge variant="secondary">{data.module.level}</Badge>
					<Badge variant="outline">{data.module.status}</Badge>
				</div>
				<CardTitle class="mt-3 text-2xl font-bold tracking-tight sm:text-3xl">{data.module.title}</CardTitle>
				<p class="mt-2 max-w-2xl text-sm text-muted-foreground">{data.module.summary}</p>
			</div>
			<div class="w-full max-w-xs shrink-0 sm:w-56">
				<div class="flex items-center justify-between text-xs font-bold text-muted-foreground">
					<span>{t('Progres kursus')}</span>
					<span>{progressPercent}%</span>
				</div>
				<Progress value={progressPercent} class="mt-2" />
				<span class="mt-1.5 block text-xs font-semibold text-muted-foreground">{completedCount} {t('dari')} {lessons.length} {t('pelajaran selesai')}</span>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
		<Card class="min-w-0">
			<CardContent class="grid gap-5">
				<div class="grid aspect-video place-items-center rounded-xl border bg-muted/40">
					{#if activeLesson}
						{@const KindIcon = kindIcon[activeLesson.kind] ?? PlayCircleIcon}
						<div class="flex flex-col items-center gap-2 text-muted-foreground">
							<KindIcon class="size-12" />
							<span class="text-xs font-bold uppercase tracking-wide">{activeLesson.kind} - {activeLesson.duration}</span>
						</div>
					{/if}
				</div>

				{#if activeLesson}
					<div>
						<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">
							{t('Pelajaran')} {activeIndex + 1} {t('dari')} {lessons.length}
						</span>
						<h2 class="mt-1 text-xl font-bold tracking-tight sm:text-2xl">{activeLesson.title}</h2>
						<p class="mt-3 leading-relaxed text-muted-foreground">{activeLesson.content}</p>
					</div>

					<div class="rounded-xl border bg-muted/30 p-4">
						<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Poin penting')}</span>
						<ul class="mt-2 grid gap-2">
							{#each activeLesson.keyPoints as point}
								<li class="flex items-start gap-2 text-sm text-foreground">
									<CheckCircle2Icon class="mt-0.5 size-4 shrink-0 text-primary" />
									<span>{point}</span>
								</li>
							{/each}
						</ul>
					</div>

					<div class="flex flex-wrap items-center justify-between gap-3">
						<Button
							variant="outline"
							disabled={activeIndex === 0}
							onclick={() => (activeIndex = Math.max(0, activeIndex - 1))}
						>
							<ChevronLeftIcon class="size-4" />
							{t('Sebelumnya')}
						</Button>
						<div class="flex flex-wrap items-center gap-2.5">
							<Button variant="outline" onclick={() => toggleComplete(activeIndex)}>
								{lessons[activeIndex].completed ? t('Tandai belum selesai') : t('Tandai selesai')}
							</Button>
							<Button onclick={markCompleteAndNext} disabled={activeIndex === lessons.length - 1 && lessons[activeIndex].completed}>
								{activeIndex === lessons.length - 1 ? t('Selesaikan pelajaran') : t('Selesai & lanjut')}
								<ChevronRightIcon class="size-4" />
							</Button>
						</div>
					</div>
				{/if}
			</CardContent>
		</Card>

		<Card class="h-fit lg:sticky lg:top-4">
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle class="text-base">{t('Daftar Pelajaran')}</CardTitle>
				<GraduationCapIcon class="size-4 text-muted-foreground" />
			</CardHeader>
			<CardContent class="grid gap-1.5 p-3 pt-0">
				{#each lessons as lesson, index}
					{@const KindIcon = kindIcon[lesson.kind] ?? PlayCircleIcon}
					<div
						role="button"
						tabindex="0"
						onclick={() => selectLesson(index)}
						onkeydown={(event) => {
							if (event.key === 'Enter' || event.key === ' ') selectLesson(index);
						}}
						class={`flex items-start gap-2.5 rounded-lg p-2.5 text-left transition-colors cursor-pointer ${
							index === activeIndex ? 'bg-primary/10' : 'hover:bg-muted/60'
						}`}
					>
						<button
							type="button"
							onclick={(event) => {
								event.stopPropagation();
								toggleComplete(index);
							}}
							class="mt-0.5 shrink-0"
							aria-label={lesson.completed ? t('Tandai belum selesai') : t('Tandai selesai')}
						>
							{#if lesson.completed}
								<CheckCircle2Icon class="size-4 text-primary" />
							{:else}
								<CircleIcon class="size-4 text-muted-foreground" />
							{/if}
						</button>
						<div class="min-w-0">
							<span class={`block text-sm font-semibold ${index === activeIndex ? 'text-primary' : 'text-foreground'}`}>
								{lesson.title}
							</span>
							<span class="mt-0.5 flex items-center gap-1.5 text-xs text-muted-foreground">
								<KindIcon class="size-3" />
								{lesson.kind} - {lesson.duration}
							</span>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>
	</div>

	<div>
		<Button variant="outline" href="/educational">{t('Kembali ke katalog kursus')}</Button>
	</div>
</AppShell>
