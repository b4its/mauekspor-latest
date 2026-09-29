<script lang="ts">
	/**
	 * Dialog penampil isi berkas + tombol "Analisa file ini".
	 *
	 * Menampilkan pratinjau isi berkas sesuai jenisnya (spreadsheet, dokumen,
	 * presentasi, PDF, teks, gambar, arsip). Tombol "Analisa file ini"
	 * memanggil asisten AI lewat endpoint `/files/{id}/analyze/` dan menampilkan
	 * hasil analisis di dalam dialog yang sama.
	 */
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { MarkdownRenderer } from '$lib/components/MarkdownRenderer';
	import ThinkingIndicator from '$lib/components/ThinkingIndicator.svelte';
	import { t } from '$lib/i18n.svelte';
	import {
		previewFileAsset,
		analyzeFileAsset,
		fileDownloadUrl,
		type FilePreviewData
	} from '$lib/api/files';

	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import TableIcon from '@lucide/svelte/icons/table';
	import PresentationIcon from '@lucide/svelte/icons/presentation';
	import ImageIcon from '@lucide/svelte/icons/image';
	import FileArchiveIcon from '@lucide/svelte/icons/file-archive';
	import FileIcon from '@lucide/svelte/icons/file';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import LoaderCircleIcon from '@lucide/svelte/icons/loader-circle';
	import DownloadIcon from '@lucide/svelte/icons/download';

	let {
		open = $bindable(false),
		fileId = ''
	}: {
		open: boolean;
		fileId: string;
	} = $props();

	let loading = $state(false);
	let error = $state('');
	let preview = $state<FilePreviewData | null>(null);
	let meta = $state<{ name: string; contentType: string; size: string; storageAvailable: boolean; downloadUrl: string } | null>(null);

	let analyzing = $state(false);
	let analysisError = $state('');
	let analysis = $state('');

	let kindIcon = $derived.by(() => {
		switch (preview?.kind) {
			case 'spreadsheet': return TableIcon;
			case 'presentation': return PresentationIcon;
			case 'pdf':
			case 'document': return FileTextIcon;
			case 'image': return ImageIcon;
			case 'archive': return FileArchiveIcon;
			default: return FileIcon;
		}
	});

	let kindLabel = $derived.by(() => {
		switch (preview?.kind) {
			case 'spreadsheet': return t('Spreadsheet');
			case 'document': return t('Dokumen');
			case 'presentation': return t('Presentasi');
			case 'pdf': return 'PDF';
			case 'image': return t('Gambar');
			case 'archive': return t('Arsip');
			case 'text': return t('Teks');
			default: return t('Berkas');
		}
	});

	// Muat pratinjau tiap kali dialog dibuka dengan berkas berbeda.
	$effect(() => {
		if (open && fileId) {
			loadPreview(fileId);
		}
	});

	async function loadPreview(id: string) {
		loading = true;
		error = '';
		preview = null;
		analysis = '';
		analysisError = '';
		try {
			const res = await previewFileAsset(id);
			preview = res.data.preview;
			meta = {
				name: res.data.name,
				contentType: res.data.contentType,
				size: res.data.size,
				storageAvailable: res.data.storageAvailable,
				downloadUrl: fileDownloadUrl(res.data.id)
			};
		} catch {
			error = t('Gagal memuat isi berkas.');
		} finally {
			loading = false;
		}
	}

	async function handleAnalyze() {
		if (!fileId || analyzing) return;
		analyzing = true;
		analysisError = '';
		try {
			const res = await analyzeFileAsset(fileId);
			analysis = res.data.analysis;
		} catch {
			analysisError = t('Gagal menganalisis berkas. Coba lagi.');
		} finally {
			analyzing = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2 pr-6 text-base">
				{#if kindIcon}
					{@const Icon = kindIcon}
					<Icon class="size-4 shrink-0 text-primary" />
				{/if}
				<span class="truncate">{meta?.name || t('Isi berkas')}</span>
			</Dialog.Title>
			<Dialog.Description class="text-sm">
				{t('Lihat isi berkas dan minta asisten AI menganalisisnya.')}
			</Dialog.Description>
		</Dialog.Header>

		{#if loading}
			<div class="space-y-3 py-2">
				<Skeleton class="h-6 w-40" />
				<Skeleton class="h-4 w-full" />
				<Skeleton class="h-24 w-full rounded-lg" />
			</div>
		{:else if error}
			<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{:else if preview && meta}
			<div class="space-y-4">
				<div class="flex flex-wrap items-center gap-2">
					<Badge variant="secondary">{kindLabel}</Badge>
					<Badge variant="outline">{meta.size}</Badge>
					{#if !meta.storageAvailable}
						<Badge variant="outline" class="border-orange-500/40 text-orange-600 dark:text-orange-400">{t('Isi tidak tersimpan di server')}</Badge>
					{/if}
					{#if meta.storageAvailable}
						<a
							href={meta.downloadUrl}
							target="_blank"
							rel="noopener"
							class="ms-auto inline-flex items-center gap-1.5 text-sm font-bold text-primary no-underline hover:underline"
						>
							<DownloadIcon class="size-3.5" />
							{t('Unduh')}
						</a>
					{/if}
				</div>

				{#if preview.summary}
					<p class="text-sm text-muted-foreground">{preview.summary}</p>
				{/if}

				<!-- Pratinjau isi sesuai jenis berkas -->
				{#if preview.kind === 'spreadsheet' && preview.sheets.length}
					<div class="space-y-4">
						{#each preview.sheets as sheet}
							<div class="overflow-hidden rounded-lg border">
								<div class="border-b bg-muted/40 px-3 py-1.5 text-xs font-bold text-muted-foreground">
									Sheet: {sheet.name}
								</div>
								<div class="max-h-64 overflow-auto">
									<table class="w-full border-collapse text-xs">
										<tbody>
											{#each sheet.rows as row, ri}
												<tr class={ri === 0 ? 'bg-muted/50 font-bold' : ''}>
													{#each row as cell}
														<td class="border px-2 py-1 align-top whitespace-nowrap">{cell}</td>
													{/each}
												</tr>
											{/each}
										</tbody>
									</table>
								</div>
							</div>
						{/each}
					</div>
				{:else if preview.kind === 'presentation' && preview.slides.length}
					<div class="space-y-2">
						{#each preview.slides as slide, i}
							<div class="rounded-lg border bg-muted/30 p-3">
								<span class="text-xs font-bold text-muted-foreground">Slide {i + 1}</span>
								<p class="mt-1 whitespace-pre-wrap text-sm">{slide}</p>
							</div>
						{/each}
					</div>
				{:else if preview.kind === 'document' && preview.paragraphs.length}
					<div class="max-h-72 space-y-2 overflow-auto rounded-lg border p-3">
						{#each preview.paragraphs as para}
							<p class="text-sm leading-relaxed">{para}</p>
						{/each}
					</div>
				{:else if preview.text}
					<pre class="max-h-72 overflow-auto rounded-lg border bg-muted/40 p-3 text-xs whitespace-pre-wrap">{preview.text}</pre>
				{:else}
					<div class="rounded-lg border border-dashed p-6 text-center text-sm font-semibold text-muted-foreground">
						{preview.note || t('Isi berkas tidak dapat ditampilkan.')}
					</div>
				{/if}

				{#if preview.truncated}
					<p class="text-xs text-muted-foreground">{t('Pratinjau dipotong untuk kinerja. Unduh berkas untuk isi lengkap.')}</p>
				{/if}

				<!-- Aksi analisis AI -->
				<div class="rounded-xl border border-primary/30 bg-primary/5 p-3">
					<div class="flex flex-wrap items-center justify-between gap-2">
						<div class="flex items-center gap-2">
							<SparklesIcon class="size-4 text-primary" />
							<span class="text-sm font-bold">{t('Analisis isi berkas ini')}</span>
						</div>
						<Button onclick={handleAnalyze} disabled={analyzing}>
							{#if analyzing}
								<LoaderCircleIcon class="size-3.5 animate-spin" />
								<span class="ms-1.5">{t('Menganalisis...')}</span>
							{:else}
								{t('Analisa file ini')}
							{/if}
						</Button>
					</div>

					{#if analyzing}
						<div class="mt-3"><ThinkingIndicator /></div>
					{/if}
					{#if analysisError}
						<p role="alert" class="mt-3 rounded-lg bg-destructive/10 px-3 py-2 text-xs font-bold text-destructive">{analysisError}</p>
					{/if}
					{#if analysis}
						<div class="mt-3 rounded-lg border bg-card p-3">
							<MarkdownRenderer text={analysis} />
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>
