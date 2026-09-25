<script lang="ts">
	import { untrack } from 'svelte';
	import { t } from '$lib/i18n.svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { deleteEducationalModule, getLessonProgress, setLessonComplete } from '$lib/api/educational';
	import { goto } from '$app/navigation';

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
	let deleting = $state(false);
	let error = $state('');

	// Muat progres tersimpan dari backend (per user), lalu sinkronkan ke lessons.
	$effect(() => {
		const moduleId = data.module.id;
		getLessonProgress(moduleId)
			.then((res) => {
				const done = new Set(res.data.completedLessonIds);
				lessons = lessons.map((lesson) => ({ ...lesson, completed: done.has(lesson.id) }));
			})
			.catch(() => { /* progres opsional; biarkan status lokal */ });
	});

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus modul ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteEducationalModule(data.module.id);
			goto('/educational');
		} catch {
			error = t('Gagal menghapus modul.');
		} finally {
			deleting = false;
		}
	}

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
		const next = !lessons[index].completed;
		lessons[index].completed = next;
		persistProgress(lessons[index].id, next);
	}

	function markCompleteAndNext() {
		lessons[activeIndex].completed = true;
		persistProgress(lessons[activeIndex].id, true);
		if (activeIndex < lessons.length - 1) {
			activeIndex += 1;
		}
	}

	async function persistProgress(lessonId: string, completed: boolean) {
		try {
			await setLessonComplete(data.module.id, lessonId, completed);
		} catch {
			error = t('Gagal menyimpan progres belajar.');
		}
	}
</script>

<svelte:head>
	<title>{data.module.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.module.title} eyebrow={t('Learning module')}>
	<Card class="panel-hero p-5 shadow-sm sm:p-6">
		<div class="flex flex-wrap items-end justify-between gap-4">
			<div class="min-w-0">
				<div class="flex flex-wrap items-center gap-2">
					<Badge variant="secondary">{data.module.level}</Badge>
					<Badge variant="outline">{data.module.status}</Badge>
				</div>
				<CardTitle class="mt-3 font-display text-3xl font-black tracking-tight text-[#0b1d3a] sm:text-4xl dark:text-white">{data.module.title}</CardTitle>
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
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if error}
			<p class="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}
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
