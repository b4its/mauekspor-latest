<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { statusTone } from '$lib/utils/format';
	import { uploadComplianceEvidence, updateComplianceRequirement, deleteComplianceRequirement } from '$lib/api/compliance';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let evidenceNote = $state('');
	let fileName = $state('');
	let uploaded = $state(false);
	let uploading = $state(false);
	let verifying = $state(false);
	let verified = $state(false);
	let serverStatus = $state('');
	let error = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let message = $state('');
	let editTitle = $state('');
	let editStatus = $state('');
	let editSeverity = $state('');
	let editOwner = $state('');
	let savedTitle = $state('');
	let savedStatus = $state('');
	let savedSeverity = $state('');
	let savedOwner = $state('');
	let localTitle = $derived(savedTitle || data.requirement.title);
	let localStatus = $derived(savedStatus || data.requirement.status);
	let localSeverity = $derived(savedSeverity || data.requirement.severity);
	let localOwner = $derived(savedOwner || data.requirement.owner);

	let displayStatus = $derived(serverStatus || (verified ? 'Verified' : uploaded ? 'Evidence Uploaded' : localStatus));

	async function uploadEvidence() {
		error = '';
		if (evidenceNote.trim().length < 8) {
			error = t('Tambahkan catatan evidence minimal 8 karakter.');
			return;
		}
		uploading = true;
		try {
			const res = await uploadComplianceEvidence({
				requirementId: data.requirement.id,
				note: evidenceNote.trim(),
				fileName: fileName.trim() || undefined
			});
			uploaded = true;
			if (res.data) {
				savedStatus = res.data.status;
				serverStatus = res.data.status;
			}
			message = t('Bukti berhasil disimpan.');
		} catch {
			error = t('Gagal menyimpan bukti ke backend.');
		} finally {
			uploading = false;
		}
	}

	async function verifyEvidence() {
		error = '';
		verifying = true;
		try {
			const res = await updateComplianceRequirement(data.requirement.id, { status: 'Verified' });
			verified = true;
			if (res.data) {
				savedStatus = res.data.status;
				serverStatus = res.data.status;
			}
			message = t('Persyaratan ditandai terverifikasi.');
		} catch {
			error = t('Gagal memverifikasi persyaratan.');
		} finally {
			verifying = false;
		}
	}

	function openEdit() {
		editTitle = data.requirement.title;
		editStatus = data.requirement.status;
		editSeverity = data.requirement.severity;
		editOwner = data.requirement.owner;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editTitle.trim()) {
			error = t('Judul requirement wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload: Record<string, string> = {};
			if (editTitle.trim() !== data.requirement.title) payload.title = editTitle.trim();
			if (editStatus.trim() !== data.requirement.status) payload.status = editStatus.trim();
			if (editSeverity.trim() !== data.requirement.severity) payload.severity = editSeverity.trim();
			if (editOwner.trim() !== data.requirement.owner) payload.owner = editOwner.trim();
			const res = await updateComplianceRequirement(data.requirement.id, payload);
			savedTitle = res.data.title;
			savedStatus = res.data.status;
			savedSeverity = res.data.severity;
			savedOwner = res.data.owner;
			message = t('Requirement diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan requirement.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus requirement ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteComplianceRequirement(data.requirement.id);
			goto('/compliance');
		} catch {
			error = t('Gagal menghapus requirement.');
		} finally {
			deleting = false;
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{localTitle} | MauEkspor</title>
</svelte:head>

<AppShell title={data.requirement.id} eyebrow={t('Compliance requirement detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{localTitle}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.requirement.projectId} - {data.product?.name ?? data.requirement.productId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('AI confidence')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{data.requirement.confidence}%</strong>
			</div>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={editTitle} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tingkat keparahan')}
						<Input bind:value={editSeverity} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Pemilik')}
						<Input bind:value={editOwner} />
					</label>
				</div>
				<Button class="w-fit" disabled={saving} onclick={handleSave}>{saving ? t('Menyimpan...') : t('Simpan perubahan')}</Button>
			</div>
		{/if}
		{#if message}
			<p class="mt-4 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
		{/if}
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="p-0"><CardTitle>{t('Requirement Context')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 pt-4 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kategori')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.category}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tingkat keparahan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.severity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Pemilik')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.owner}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Jatuh tempo')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.due}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Sumber')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.source}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tanggal sumber')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.sourceDate}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Required Evidence')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 p-0 pt-4">
				<p class="text-muted-foreground">{data.requirement.requiredEvidence}</p>
				<div class="rounded-lg border bg-muted/30 p-3.5">
					<span class="block text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Status saat ini')}</span>
					<strong class="mt-1 block text-sm font-bold">{uploaded ? evidenceNote : data.requirement.currentEvidence}</strong>
					{#if fileName}
						<small class="mt-1 block text-sm text-muted-foreground">{t('File terlampir:')} {fileName}</small>
					{/if}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Demo Unggah Bukti')}</CardTitle></CardHeader>
			<CardContent class="p-0 pt-4">
				<form class="grid gap-3.5" onsubmit={(event) => { event.preventDefault(); uploadEvidence(); }}>
					<div class="grid gap-2">
						<Label>{t('Catatan bukti')}</Label>
						<Textarea bind:value={evidenceNote} placeholder={t('Label artwork Jepang diunggah, ditinjau oleh importir...')} rows={5} />
					</div>
					<div class="grid gap-2">
						<Label>{t('Nama file')}</Label>
						<Input bind:value={fileName} placeholder="jp-label-artwork-v2.pdf" />
					</div>
					{#if error}
						<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					{#if message}
						<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
					{/if}
					<div class="flex flex-wrap gap-2.5">
						<Button variant="outline" type="submit" disabled={uploading}>{uploading ? t('Menyimpan...') : t('Simpan bukti')}</Button>
						<Button disabled={!uploaded || verifying || verified} onclick={verifyEvidence}>
							{verifying ? t('Memverifikasi...') : verified ? t('Terverifikasi') : t('Tandai terverifikasi')}
						</Button>
					</div>
				</form>
			</CardContent>
		</Card>
	</div>
</AppShell>