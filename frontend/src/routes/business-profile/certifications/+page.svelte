<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { businessProfiles as seedProfiles } from '$lib/data/trade';
	import { listBusinessProfiles, updateCertifications } from '$lib/api/business-profile';
	import { uploadFileBinary, fileDownloadUrl } from '$lib/api/files';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { t } from '$lib/i18n.svelte';

	import UploadIcon from '@lucide/svelte/icons/upload';
	import FileCheckIcon from '@lucide/svelte/icons/file-check-2';
	import AlertCircleIcon from '@lucide/svelte/icons/alert-circle';
	import XIcon from '@lucide/svelte/icons/x';

	const certOptions = ['Halal', 'ISO 22000', 'HACCP', 'SVLK', 'Organic', 'Origin declaration', 'Nutrition facts'];

	type CertState = {
		name: string;
		selected: boolean;
		fileId: string;
		fileName: string;
		verified: boolean;
		uploading?: boolean;
	};

	let certs = $state<CertState[]>(certOptions.map((name) => ({ name, selected: false, fileId: '', fileName: '', verified: false })));
	let synced = $state(false);
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	$effect(() => {
		profiles.load();
	});

	// Sinkronkan dari profil yang dimuat (hanya sekali, agar tidak menimpa edit user).
	$effect(() => {
		if (synced) return;
		const profile = profiles.items[0];
		if (!profile) return;
		const items = profile.certificationItems ?? [];
		const byName = new Map(items.map((i) => [i.name, i]));
		const known = new Set(certOptions);
		const extra = items.filter((i) => !known.has(i.name)).map((i) => ({
			name: i.name, selected: true, fileId: i.evidenceFileId ?? '', fileName: i.evidenceFile ?? '', verified: !!i.verified
		}));
		certs = [
			...certOptions.map((name) => {
				const item = byName.get(name);
				return {
					name,
					selected: !!item || (profile.certifications ?? []).includes(name),
					fileId: item?.evidenceFileId ?? '',
					fileName: item?.evidenceFile ?? '',
					verified: !!item?.verified
				};
			}),
			...extra
		];
		synced = true;
	});

	function toggleCert(name: string) {
		certs = certs.map((c) =>
			c.name === name ? { ...c, selected: !c.selected, ...(c.selected ? { fileId: '', fileName: '', verified: false } : {}) } : c
		);
	}

	async function handleUpload(name: string, file: File) {
		error = '';
		certs = certs.map((c) => (c.name === name ? { ...c, uploading: true } : c));
		const profile = profiles.items[0] ?? seedProfiles[0];
		try {
			const res = await uploadFileBinary(file, 'Certificate', profile?.id ?? '', ['certificate', name]);
			const id = res.data?.id ?? '';
			certs = certs.map((c) =>
				c.name === name ? { ...c, fileId: id, fileName: res.data?.name ?? file.name, verified: true, uploading: false, selected: true } : c
			);
		} catch {
			error = t('Gagal mengunggah bukti sertifikasi.');
			certs = certs.map((c) => (c.name === name ? { ...c, uploading: false } : c));
		}
	}

	function clearEvidence(name: string) {
		certs = certs.map((c) => (c.name === name ? { ...c, fileId: '', fileName: '', verified: false } : c));
	}

	async function handleSave() {
		error = '';
		const profile = profiles.items[0] ?? seedProfiles[0];
		if (!profile) {
			error = t('Profil bisnis belum tersedia.');
			return;
		}
		saving = true;
		try {
			const items = certs
				.filter((c) => c.selected)
				.map((c) => ({ name: c.name, fileId: c.fileId || undefined, fileName: c.fileName || undefined }));
			const res = await updateCertifications(profile.id, items);
			if (res.data) {
				profiles.upsert(res.data);
				// Sinkronkan kembali status verified dari backend.
				const byName = new Map((res.data.certificationItems ?? []).map((i) => [i.name, i]));
				certs = certs.map((c) => {
					const item = byName.get(c.name);
					return item ? { ...c, verified: !!item.verified, fileId: item.evidenceFileId ?? c.fileId, fileName: item.evidenceFile ?? c.fileName } : c;
				});
			}
			saved = true;
		} catch {
			error = t('Gagal menyimpan sertifikasi.');
		} finally {
			saving = false;
		}
	}

	let selectedCount = $derived(certs.filter((c) => c.selected).length);
	let verifiedCount = $derived(certs.filter((c) => c.selected && c.verified).length);
</script>

<svelte:head>
	<title>{t('Kelola Sertifikasi')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Certifications')} eyebrow={t('Manage business certification claims')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Berbasis bukti')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Unggah dokumen/gambar sebagai bukti setiap sertifikasi.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Sertifikasi hanya menambah skor kesiapan bila disertai bukti berkas (dokumen atau gambar). Klaim tanpa bukti tersimpan sebagai klaim saja, tidak dihitung.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if error}
		<div class="flex items-center justify-between rounded-lg bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive" role="alert">
			<span class="flex items-center gap-2"><AlertCircleIcon class="size-4" />{error}</span>
			<button onclick={() => (error = '')} aria-label={t('Tutup')} title={t('Tutup')}><XIcon class="size-4" /></button>
		</div>
	{/if}

	{#if saved}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Tersimpan')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{verifiedCount} {t('dari')} {selectedCount} {t('sertifikasi berbukti')}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					{t('Klaim tanpa bukti tidak menambah skor kesiapan. Lengkapi berkas bila ingin dihitung.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/business-profile">{t('Kembali ke profil')}</Button>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			{#each certs as cert (cert.name)}
				<div class="flex flex-col gap-3 rounded-lg border bg-muted/30 px-4 py-3.5">
					<label class="flex items-center gap-3">
						<Checkbox checked={cert.selected} onCheckedChange={() => toggleCert(cert.name)} />
						<span class="text-sm font-semibold">{cert.name}</span>
						{#if cert.selected}
							{#if cert.verified}
								<Badge variant="default" class="ms-auto gap-1 text-[10px]"><FileCheckIcon class="size-3" />{t('Berbukti')}</Badge>
							{:else}
								<Badge variant="outline" class="ms-auto text-[10px] text-amber-700 dark:text-amber-400">{t('Tanpa bukti')}</Badge>
							{/if}
						{/if}
					</label>

					{#if cert.selected}
						{#if cert.fileId && cert.verified}
							<div class="flex items-center justify-between gap-2 rounded-md border bg-background px-2.5 py-1.5 text-xs">
								<a href={fileDownloadUrl(cert.fileId)} target="_blank" rel="noopener" class="truncate font-medium text-primary hover:underline">
									{cert.fileName || t('Lihat bukti')}
								</a>
								<button type="button" onclick={() => clearEvidence(cert.name)} class="text-muted-foreground hover:text-destructive" aria-label={t('Hapus bukti')} title={t('Hapus bukti')}>
									<XIcon class="size-3.5" />
								</button>
							</div>
						{:else}
							<label class="flex cursor-pointer items-center justify-center gap-2 rounded-md border border-dashed px-2.5 py-2 text-xs font-semibold text-muted-foreground hover:border-primary/50 hover:text-foreground">
								<input
									type="file"
									class="sr-only"
									accept="image/*,application/pdf"
									disabled={cert.uploading}
									onchange={(e) => {
										const input = e.currentTarget as HTMLInputElement;
										const file = input.files?.[0];
										if (file) handleUpload(cert.name, file);
										input.value = '';
									}}
								/>
								{#if cert.uploading}
									{t('Mengunggah...')}
								{:else}
									<UploadIcon class="size-3.5" />
									{t('Unggah bukti (dokumen/gambar)')}
								{/if}
							</label>
						{/if}
					{/if}
				</div>
			{/each}
		</div>
		<div class="flex flex-wrap gap-3">
			<Button variant="outline" href="/business-profile">{t('Batal')}</Button>
			<Button onclick={handleSave} disabled={saving}>{saving ? t('Menyimpan...') : t('Simpan sertifikasi')}</Button>
		</div>
	{/if}
</AppShell>
