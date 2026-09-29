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
	import RotateCcwIcon from '@lucide/svelte/icons/rotate-ccw';
	import TrophyIcon from '@lucide/svelte/icons/trophy';
	import AlertCircleIcon from '@lucide/svelte/icons/alert-circle';
	import XIcon from '@lucide/svelte/icons/x';
	import CheckIcon from '@lucide/svelte/icons/check';
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
	import VideoIcon from '@lucide/svelte/icons/video';
	import { educationalLessons } from '$lib/data/trade';

	let { data } = $props();

	const TOPIC_YOUTUBE_VIDEOS: Record<string, { url: string; title: string }> = {
		'EDU-START': {
			url: 'https://www.youtube.com/watch?v=C7VLuiVPIQM',
			title: 'PPEJP Kemendag: Desain Kemasan & Paspor Ekspor'
		},
		'EDU-COMPLIANCE': {
			url: 'https://www.youtube.com/watch?v=-I2EJ5MUVkY',
			title: 'EU CBAM 2026: Regulatory Guidance & Compliance'
		},
		'EDU-COSTING': {
			url: 'https://www.youtube.com/watch?v=7g7IC4IzjDM',
			title: 'Incoterms 2020 & Container Shipping Explained'
		},
		'EDU-TARIFFS-2026': {
			url: 'https://www.youtube.com/watch?v=S0T09u1T8kY',
			title: 'Bank Indonesia: Tutorial Pelaporan DHE SDA pada SiMoDIS'
		},
		'EDU-DES-PANEN-01': {
			url: 'https://www.youtube.com/watch?v=JnMtuZTjV6Q',
			title: 'Badan Karantina Indonesia: Karantina Tumbuhan & Ekspor Pertanian'
		},
		'EDU-DES-HALAL-02': {
			url: 'https://www.youtube.com/watch?v=UaPPWKAYj7E',
			title: 'BPJPH Kemenag: Tutorial SIHALAL Sertifikasi Halal'
		},
		'EDU-DES-KEMAS-03': {
			url: 'https://www.youtube.com/watch?v=tK-V0wXk-V0',
			title: 'Barantin: Standar Instalasi Kemasan Kayu ISPM 15 & Fumigasi'
		},
		'EDU-DES-NIB-04': {
			url: 'https://www.youtube.com/watch?v=3-1hUZ6EZn0',
			title: 'Kementerian Investasi / BKPM: Tutorial NIB Ekspor via OSS RBA'
		},
		'EDU-DES-DOC-05': {
			url: 'https://www.youtube.com/watch?v=7g7IC4IzjDM',
			title: 'Dokumen Ekspor & Container Logistics'
		},
		'EDU-DES-KARANTINA-06': {
			url: 'https://www.youtube.com/watch?v=JnMtuZTjV6Q',
			title: 'Badan Karantina Indonesia: Kuliah Karantina & Persyaratan Ekspor'
		},
		'EDU-DES-CITES-07': {
			url: 'https://www.youtube.com/watch?v=tK-V0wXk-V0',
			title: 'Kepatuhan Legalitas Kayu SVLK & Kemasan ISPM 15'
		}
	};

	function resolveVideoUrl(lesson: any): string | null {
		if (lesson?.videoUrl && typeof lesson.videoUrl === 'string' && lesson.videoUrl.trim()) {
			return lesson.videoUrl.trim();
		}
		if (lesson?.video_url && typeof lesson.video_url === 'string' && lesson.video_url.trim()) {
			return lesson.video_url.trim();
		}

		// Cek master trade data berdasarkan id
		const master = educationalLessons.find((l) => l.id === lesson?.id);
		if (master?.videoUrl) return master.videoUrl;

		// Cek berdasarkan moduleId
		const modId = lesson?.moduleId || data?.module?.id;
		if (modId && TOPIC_YOUTUBE_VIDEOS[modId]) {
			return TOPIC_YOUTUBE_VIDEOS[modId].url;
		}

		// Cek pencocokan semantik dari judul atau konten jika bertipe Video
		const text = `${lesson?.title || ''} ${lesson?.content || ''} ${data?.module?.title || ''}`.toLowerCase();
		if (text.includes('karantina') || text.includes('phytosanitary') || text.includes('hama') || text.includes('panen')) {
			return 'https://www.youtube.com/watch?v=JnMtuZTjV6Q';
		}
		if (text.includes('halal') || text.includes('sihalal') || text.includes('bpjph')) {
			return 'https://www.youtube.com/watch?v=UaPPWKAYj7E';
		}
		if (text.includes('kemas') || text.includes('ispm') || text.includes('fumigasi') || text.includes('palet') || text.includes('rotan')) {
			return 'https://www.youtube.com/watch?v=tK-V0wXk-V0';
		}
		if (text.includes('nib') || text.includes('oss') || text.includes('kbli') || text.includes('iumk')) {
			return 'https://www.youtube.com/watch?v=3-1hUZ6EZn0';
		}
		if (text.includes('dhe') || text.includes('simodis') || text.includes('devisa')) {
			return 'https://www.youtube.com/watch?v=S0T09u1T8kY';
		}
		if (text.includes('incoterm') || text.includes('fob') || text.includes('cif') || text.includes('kontainer') || text.includes('forwarder')) {
			return 'https://www.youtube.com/watch?v=7g7IC4IzjDM';
		}
		if (text.includes('cbam') || text.includes('eudr') || text.includes('eropa')) {
			return 'https://www.youtube.com/watch?v=-I2EJ5MUVkY';
		}
		return 'https://www.youtube.com/watch?v=C7VLuiVPIQM';
	}

	function getYouTubeEmbedUrl(url?: string | null): string | null {
		if (!url) return null;
		const trimmed = url.trim();
		if (!trimmed) return null;
		if (/^[a-zA-Z0-9_-]{11}$/.test(trimmed)) {
			return `https://www.youtube-nocookie.com/embed/${trimmed}?rel=0&modestbranding=1`;
		}
		const match = trimmed.match(/(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})/);
		return match ? `https://www.youtube-nocookie.com/embed/${match[1]}?rel=0&modestbranding=1` : null;
	}

	const initialLessons = $state.snapshot(untrack(() => data.lessons));
	let lessons = $state(initialLessons.map((lesson) => ({ ...lesson })));
	let initialIndex = initialLessons.findIndex((lesson) => !lesson.completed);
	let activeIndex = $state(initialIndex === -1 ? 0 : initialIndex);
	let deleting = $state(false);
	let error = $state('');

	// State kuis interaktif
	let userAnswers = $state<Record<number, number>>({});
	let quizSubmitted = $state(false);
	let quizScore = $state<number | null>(null);

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

	function getLessonQuestions(lesson: any) {
		if (lesson?.quizQuestions && Array.isArray(lesson.quizQuestions) && lesson.quizQuestions.length > 0) {
			return lesson.quizQuestions;
		}
		const seed = educationalLessons.find((l) => l.id === lesson?.id);
		if (seed?.quizQuestions?.length) {
			return seed.quizQuestions;
		}
		return [];
	}

	function selectLesson(index: number) {
		activeIndex = index;
		userAnswers = {};
		quizSubmitted = false;
		quizScore = null;
	}

	function handleSelectOption(qIdx: number, optIdx: number) {
		if (quizSubmitted) return;
		userAnswers[qIdx] = optIdx;
	}

	function submitQuiz(questions: any[]) {
		if (!questions || questions.length === 0) return;
		let correctCount = 0;
		for (let i = 0; i < questions.length; i++) {
			if (userAnswers[i] === questions[i].correctIndex) {
				correctCount++;
			}
		}
		const score = Math.round((correctCount / questions.length) * 100);
		quizScore = score;
		quizSubmitted = true;
		if (score >= 70) {
			lessons[activeIndex].completed = true;
			persistProgress(lessons[activeIndex].id, true);
		}
	}

	function resetQuiz() {
		userAnswers = {};
		quizSubmitted = false;
		quizScore = null;
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
			selectLesson(activeIndex + 1);
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
				{#if activeLesson}
					{@const questions = getLessonQuestions(activeLesson)}
					{#if activeLesson.kind === 'Quiz' || questions.length > 0}
						<!-- KUIS INTERAKTIF -->
						<div class="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 sm:p-6">
							<div class="flex flex-wrap items-center justify-between gap-3 border-b border-border/40 pb-4">
								<div class="flex items-center gap-2">
									<Badge class="bg-emerald-600 text-white hover:bg-emerald-700">
										<ListChecksIcon class="size-3.5 mr-1" />
										{t('Kuis Pemahaman Modul')}
									</Badge>
									<Badge variant="outline">{questions.length} {t('Pertanyaan')}</Badge>
								</div>
								{#if quizSubmitted && quizScore !== null}
									<Badge class={quizScore >= 70 ? 'bg-emerald-600 text-white' : 'bg-destructive text-destructive-foreground'}>
										{quizScore >= 70 ? t('LULUS') : t('BELUM LULUS')} - {quizScore}%
									</Badge>
								{/if}
							</div>

							<div class="mt-4">
								<h2 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">{activeLesson.title}</h2>
								<p class="mt-2 text-sm text-muted-foreground">{activeLesson.content}</p>
							</div>

							<!-- Hasil Evaluasi / Skor Kuis -->
							{#if quizSubmitted && quizScore !== null}
								<div class={`mt-5 rounded-xl border p-4 ${quizScore >= 70 ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-950 dark:text-emerald-200' : 'border-destructive/40 bg-destructive/10 text-destructive'}`}>
									<div class="flex items-start gap-3">
										{#if quizScore >= 70}
											<TrophyIcon class="size-6 shrink-0 text-emerald-600 dark:text-emerald-400 mt-0.5" />
											<div>
												<strong class="block font-bold text-base">{t('Selamat! Anda Telah Lulus Kuis Ini')} 🎉</strong>
												<p class="mt-1 text-sm leading-relaxed">
													{t('Skor Anda:')} <span class="font-bold">{quizScore}%</span> ({Object.keys(userAnswers).filter(k => userAnswers[Number(k)] === questions[Number(k)]?.correctIndex).length} {t('dari')} {questions.length} {t('jawaban benar')}). {t('Kepatuhan pemahaman materi ini telah tersimpan dalam progres belajar Anda.')}
												</p>
											</div>
										{:else}
											<AlertCircleIcon class="size-6 shrink-0 text-destructive mt-0.5" />
											<div>
												<strong class="block font-bold text-base">{t('Belum Mencapai Nilai Kelulusan')}</strong>
												<p class="mt-1 text-sm leading-relaxed">
													{t('Skor Anda:')} <span class="font-bold">{quizScore}%</span> ({t('minimal kelulusan')} 70%). {t('Silakan pelajari pembahasan kunci jawaban di bawah dan coba kerjakan ulang kuis.')}
												</p>
											</div>
										{/if}
									</div>
								</div>
							{/if}

							<!-- Daftar Pertanyaan -->
							<div class="mt-6 space-y-6">
								{#each questions as q, qIdx}
									{@const userAnswer = userAnswers[qIdx]}
									{@const isAnswered = userAnswer !== undefined}
									{@const isCorrect = isAnswered && userAnswer === q.correctIndex}
									<div class={`rounded-xl border p-4 sm:p-5 transition-colors ${quizSubmitted ? (isCorrect ? 'border-emerald-500/40 bg-card shadow-xs' : 'border-destructive/40 bg-card shadow-xs') : 'border-border bg-card'}`}>
										<div class="flex items-start justify-between gap-3">
											<span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
												{t('Pertanyaan')} {qIdx + 1} {t('dari')} {questions.length}
											</span>
											{#if quizSubmitted}
												{#if isCorrect}
													<span class="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400">
														<CheckCircle2Icon class="size-4" /> {t('Benar')}
													</span>
												{:else}
													<span class="inline-flex items-center gap-1 text-xs font-bold text-destructive">
														<XIcon class="size-4" /> {t('Salah')}
													</span>
												{/if}
											{/if}
										</div>
										<h3 class="mt-2 text-base font-bold text-foreground leading-snug sm:text-lg">{q.question}</h3>

										<!-- Pilihan Jawaban -->
										<div class="mt-4 grid gap-2.5">
											{#each q.options as opt, optIdx}
												{@const isSelected = userAnswer === optIdx}
												{@const isOptionCorrect = q.correctIndex === optIdx}
												{@const letter = String.fromCharCode(65 + optIdx)}

												<button
													type="button"
													disabled={quizSubmitted}
													onclick={() => handleSelectOption(qIdx, optIdx)}
													class={`flex items-start gap-3 w-full rounded-lg border p-3 text-left transition-all text-sm font-medium ${
														quizSubmitted
															? isOptionCorrect
																? 'border-emerald-500 bg-emerald-500/15 text-emerald-950 dark:text-emerald-100 font-semibold ring-1 ring-emerald-500'
																: isSelected
																	? 'border-destructive bg-destructive/15 text-destructive font-semibold ring-1 ring-destructive'
																	: 'border-border/50 opacity-60 text-muted-foreground'
															: isSelected
																? 'border-primary bg-primary/10 text-primary font-semibold ring-1 ring-primary'
																: 'border-border bg-muted/20 hover:bg-muted/50 text-foreground'
													}`}
												>
													<span class={`grid size-6 shrink-0 place-items-center rounded-full text-xs font-bold ${
														quizSubmitted
															? isOptionCorrect
																? 'bg-emerald-600 text-white'
																: isSelected
																	? 'bg-destructive text-white'
																	: 'bg-muted text-muted-foreground'
															: isSelected
																? 'bg-primary text-primary-foreground'
																: 'bg-muted/80 text-foreground'
													}`}>
														{letter}
													</span>
													<span class="flex-1 leading-relaxed">{opt}</span>
													{#if quizSubmitted && isOptionCorrect}
														<Badge variant="outline" class="shrink-0 border-emerald-500/50 bg-emerald-50 text-[10px] text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
															{t('Kunci Benar')}
														</Badge>
													{/if}
												</button>
											{/each}
										</div>

										<!-- Pembahasan Regulasi / Penjelasan -->
										{#if quizSubmitted && q.explanation}
											<div class="mt-3.5 rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs leading-relaxed text-foreground/90">
												<strong class="font-bold text-primary block mb-0.5">💡 {t('Pembahasan & Rujukan Regulasi:')}</strong>
												{q.explanation}
											</div>
										{/if}
									</div>
								{/each}
							</div>

							<!-- Tombol Aksi Kuis -->
							<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-border/40 pt-4">
								<Button
									variant="outline"
									disabled={activeIndex === 0}
									onclick={() => (activeIndex = Math.max(0, activeIndex - 1))}
								>
									<ChevronLeftIcon class="size-4 mr-1" />
									{t('Sebelumnya')}
								</Button>

								<div class="flex flex-wrap items-center gap-2.5">
									{#if !quizSubmitted}
										<Button
											class="bg-emerald-600 hover:bg-emerald-700 text-white"
											onclick={() => submitQuiz(questions)}
											disabled={Object.keys(userAnswers).length < questions.length}
										>
											<ListChecksIcon class="size-4 mr-1.5" />
											{t('Kirim Jawaban & Periksa Skor')}
										</Button>
									{:else}
										<Button variant="outline" onclick={resetQuiz}>
											<RotateCcwIcon class="size-4 mr-1.5" />
											{t('Ulangi Kuis')}
										</Button>
										{#if activeIndex < lessons.length - 1}
											<Button onclick={markCompleteAndNext}>
												{t('Pelajaran Berikutnya')}
												<ChevronRightIcon class="size-4 ml-1" />
											</Button>
										{/if}
									{/if}
								</div>
							</div>
						</div>
					{:else}
						{@const KindIcon = kindIcon[activeLesson.kind] ?? PlayCircleIcon}
						{@const resolvedVideoUrl = activeLesson.kind === 'Video' ? resolveVideoUrl(activeLesson) : null}
						{@const ytEmbedUrl = resolvedVideoUrl ? getYouTubeEmbedUrl(resolvedVideoUrl) : null}

						{#if ytEmbedUrl}
							<!-- VIDEO PEMBELAJARAN YOUTUBE (INTERAKTIF & RESPONSIF) -->
							<div class="space-y-2.5">
								<div class="relative aspect-video w-full overflow-hidden rounded-2xl border bg-black shadow-md">
									<iframe
										src={ytEmbedUrl}
										title={activeLesson.title}
										class="absolute inset-0 size-full"
										frameborder="0"
										allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
										allowfullscreen
									></iframe>
								</div>
								<div class="flex flex-wrap items-center justify-between gap-2 px-1 text-xs text-muted-foreground">
									<div class="flex items-center gap-1.5 font-semibold text-rose-600 dark:text-rose-400">
										<VideoIcon class="size-4" />
										<span>{t('Video Pembelajaran YouTube Resmi')}</span>
									</div>
									{#if resolvedVideoUrl}
										<a
											href={resolvedVideoUrl}
											target="_blank"
											rel="noopener noreferrer"
											class="inline-flex items-center gap-1 font-medium underline hover:text-foreground"
										>
											<span>{t('Buka di YouTube')}</span>
											<ExternalLinkIcon class="size-3" />
										</a>
									{/if}
								</div>
							</div>
						{:else}
							<!-- MATERI PEMBELAJARAN (READING / PLACEHOLDER) -->
							<div class="grid aspect-video place-items-center rounded-xl border bg-muted/40">
								<div class="flex flex-col items-center gap-2 text-muted-foreground">
									<KindIcon class="size-12" />
									<span class="text-xs font-bold uppercase tracking-wide">{activeLesson.kind} - {activeLesson.duration}</span>
								</div>
							</div>
						{/if}

						<div>
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">
								{t('Pelajaran')} {activeIndex + 1} {t('dari')} {lessons.length}
							</span>
							<h2 class="mt-1 text-xl font-bold tracking-tight sm:text-2xl">{activeLesson.title}</h2>
							<p class="mt-3 leading-relaxed text-muted-foreground whitespace-pre-line">{activeLesson.content}</p>
						</div>

						{#if activeLesson.keyPoints && activeLesson.keyPoints.length > 0}
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
						{/if}

						<div class="flex flex-wrap items-center justify-between gap-3">
							<Button
								variant="outline"
								disabled={activeIndex === 0}
								onclick={() => (activeIndex = Math.max(0, activeIndex - 1))}
							>
								<ChevronLeftIcon class="size-4 mr-1" />
								{t('Sebelumnya')}
							</Button>
							<div class="flex flex-wrap items-center gap-2.5">
								<Button variant="outline" onclick={() => toggleComplete(activeIndex)}>
									{lessons[activeIndex].completed ? t('Tandai belum selesai') : t('Tandai selesai')}
								</Button>
								<Button onclick={markCompleteAndNext} disabled={activeIndex === lessons.length - 1 && lessons[activeIndex].completed}>
									{activeIndex === lessons.length - 1 ? t('Selesaikan pelajaran') : t('Selesai & lanjut')}
									<ChevronRightIcon class="size-4 ml-1" />
								</Button>
							</div>
						</div>
					{/if}
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
