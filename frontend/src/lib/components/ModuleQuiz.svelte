<script lang="ts">
	/**
	 * Kuis interaktif untuk sebuah modul edukasi.
	 *
	 * Soal dimuat dari backend (`/educational/modules/{id}/quiz/`) dan menyesuaikan
	 * topik/materi modul. Pengguna memilih satu opsi per soal, mengirim jawaban,
	 * lalu melihat skor, kelulusan (≥70%), dan penjelasan tiap soal.
	 */
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { t } from '$lib/i18n.svelte';
	import { getModuleQuiz, submitModuleQuiz, type ModuleQuiz, type QuizResult } from '$lib/api/educational';

	import ListChecksIcon from '@lucide/svelte/icons/list-checks';
	import LoaderCircleIcon from '@lucide/svelte/icons/loader-circle';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';
	import XCircleIcon from '@lucide/svelte/icons/x-circle';
	import RotateCcwIcon from '@lucide/svelte/icons/rotate-ccw';
	import TrophyIcon from '@lucide/svelte/icons/trophy';

	let { moduleId, onpass }: { moduleId: string; onpass?: () => void } = $props();

	let loading = $state(true);
	let error = $state('');
	let quiz = $state<ModuleQuiz | null>(null);
	let answers = $state<Record<string, number>>({});
	let result = $state<QuizResult | null>(null);
	let submitting = $state(false);

	$effect(() => {
		if (moduleId) loadQuiz(moduleId);
	});

	async function loadQuiz(id: string) {
		loading = true;
		error = '';
		result = null;
		answers = {};
		try {
			const res = await getModuleQuiz(id);
			quiz = res.data;
		} catch {
			error = t('Gagal memuat kuis.');
		} finally {
			loading = false;
		}
	}

	function choose(questionId: string, option: number) {
		if (result) return; // sudah dinilai — kunci jawaban
		answers = { ...answers, [questionId]: option };
	}

	let answeredCount = $derived(Object.keys(answers).length);
	let allAnswered = $derived(!!quiz && quiz.questions.length > 0 && answeredCount === quiz.questions.length);

	async function handleSubmit() {
		if (!quiz || submitting || !allAnswered) return;
		submitting = true;
		error = '';
		try {
			const res = await submitModuleQuiz(moduleId, answers);
			result = res.data;
			if (result.passed && onpass) onpass();
		} catch {
			error = t('Gagal mengirim jawaban kuis.');
		} finally {
			submitting = false;
		}
	}

	function retry() {
		result = null;
		answers = {};
	}
</script>

<div class="rounded-xl border bg-card p-4">
	<div class="flex flex-wrap items-center justify-between gap-2">
		<div class="flex items-center gap-2">
			<ListChecksIcon class="size-4 text-primary" />
			<span class="text-sm font-bold">{t('Kuis modul')}</span>
			{#if quiz}
				<Badge variant="outline">{quiz.questionCount} {t('soal')}</Badge>
			{/if}
		</div>
		{#if quiz?.lastAttempt}
			<span class="text-xs font-semibold text-muted-foreground">
				{t('Skor terbaik')}: {quiz.lastAttempt.bestScore}% · {quiz.lastAttempt.attemptCount}× {t('percobaan')}
			</span>
		{/if}
	</div>

	{#if loading}
		<div class="grid place-items-center py-8">
			<LoaderCircleIcon class="size-5 animate-spin text-muted-foreground" />
		</div>
	{:else if error}
		<p role="alert" class="mt-3 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{:else if quiz && quiz.questions.length === 0}
		<p class="mt-3 text-sm text-muted-foreground">{t('Belum ada soal untuk modul ini.')}</p>
	{:else if quiz}
		<!-- Hasil penilaian -->
		{#if result}
			<div class="mt-3 rounded-lg border p-3 {result.passed ? 'border-emerald-500/40 bg-emerald-500/10' : 'border-orange-500/40 bg-orange-500/10'}">
				<div class="flex flex-wrap items-center justify-between gap-3">
					<div class="flex items-center gap-2">
						{#if result.passed}
							<TrophyIcon class="size-5 text-emerald-600 dark:text-emerald-400" />
							<span class="font-bold text-emerald-700 dark:text-emerald-300">{t('Lulus!')}</span>
						{:else}
							<span class="font-bold text-orange-700 dark:text-orange-300">{t('Belum lulus')}</span>
						{/if}
					</div>
					<span class="text-2xl font-black">{result.score}%</span>
				</div>
				<p class="mt-1 text-xs font-semibold text-muted-foreground">{result.correctCount} {t('benar dari')} {result.total} {t('soal')} (KKM 70%)</p>
				<Progress value={result.score} class="mt-2" />
			</div>
		{/if}

		<!-- Soal -->
		<ol class="mt-4 grid gap-4">
			{#each quiz.questions as question, qi}
				{@const detail = result?.details.find((d) => d.id === question.id)}
				<li class="rounded-lg border p-3">
					<div class="flex items-start gap-2">
						<span class="mt-0.5 grid size-6 shrink-0 place-items-center rounded-full bg-muted text-xs font-bold">{qi + 1}</span>
						<p class="text-sm font-semibold">{question.question}</p>
					</div>
					<div class="mt-2.5 grid gap-1.5 ps-8">
						{#each question.options as option, oi}
							{@const chosen = (detail ? detail.chosen : answers[question.id]) === oi}
							{@const isAnswer = !!detail && detail.answer === oi}
							<button
								type="button"
								disabled={!!result}
								onclick={() => choose(question.id, oi)}
								class={`flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
									result
										? isAnswer
											? 'border-emerald-500/50 bg-emerald-500/10 font-semibold'
											: chosen
												? 'border-destructive/50 bg-destructive/10'
												: 'border-border opacity-70'
										: chosen
											? 'border-primary bg-primary/10 font-semibold'
											: 'border-border hover:bg-muted/60'
								} ${result ? '' : 'cursor-pointer'}`}
							>
								{#if result && isAnswer}
									<CheckCircle2Icon class="size-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
								{:else if result && chosen}
									<XCircleIcon class="size-4 shrink-0 text-destructive" />
								{:else}
									<span class="grid size-4 shrink-0 place-items-center rounded-full border text-[10px] font-bold">
										{String.fromCharCode(65 + oi)}
									</span>
								{/if}
								<span>{option}</span>
							</button>
						{/each}
					</div>
					{#if detail}
						<p class="mt-2 ps-8 text-xs text-muted-foreground">
							<strong class="font-bold">{t('Penjelasan')}:</strong> {detail.explanation}
						</p>
					{/if}
				</li>
			{/each}
		</ol>

		<div class="mt-4 flex flex-wrap items-center justify-between gap-3">
			<span class="text-xs font-semibold text-muted-foreground">
				{answeredCount}/{quiz.questions.length} {t('dijawab')}
			</span>
			{#if result}
				{#if result.passed}
					<span class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{t('Pelajaran kuis ditandai selesai.')}</span>
				{/if}
				<Button variant="outline" onclick={retry}>
					<RotateCcwIcon class="size-4" />
					{t('Coba lagi')}
				</Button>
			{:else}
				<Button onclick={handleSubmit} disabled={submitting || !allAnswered}>
					{submitting ? t('Menilai...') : t('Kirim jawaban')}
				</Button>
			{/if}
		</div>
	{/if}
</div>
