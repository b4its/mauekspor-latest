<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { NativeSelect, NativeSelectOption } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';
	import { educationalModules as seedModules } from '$lib/data/trade';
	import {
		listEducationalModules,
		publishEducationalModule,
		createEducationalModule,
		deleteEducationalModule,
		updateEducationalModule,
		type EducationalModulePayload,
		type LessonPayload
	} from '$lib/api/educational';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	import PlusIcon from '@lucide/svelte/icons/plus';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import BookOpenIcon from '@lucide/svelte/icons/book-open';
	import GraduationCapIcon from '@lucide/svelte/icons/graduation-cap';
	import HelpCircleIcon from '@lucide/svelte/icons/help-circle';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';
	import AlertCircleIcon from '@lucide/svelte/icons/alert-circle';
	import XIcon from '@lucide/svelte/icons/x';
	import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
	import EyeIcon from '@lucide/svelte/icons/eye';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';
	import VideoIcon from '@lucide/svelte/icons/video';

	let modules = createRemoteList(listEducationalModules, seedModules);
	let publishing = $state('');
	let deleting = $state('');
	let error = $state('');
	let successMsg = $state('');

	function getYouTubeEmbedUrl(url?: string): string | null {
		if (!url) return null;
		const trimmed = url.trim();
		if (!trimmed) return null;
		if (/^[a-zA-Z0-9_-]{11}$/.test(trimmed)) {
			return `https://www.youtube-nocookie.com/embed/${trimmed}?rel=0&modestbranding=1`;
		}
		const match = trimmed.match(/(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})/);
		return match ? `https://www.youtube-nocookie.com/embed/${match[1]}?rel=0&modestbranding=1` : null;
	}

	// State Modal Pembuat Modul Lengkap
	let isBuilderOpen = $state(false);
	let isSaving = $state(false);
	let activeTab = $state<'info' | 'lessons' | 'quiz'>('info');

	// Form Modul
	let formTitle = $state('');
	let formLevel = $state('Beginner');
	let formSummary = $state('');
	let formStatus = $state('Published');

	// Form Materi
	type FormLesson = {
		title: string;
		kind: 'Reading' | 'Video';
		duration: string;
		content: string;
		videoUrl: string;
		keyPointsStr: string;
	};
	let formLessons = $state<FormLesson[]>([
		{
			title: '',
			kind: 'Reading',
			duration: '5 min',
			content: '',
			videoUrl: '',
			keyPointsStr: ''
		}
	]);

	// Form Kuis
	type FormQuiz = {
		question: string;
		options: [string, string, string, string];
		correctIndex: number;
		explanation: string;
	};
	let formQuizzes = $state<FormQuiz[]>([
		{
			question: '',
			options: ['', '', '', ''],
			correctIndex: 0,
			explanation: ''
		}
	]);

	$effect(() => {
		modules.load();
	});

	function resetForm() {
		formTitle = '';
		formLevel = 'Beginner';
		formSummary = '';
		formStatus = 'Published';
		formLessons = [
			{
				title: '',
				kind: 'Reading',
				duration: '5 min',
				content: '',
				videoUrl: '',
				keyPointsStr: ''
			}
		];
		formQuizzes = [
			{
				question: '',
				options: ['', '', '', ''],
				correctIndex: 0,
				explanation: ''
			}
		];
		activeTab = 'info';
	}

	function loadSampleTemplate() {
		formTitle = 'Sertifikasi Karantina Barantin & Uji Mutu Ekspor';
		formLevel = 'Intermediate';
		formSummary = 'Panduan teknis pemenuhan standar karantina tumbuhan (SPS WTO), penerbitan Phytosanitary Certificate dari Badan Karantina Indonesia, dan kepatuhan residu ekspor.';
		formStatus = 'Published';

		formLessons = [
			{
				title: 'Regulasi Karantina Tumbuhan & Prosedur Phytosanitary Certificate',
				kind: 'Reading',
				duration: '7 min',
				content: 'Sesuai amanat UU No. 21 Tahun 2019 tentang Karantina Hewan, Ikan, dan Tumbuhan, setiap komoditas pertanian dan pangan yang diekspor wajib dilengkapi Phytosanitary Certificate dari Badan Karantina Indonesia (Barantin). Proses pengajuan dilakukan melalui sistem digital Barantin dengan melampirkan invoice, packing list, serta permohonan pemeriksaan fisik dan laboratorium kesehatan tumbuhan sebelum muat ke kontainer.',
				videoUrl: '',
				keyPointsStr: 'UU No. 21/2019 tentang Karantina Nasional\nPengajuan digital lewat sistem Barantin\nPemeriksaan fisik dan uji lab bebas Organisme Pengganggu Tumbuhan Karantina (OPTK)'
			},
			{
				title: 'Kepatuhan Standar Kayu Kemasan ISPM 15 & Batas Residu Pestisida (MRL)',
				kind: 'Reading',
				duration: '6 min',
				content: 'Pasar global (Uni Eropa, Amerika Serikat, Jepang, Australia) menerapkan batas maksimum residu pestisida (MRL) yang sangat ketat. Selain itu, palet dan kemasan kayu wajib memenuhi standar perlakuan panas (HT) atau fumigasi resmi berstempel ISPM 15 oleh penyedia tersertifikasi, guna menghindari penolakan barang saat tiba di pelabuhan tujuan.',
				videoUrl: '',
				keyPointsStr: 'Wajib perlakuan panas / fumigasi ISPM 15 pada palet kayu\nPengujian lab MRL sebelum pengapalan\nPelanggaran MRL berisiko penolakan kontainer (Rejection Notice)'
			},
			{
				title: 'Video Pembelajaran: Karantina Tumbuhan & Persyaratan Ekspor',
				kind: 'Video',
				duration: '10 min',
				content: 'Video pembelajaran resmi dari Badan Karantina Indonesia mengenai tahapan uji laboratorium, penerbitan sertifikat karantina tumbuhan, dan kepatuhan kontainer sebelum dikapalkan.',
				videoUrl: 'https://www.youtube.com/watch?v=JnMtuZTjV6Q',
				keyPointsStr: 'Alur inspeksi fisik dan laboratorium di pelabuhan muat\nPenerbitan Phytosanitary Certificate secara elektronik\nMitigasi penolakan barang di negara tujuan ekspor'
			}
		];

		formQuizzes = [
			{
				question: 'Lembaga resmi di Indonesia yang berwenang menerbitkan Phytosanitary Certificate untuk ekspor komoditas tumbuhan adalah...',
				options: [
					'Badan Karantina Indonesia (Barantin)',
					'Kementerian Perdagangan RI',
					'Direktorat Jenderal Bea dan Cukai',
					'Kementerian Koordinator Perekonomian'
				],
				correctIndex: 0,
				explanation: 'Berdasarkan UU No. 21 Tahun 2019, fungsi perlindungan karantina hewan, ikan, dan tumbuhan untuk perdagangan internasional dipusatkan pada Badan Karantina Indonesia (Barantin).'
			},
			{
				question: 'Mengapa kemasan palet kayu wajib memenuhi sertifikasi stempel resmi ISPM 15?',
				options: [
					'Hanya agar barang terlihat rapi di pelabuhan muat',
					'Untuk mencegah penyebaran hama rayap dan serangga karantina antar-negara',
					'Sebagai syarat pembayaran L/C di bank devisa semata',
					'Agar terbebas dari bea masuk di negara tujuan'
				],
				correctIndex: 1,
				explanation: 'Standar ISPM 15 (International Standards for Phytosanitary Measures No. 15) diwajibkan secara global untuk membunuh hama dan serangga perusak kayu sebelum masuk ke ekosistem negara tujuan.'
			}
		];
	}

	function addLesson() {
		formLessons = [
			...formLessons,
			{
				title: '',
				kind: 'Reading',
				duration: '5 min',
				content: '',
				videoUrl: '',
				keyPointsStr: ''
			}
		];
	}

	function removeLesson(index: number) {
		if (formLessons.length <= 1) {
			error = t('Modul minimal harus memiliki 1 materi pembelajaran.');
			return;
		}
		formLessons = formLessons.filter((_, i) => i !== index);
	}

	function addQuiz() {
		formQuizzes = [
			...formQuizzes,
			{
				question: '',
				options: ['', '', '', ''],
				correctIndex: 0,
				explanation: ''
			}
		];
	}

	function removeQuiz(index: number) {
		if (formQuizzes.length <= 1) {
			error = t('Modul minimal harus memiliki 1 pertanyaan kuis pemahaman.');
			return;
		}
		formQuizzes = formQuizzes.filter((_, i) => i !== index);
	}

	async function handleSaveModule() {
		error = '';
		if (!formTitle.trim() || formTitle.trim().length < 3) {
			error = t('Judul modul harus diisi minimal 3 karakter.');
			activeTab = 'info';
			return;
		}

		// Validasi materi
		for (let i = 0; i < formLessons.length; i++) {
			const l = formLessons[i];
			if (!l.title.trim()) {
				error = t(`Judul materi ke-${i + 1} tidak boleh kosong.`);
				activeTab = 'lessons';
				return;
			}
			if (!l.content.trim()) {
				error = t(`Isi konten materi ke-${i + 1} tidak boleh kosong.`);
				activeTab = 'lessons';
				return;
			}
		}

		// Validasi kuis
		for (let i = 0; i < formQuizzes.length; i++) {
			const q = formQuizzes[i];
			if (!q.question.trim()) {
				error = t(`Pertanyaan kuis ke-${i + 1} tidak boleh kosong.`);
				activeTab = 'quiz';
				return;
			}
			if (q.options.some((opt) => !opt.trim())) {
				error = t(`Keempat opsi jawaban (A, B, C, D) pada soal kuis ke-${i + 1} wajib diisi.`);
				activeTab = 'quiz';
				return;
			}
		}

		isSaving = true;
		try {
			const lessonsPayload: LessonPayload[] = formLessons.map((l) => ({
				title: l.title.trim(),
				kind: l.kind,
				duration: l.duration.trim() || '5 min',
				content: l.content.trim(),
				video_url: l.videoUrl.trim(),
				key_points: l.keyPointsStr
					.split('\n')
					.map((p) => p.trim())
					.filter((p) => p.length > 0)
			}));

			const quizPayload = formQuizzes.map((q) => ({
				question: q.question.trim(),
				options: q.options.map((opt) => opt.trim()),
				correct_index: q.correctIndex,
				explanation: q.explanation.trim()
			}));

			const payload: EducationalModulePayload = {
				title: formTitle.trim(),
				description: formSummary.trim(),
				summary: formSummary.trim(),
				level: formLevel,
				status: formStatus,
				order_index: modules.items.length + 1,
				lessons: lessonsPayload,
				quiz_questions: quizPayload
			};

			const res = await createEducationalModule(payload);
			if (res.data) {
				modules.upsert(res.data);
			}
			await modules.load();

			successMsg = t('Modul pembelajaran dan kuis berhasil dibuat dan tersimpan ke database!');
			isBuilderOpen = false;
			resetForm();
			setTimeout(() => {
				successMsg = '';
			}, 4000);
		} catch (e) {
			error = e instanceof Error ? e.message : t('Gagal menyimpan modul baru.');
		} finally {
			isSaving = false;
		}
	}

	async function publishModule(id: string) {
		error = '';
		publishing = id;
		try {
			const res = await publishEducationalModule(id);
			if (res.data) {
				modules.upsert(res.data);
			} else {
				const module = modules.items.find((item) => item.id === id);
				if (module) modules.upsert({ ...module, status: 'Published' });
			}
			successMsg = t('Modul berhasil dipublikasikan!');
			setTimeout(() => {
				successMsg = '';
			}, 3000);
		} catch {
			error = t('Gagal mempublikasikan modul.');
		} finally {
			publishing = '';
		}
	}

	async function removeModule(id: string) {
		if (!confirm(t('Hapus modul ini beserta seluruh materi dan kuisnya?'))) return;
		error = '';
		deleting = id;
		try {
			await deleteEducationalModule(id);
			modules.remove(id);
			successMsg = t('Modul berhasil dihapus.');
			setTimeout(() => {
				successMsg = '';
			}, 3000);
		} catch {
			error = t('Gagal menghapus modul.');
		} finally {
			deleting = '';
		}
	}

	async function moveModule(index: number, dir: -1 | 1) {
		const target = index + dir;
		if (target < 0 || target >= modules.items.length) return;
		const a = modules.items[index];
		const b = modules.items[target];
		const aOrder = a.orderIndex ?? index;
		const bOrder = b.orderIndex ?? target;
		try {
			const resA = await updateEducationalModule(a.id, { title: a.title, description: a.description ?? '', order_index: bOrder });
			const resB = await updateEducationalModule(b.id, { title: b.title, description: b.description ?? '', order_index: aOrder });
			if (resA.data) modules.upsert(resA.data);
			if (resB.data) modules.upsert(resB.data);
			if (!resA.data || !resB.data) {
				await modules.load();
			}
		} catch {
			error = t('Gagal mengubah urutan modul.');
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	let paginationPage_modules = $state(1);
	let paginationPageSize_modules = $state(8);
	let pagedItems_modules = $derived(paginate(modules.items ?? [], paginationPage_modules, paginationPageSize_modules));
	let paginationTotalPages_modules = $derived(calcTotalPages(modules.items?.length ?? 0, paginationPageSize_modules));
</script>

<svelte:head>
	<title>{t('Manajemen Modul Edukasi & Kuis')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Manajemen Modul Edukasi')} eyebrow={t('Pusat Kontrol Kurikulum & Evaluasi Kuis')}>
	<!-- Top Hero Banner -->
	<Card class="panel-hero border bg-gradient-to-br from-primary/5 via-card to-card p-6 shadow-sm md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<div class="flex items-center gap-2">
					<Badge variant="outline" class="gap-1 border-primary/30 bg-primary/10 text-primary">
						<GraduationCapIcon class="size-3.5" />
						<span>{t('Panel Admin Edukasi')}</span>
					</Badge>
					<Badge variant="secondary" class="text-xs">
						{modules.items.length} {t('Modul Aktif')}
					</Badge>
				</div>
				<CardTitle class="mt-3 font-display text-3xl font-black tracking-tight text-foreground md:text-4xl">
					{t('Kurikulum & Kuis Evaluasi Ekspor')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl text-sm leading-relaxed">
					{t('Kelola materi pelatihan komprehensif dan bank soal kuis interaktif berstandar regulasi perdagangan internasional 2026 untuk menguji pemahaman eksportir.')}
				</CardDescription>
			</div>
			<div class="flex flex-wrap items-center gap-2.5">
				<Button
					size="lg"
					class="gap-2 shadow-sm"
					onclick={() => {
						resetForm();
						isBuilderOpen = true;
					}}
				>
					<PlusIcon class="size-4" />
					<span>{t('Buat Modul & Kuis Baru')}</span>
				</Button>
				<Button variant="outline" href="/admin" class="gap-2">
					<ArrowLeftIcon class="size-4" />
					<span>{t('Dasbor Admin')}</span>
				</Button>
				<Button variant="outline" href="/educational" class="gap-2">
					<EyeIcon class="size-4" />
					<span>{t('Lihat Katalog')}</span>
				</Button>
			</div>
		</div>
	</Card>

	<!-- Alerts -->
	{#if error}
		<div class="mt-4 flex items-center justify-between rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-semibold text-destructive">
			<div class="flex items-center gap-2">
				<AlertCircleIcon class="size-4 shrink-0" />
				<span>{error}</span>
			</div>
			<button onclick={() => (error = '')} class="hover:opacity-80"><XIcon class="size-4" /></button>
		</div>
	{/if}

	{#if successMsg}
		<div class="mt-4 flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
			<div class="flex items-center gap-2">
				<CheckCircle2Icon class="size-4 shrink-0" />
				<span>{successMsg}</span>
			</div>
			<button onclick={() => (successMsg = '')} class="hover:opacity-80"><XIcon class="size-4" /></button>
		</div>
	{/if}

	<!-- Modules Table / Card List -->
	<Card class="mt-6 shadow-sm">
		<CardHeader class="flex-row items-center justify-between gap-3 border-b pb-4">
			<div class="flex items-center gap-2">
				<BookOpenIcon class="size-5 text-primary" />
				<div>
					<CardTitle class="text-lg">{t('Daftar Seluruh Modul Pembelajaran')}</CardTitle>
					<CardDescription class="text-xs">{t('Setiap modul wajib memuat materi bacaan/video serta kuis evaluasi.')}</CardDescription>
				</div>
			</div>
			<Button size="sm" variant="ghost" onclick={() => modules.load()} title={t('Segarkan Data')}>
				<RefreshCwIcon class="size-4 {modules.loading ? 'animate-spin' : ''}" />
			</Button>
		</CardHeader>

		<CardContent class="grid gap-3 pt-4">
			{#if modules.items.length === 0}
				<div class="py-12 text-center">
					<GraduationCapIcon class="mx-auto size-12 text-muted-foreground/40" />
					<h3 class="mt-3 text-base font-bold">{t('Belum ada modul edukasi')}</h3>
					<p class="mt-1 text-sm text-muted-foreground">{t('Buat modul baru lengkap dengan materi dan kuis sekarang.')}</p>
					<Button class="mt-4 gap-2" onclick={() => { resetForm(); isBuilderOpen = true; }}>
						<PlusIcon class="size-4" />
						<span>{t('Buat Modul Baru')}</span>
					</Button>
				</div>
			{:else}
				{#each pagedItems_modules as module, index (module.id)}
					<div class="flex flex-col justify-between gap-3 rounded-xl border bg-card p-4 transition-colors hover:border-primary/40 sm:flex-row sm:items-center">
						<div class="min-w-0 flex-1 space-y-1.5">
							<div class="flex flex-wrap items-center gap-2">
								<Badge variant="outline" class="font-mono text-[11px] font-bold">
									#{index + 1}
								</Badge>
								<strong class="text-base font-bold text-foreground">{module.title}</strong>
								<Badge variant={toneVariant(statusTone(module.status))} class="text-[11px]">
									{module.status}
								</Badge>
							</div>

							{#if module.summary || module.description}
								<p class="line-clamp-2 text-xs text-muted-foreground">
									{module.summary || module.description}
								</p>
							{/if}

							<div class="flex flex-wrap items-center gap-3 pt-1 text-xs text-muted-foreground">
								<span class="inline-flex items-center gap-1 font-medium text-foreground">
									<Badge variant="secondary" class="text-[10px] uppercase font-bold tracking-wider">
										{module.level}
									</Badge>
								</span>
								<span class="inline-flex items-center gap-1">
									<BookOpenIcon class="size-3.5 text-primary" />
									<strong>{module.lessonCount ?? module.lessons ?? 0}</strong> {t('Materi')}
								</span>
								<span class="inline-flex items-center gap-1">
									<HelpCircleIcon class="size-3.5 text-amber-500" />
									<strong>{module.quizCount ?? 1}</strong> {t('Kuis Interaktif')}
								</span>
							</div>
						</div>

						<div class="flex flex-wrap items-center justify-end gap-2 shrink-0 pt-2 sm:pt-0">
							<div class="flex items-center gap-1">
								<Button
									size="sm"
									variant="outline"
									disabled={index === 0}
									onclick={() => moveModule(index, -1)}
									title={t('Pindah ke atas')}
								>
									↑
								</Button>
								<Button
									size="sm"
									variant="outline"
									disabled={index === modules.items.length - 1}
									onclick={() => moveModule(index, 1)}
									title={t('Pindah ke bawah')}
								>
									↓
								</Button>
							</div>

							<Button size="sm" variant="outline" href={`/educational/modules/${module.id}`} class="gap-1.5">
								<EyeIcon class="size-3.5" />
								<span>{t('Detail & Uji Kuis')}</span>
							</Button>

							{#if module.status !== 'Published'}
								<Button
									size="sm"
									variant="default"
									disabled={publishing === module.id}
									onclick={() => publishModule(module.id)}
									class="gap-1.5"
								>
									<CheckCircle2Icon class="size-3.5" />
									<span>{publishing === module.id ? t('Mempublikasikan...') : t('Publikasikan')}</span>
								</Button>
							{/if}

							<Button
								size="sm"
								variant="destructive"
								disabled={deleting === module.id}
								onclick={() => removeModule(module.id)}
								title={t('Hapus Modul')}
							>
								<Trash2Icon class="size-3.5" />
							</Button>
						</div>
					</div>
				{/each}
			{/if}
		</CardContent>
	</Card>

	<div class="mt-4">
		<Pagination
			bind:page={paginationPage_modules}
			bind:pageSize={paginationPageSize_modules}
			totalPages={paginationTotalPages_modules}
			totalItems={modules.items?.length ?? 0}
		/>
	</div>

	<!-- ==================================================================== -->
	<!-- MODAL FORM BUILDER: BUAT MODUL, MATERI & KUIS LENGKAP               -->
	<!-- ==================================================================== -->
	{#if isBuilderOpen}
		<Dialog.Root bind:open={isBuilderOpen}>
			<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-4xl p-6">
				<Dialog.Header class="border-b pb-4">
					<div class="flex flex-wrap items-center justify-between gap-3">
						<div class="flex items-center gap-2.5">
							<div class="rounded-xl bg-primary/10 p-2 text-primary">
								<GraduationCapIcon class="size-5" />
							</div>
							<div>
								<Dialog.Title class="text-lg font-bold">
									{t('Buat Modul Edukasi Lengkap')}
								</Dialog.Title>
								<Dialog.Description class="text-xs text-muted-foreground">
									{t('Definisikan identitas modul, materi pembelajaran berbobot, serta soal kuis interaktif.')}
								</Dialog.Description>
							</div>
						</div>
						<Button
							type="button"
							size="sm"
							variant="outline"
							class="gap-1.5 text-xs text-primary"
							onclick={loadSampleTemplate}
						>
							<SparklesIcon class="size-3.5 text-amber-500" />
							<span>{t('⚡ Muat Templat Contoh Lengkap')}</span>
						</Button>
					</div>
				</Dialog.Header>

				<!-- Stepper / Section Tab Navigation -->
				<div class="mt-4 flex flex-wrap gap-2 border-b pb-3">
					<button
						type="button"
						onclick={() => (activeTab = 'info')}
						class="flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all {activeTab === 'info' ? 'bg-primary text-primary-foreground shadow-xs' : 'text-muted-foreground hover:bg-muted'}"
					>
						<span>1. {t('Identitas Modul')}</span>
					</button>

					<button
						type="button"
						onclick={() => (activeTab = 'lessons')}
						class="flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all {activeTab === 'lessons' ? 'bg-primary text-primary-foreground shadow-xs' : 'text-muted-foreground hover:bg-muted'}"
					>
						<span>2. {t('Materi Pembelajaran')}</span>
						<Badge variant={activeTab === 'lessons' ? 'secondary' : 'outline'} class="text-[10px]">
							{formLessons.length}
						</Badge>
					</button>

					<button
						type="button"
						onclick={() => (activeTab = 'quiz')}
						class="flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all {activeTab === 'quiz' ? 'bg-primary text-primary-foreground shadow-xs' : 'text-muted-foreground hover:bg-muted'}"
					>
						<span>3. {t('Kuis Pemahaman')}</span>
						<Badge variant={activeTab === 'quiz' ? 'secondary' : 'outline'} class="text-[10px]">
							{formQuizzes.length}
						</Badge>
					</button>
				</div>

				<!-- Section 1: Informasi Modul -->
				{#if activeTab === 'info'}
					<div class="mt-4 space-y-4">
						<div class="space-y-1.5">
							<label for="module-title" class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
								{t('Judul Modul')} <span class="text-destructive">*</span>
							</label>
							<Input
								id="module-title"
								bind:value={formTitle}
								placeholder={t('Contoh: Panduan Klasifikasi HS Code & Tarif Impor 2026')}
								class="text-sm font-medium"
							/>
						</div>

						<div class="grid gap-4 sm:grid-cols-2">
							<div class="space-y-1.5">
								<label for="module-level" class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
									{t('Tingkat Kesulitan')}
								</label>
								<NativeSelect id="module-level" bind:value={formLevel}>
									<NativeSelectOption value="Beginner">{t('Pemula (Beginner)')}</NativeSelectOption>
									<NativeSelectOption value="Intermediate">{t('Menengah (Intermediate)')}</NativeSelectOption>
									<NativeSelectOption value="Advanced">{t('Mahir (Advanced)')}</NativeSelectOption>
								</NativeSelect>
							</div>

							<div class="space-y-1.5">
								<label for="module-status" class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
									{t('Status Publikasi')}
								</label>
								<NativeSelect id="module-status" bind:value={formStatus}>
									<NativeSelectOption value="Published">{t('Langsung Publikasikan (Published)')}</NativeSelectOption>
									<NativeSelectOption value="Draft">{t('Simpan Sebagai Draf (Draft)')}</NativeSelectOption>
								</NativeSelect>
							</div>
						</div>

						<div class="space-y-1.5">
							<label for="module-summary" class="text-xs font-bold uppercase tracking-wider text-muted-foreground">
								{t('Deskripsi / Ringkasan Modul')}
							</label>
							<Textarea
								id="module-summary"
								bind:value={formSummary}
								rows={4}
								placeholder={t('Jelaskan tujuan pembelajaran, dasar regulasi yang dibahas, dan target kompetensi eksportir...')}
								class="text-sm"
							/>
						</div>
					</div>
				{/if}

				<!-- Section 2: Materi Pembelajaran -->
				{#if activeTab === 'lessons'}
					<div class="mt-4 space-y-4">
						<div class="flex items-center justify-between">
							<div>
								<h4 class="text-sm font-bold text-foreground">{t('Daftar Materi Modul')}</h4>
								<p class="text-xs text-muted-foreground">{t('Materi bacaan berbobot atau panduan video yang dipelajari eksportir.')}</p>
							</div>
							<Button size="sm" variant="outline" class="gap-1.5" onclick={addLesson}>
								<PlusIcon class="size-3.5" />
								<span>{t('Tambah Materi')}</span>
							</Button>
						</div>

						<div class="space-y-4">
							{#each formLessons as lesson, i}
								<div class="rounded-xl border bg-muted/20 p-4 space-y-3">
									<div class="flex items-center justify-between border-b pb-2">
										<div class="flex items-center gap-2">
											<span class="flex size-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
												{i + 1}
											</span>
											<span class="text-xs font-bold uppercase text-muted-foreground">
												{t('Materi')} #{i + 1}
											</span>
										</div>
										{#if formLessons.length > 1}
											<button
												type="button"
												onclick={() => removeLesson(i)}
												class="text-destructive hover:opacity-80 text-xs font-semibold flex items-center gap-1"
											>
												<Trash2Icon class="size-3" />
												<span>{t('Hapus')}</span>
											</button>
										{/if}
									</div>

									<div class="grid gap-3 sm:grid-cols-4">
										<div class="sm:col-span-2 space-y-1">
											<label for="lesson-title-{i}" class="text-[11px] font-bold text-muted-foreground">{t('Judul Materi')}</label>
											<Input id="lesson-title-{i}" bind:value={lesson.title} placeholder={t('Contoh: Ketentuan Incoterms 2020 FOB vs CIF')} class="text-xs" />
										</div>
										<div class="space-y-1">
											<label for="lesson-kind-{i}" class="text-[11px] font-bold text-muted-foreground">{t('Tipe')}</label>
											<NativeSelect id="lesson-kind-{i}" bind:value={lesson.kind} class="text-xs">
												<NativeSelectOption value="Reading">{t('Reading (Bacaan)')}</NativeSelectOption>
												<NativeSelectOption value="Video">{t('Video (Visual)')}</NativeSelectOption>
											</NativeSelect>
										</div>
										<div class="space-y-1">
											<label for="lesson-duration-{i}" class="text-[11px] font-bold text-muted-foreground">{t('Estimasi Waktu')}</label>
											<Input id="lesson-duration-{i}" bind:value={lesson.duration} placeholder="5 min" class="text-xs" />
										</div>
									</div>

									{#if lesson.kind === 'Video'}
										<div class="space-y-2 rounded-lg border border-red-500/20 bg-red-500/5 p-3">
											<div class="flex items-center justify-between">
												<label for="lesson-video-{i}" class="flex items-center gap-1.5 text-[11px] font-bold text-red-600 dark:text-red-400">
													<VideoIcon class="size-3.5" />
													<span>{t('URL Video YouTube')}</span>
													<span class="text-[10px] font-normal text-muted-foreground">({t('Contoh: https://www.youtube.com/watch?v=... atau youtu.be/...')})</span>
												</label>
												{#if lesson.videoUrl && getYouTubeEmbedUrl(lesson.videoUrl)}
													<Badge variant="outline" class="border-red-500/30 text-[10px] text-red-600 dark:text-red-400">
														{t('Valid YouTube URL')}
													</Badge>
												{/if}
											</div>
											<Input
												id="lesson-video-{i}"
												bind:value={lesson.videoUrl}
												placeholder="https://www.youtube.com/watch?v=..."
												class="text-xs font-mono"
											/>
											{#if lesson.videoUrl && getYouTubeEmbedUrl(lesson.videoUrl)}
												<div class="mt-2 overflow-hidden rounded-md border border-border bg-black aspect-video max-w-sm">
													<iframe
														src={getYouTubeEmbedUrl(lesson.videoUrl)}
														title={lesson.title || 'Preview Video YouTube'}
														class="w-full h-full border-0"
														allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
														allowfullscreen
													></iframe>
												</div>
											{/if}
										</div>
									{/if}

									<div class="space-y-1">
										<label for="lesson-content-{i}" class="text-[11px] font-bold text-muted-foreground">{t('Isi / Konten Materi')}</label>
										<Textarea
											id="lesson-content-{i}"
											bind:value={lesson.content}
											rows={4}
											placeholder={t('Tuliskan penjelasan materi lengkap, dasar hukum, alur proses, dan panduan praktis ekspor...')}
											class="text-xs"
										/>
									</div>

									<div class="space-y-1">
										<label for="lesson-points-{i}" class="text-[11px] font-bold text-muted-foreground">{t('Poin-Poin Kunci (Pisahkan dengan baris baru)')}</label>
										<Textarea
											id="lesson-points-{i}"
											bind:value={lesson.keyPointsStr}
											rows={2}
											placeholder={t('Contoh:\n- Poin 1: Tanggung jawab biaya berakhir di atas kapal\n- Poin 2: Asuransi laut ditanggung buyer')}
											class="text-xs font-mono"
										/>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Section 3: Kuis Pemahaman -->
				{#if activeTab === 'quiz'}
					<div class="mt-4 space-y-4">
						<div class="flex items-center justify-between">
							<div>
								<h4 class="text-sm font-bold text-foreground">{t('Bank Soal Kuis Interaktif')}</h4>
								<p class="text-xs text-muted-foreground">{t('Pertanyaan pilihan ganda (A-D) dengan kunci jawaban dan pembahasan regulasi.')}</p>
							</div>
							<Button size="sm" variant="outline" class="gap-1.5" onclick={addQuiz}>
								<PlusIcon class="size-3.5" />
								<span>{t('Tambah Soal Kuis')}</span>
							</Button>
						</div>

						<div class="space-y-4">
							{#each formQuizzes as q, qIndex}
								<div class="rounded-xl border bg-muted/20 p-4 space-y-3">
									<div class="flex items-center justify-between border-b pb-2">
										<div class="flex items-center gap-2">
											<span class="flex size-5 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white">
												{qIndex + 1}
											</span>
											<span class="text-xs font-bold uppercase text-muted-foreground">
												{t('Pertanyaan')} #{qIndex + 1}
											</span>
										</div>
										{#if formQuizzes.length > 1}
											<button
												type="button"
												onclick={() => removeQuiz(qIndex)}
												class="text-destructive hover:opacity-80 text-xs font-semibold flex items-center gap-1"
											>
												<Trash2Icon class="size-3" />
												<span>{t('Hapus')}</span>
											</button>
										{/if}
									</div>

									<div class="space-y-1">
										<label for="quiz-question-{qIndex}" class="text-[11px] font-bold text-muted-foreground">{t('Teks Pertanyaan')}</label>
										<Input
											id="quiz-question-{qIndex}"
											bind:value={q.question}
											placeholder={t('Contoh: Berapa digit HS Code yang berlaku seragam secara internasional?')}
											class="text-xs font-medium"
										/>
									</div>

									<div class="grid gap-2 sm:grid-cols-2">
										<div class="space-y-1">
											<label for="quiz-opt-a-{qIndex}" class="text-[10px] font-bold text-muted-foreground">Opsi A</label>
											<Input id="quiz-opt-a-{qIndex}" bind:value={q.options[0]} placeholder="Pilihan A" class="text-xs" />
										</div>
										<div class="space-y-1">
											<label for="quiz-opt-b-{qIndex}" class="text-[10px] font-bold text-muted-foreground">Opsi B</label>
											<Input id="quiz-opt-b-{qIndex}" bind:value={q.options[1]} placeholder="Pilihan B" class="text-xs" />
										</div>
										<div class="space-y-1">
											<label for="quiz-opt-c-{qIndex}" class="text-[10px] font-bold text-muted-foreground">Opsi C</label>
											<Input id="quiz-opt-c-{qIndex}" bind:value={q.options[2]} placeholder="Pilihan C" class="text-xs" />
										</div>
										<div class="space-y-1">
											<label for="quiz-opt-d-{qIndex}" class="text-[10px] font-bold text-muted-foreground">Opsi D</label>
											<Input id="quiz-opt-d-{qIndex}" bind:value={q.options[3]} placeholder="Pilihan D" class="text-xs" />
										</div>
									</div>

									<div class="grid gap-3 sm:grid-cols-2">
										<div class="space-y-1">
											<label for="quiz-correct-{qIndex}" class="text-[11px] font-bold text-muted-foreground">{t('Kunci Jawaban Benar')}</label>
											<NativeSelect id="quiz-correct-{qIndex}" bind:value={q.correctIndex} class="text-xs">
												<NativeSelectOption value={0}>Opsi A: {q.options[0] ? q.options[0].slice(0, 30) : 'A'}</NativeSelectOption>
												<NativeSelectOption value={1}>Opsi B: {q.options[1] ? q.options[1].slice(0, 30) : 'B'}</NativeSelectOption>
												<NativeSelectOption value={2}>Opsi C: {q.options[2] ? q.options[2].slice(0, 30) : 'C'}</NativeSelectOption>
												<NativeSelectOption value={3}>Opsi D: {q.options[3] ? q.options[3].slice(0, 30) : 'D'}</NativeSelectOption>
											</NativeSelect>
										</div>

										<div class="space-y-1">
											<label for="quiz-exp-{qIndex}" class="text-[11px] font-bold text-muted-foreground">{t('Penjelasan / Pembahasan Edukasi')}</label>
											<Input
												id="quiz-exp-{qIndex}"
												bind:value={q.explanation}
												placeholder={t('Contoh: Berdasarkan konvensi WCO, 6 digit pertama HS Code adalah seragam dunia.')}
												class="text-xs"
											/>
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Footer Controls -->
				<Dialog.Footer class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t pt-4">
					<div class="flex items-center gap-2">
						{#if activeTab !== 'info'}
							<Button
								type="button"
								variant="outline"
								size="sm"
								onclick={() => (activeTab = activeTab === 'quiz' ? 'lessons' : 'info')}
							>
								{t('Sebelumnya')}
							</Button>
						{/if}
						{#if activeTab !== 'quiz'}
							<Button
								type="button"
								variant="outline"
								size="sm"
								onclick={() => (activeTab = activeTab === 'info' ? 'lessons' : 'quiz')}
							>
								{t('Lanjut')}
							</Button>
						{/if}
					</div>

					<div class="flex items-center gap-2">
						<Button
							type="button"
							variant="outline"
							size="sm"
							onclick={() => (isBuilderOpen = false)}
						>
							{t('Batal')}
						</Button>
						<Button
							type="button"
							size="sm"
							disabled={isSaving}
							onclick={handleSaveModule}
							class="gap-1.5"
						>
							{#if isSaving}
								<RefreshCwIcon class="size-3.5 animate-spin" />
								<span>{t('Menyimpan...')}</span>
							{:else}
								<CheckCircle2Icon class="size-3.5" />
								<span>{t('Simpan Modul & Kuis')}</span>
							{/if}
						</Button>
					</div>
				</Dialog.Footer>
			</Dialog.Content>
		</Dialog.Root>
	{/if}
</AppShell>