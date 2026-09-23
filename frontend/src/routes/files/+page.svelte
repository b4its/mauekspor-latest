<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { fileAssets, projects } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { uploadFileAsset, uploadFileBinary, verifyFileAsset, listFiles, fileDownloadUrl } from '$lib/api/files';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Document', 'Certificate', 'Image', 'Evidence', 'Report'];

	function trType(x: string) {
		return t(x === 'All' ? 'Semua' : x === 'Document' ? 'Dokumen' : x === 'Certificate' ? 'Sertifikat' : x === 'Image' ? 'Gambar' : x === 'Evidence' ? 'Bukti' : 'Laporan');
	}

	function trStatus(s: string) {
		return t(s === 'Verified' ? 'Terverifikasi' : s === 'Archived' ? 'Diarsipkan' : s === 'Uploaded' ? 'Terunggah' : 'Menunggu');
	}
	let activeFilter = $state('All');
	let query = $state('');
	let uploaded = $state('');
	let uploading = $state(false);
	let verified = $state(false);
	let error = $state('');
	let verifiedId = $state('');

	let files = createRemoteList(listFiles, fileAssets);
	$effect(() => {
		files.load();
	});

	let filteredFiles = $derived(
		files.items.filter(
			(file) =>
				(activeFilter === 'All' || file.type === activeFilter) &&
				[file.name, file.type, file.status, file.owner, ...file.tags].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let needsReview = $derived(files.items.filter((file) => file.status !== 'Verified' && file.status !== 'Archived').length);
	function projectName(id: string) {
		return projects.find((project) => project.id === id)?.name ?? id;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		error = '';
		uploading = true;
		try {
			await uploadFileBinary(file, 'Evidence', projects[0]?.id ?? '', ['evidence']);
			uploaded = file.name;
			await files.load();
		} catch {
			error = t('Gagal mengunggah file.');
		} finally {
			uploading = false;
			input.value = '';
		}
	}

	async function handleVerify(fileId: string) {
		error = '';
		try {
			await verifyFileAsset(fileId);
			verifiedId = fileId;
		} catch {
			error = t('Gagal memverifikasi file.');
		}
	}
</script>

<svelte:head>
	<title>{t('Files')} | MauEkspor</title>
</svelte:head>

<AppShell title="Files" eyebrow={t('Pustaka bukti dan aset')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Kontrol file')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Jaga dokumen ekspor, bukti, sertifikat, dan aset tetap terorganisir.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Pusatkan file berdasarkan proyek, pemilik, jenis, status, dan tag operasional agar alur kerja kepatuhan dan dokumen tetap dapat ditelusuri.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<label class="cursor-pointer">
				<input type="file" class="hidden" onchange={handleUpload} disabled={uploading} />
				<Button type="button" disabled={uploading} class="pointer-events-none">{uploading ? t('Mengunggah...') : t('Unggah file')}</Button>
			</label>
			<Badge variant="outline">{t('Tinjauan')} {needsReview}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if uploaded}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('File berhasil diunggah.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{uploaded} {t('tersimpan di backend.')}
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{trType(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari file, tag, pemilik...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredFiles as file}
			<Card class="gap-4">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(verified || verifiedId === file.id ? 'Verified' : file.status))}>{verified || verifiedId === file.id ? t('Terverifikasi') : trStatus(file.status)}</Badge>
					<strong class="text-sm font-bold text-muted-foreground">{trType(file.type)}</strong>
				</div>
				<CardHeader class="p-0">
					<CardTitle class="text-xl font-bold tracking-tight">{file.name}</CardTitle>
					<CardDescription>{projectName(file.projectId)} · {file.owner}</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-3 p-0">
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Updated')} <strong class="mt-1 block text-sm font-bold text-foreground">{file.updatedAt}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Ukuran')} <strong class="mt-1 block text-sm font-bold text-foreground">{file.size}</strong>
						</div>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each file.tags as tag}
							<span class="rounded-full border bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">{tag}</span>
						{/each}
					</div>
				</CardContent>
				<div class="flex flex-wrap items-center gap-2">
				{#if file.storageName}
					<a href={fileDownloadUrl(file.id)} target="_blank" rel="noopener" class="text-sm font-bold text-primary no-underline hover:underline">{t('Unduh')}</a>
				{/if}
				<Button variant="outline" onclick={() => handleVerify(file.id)}>{verifiedId === file.id ? t('Terverifikasi') : t('Verifikasi file')}</Button>
			</div>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada file yang cocok dengan pencarian.')}</div>
		{/each}
	</div>
</AppShell>