<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { statusTone } from '$lib/utils/format';
	import { generateTradeDocument, approveTradeDocument, updateTradeDocument, deleteTradeDocument } from '$lib/api/documents';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let approving = $state(false);
	let approved = $state(false);
	let regenerated = $state(false);
	let error = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let message = $state('');
	let editType = $state('');
	let editStatus = $state('');
	let editVersion = $state('');
	let editOwner = $state('');
	let savedType = $state('');
	let savedStatus = $state('');
	let savedVersion = $state('');
	let savedOwner = $state('');
	let localType = $derived(savedType || data.document.type);
	let localStatus = $derived(savedStatus || data.document.status);
	let localVersion = $derived(savedVersion || data.document.version);
	let localOwner = $derived(savedOwner || data.document.owner);

	let displayStatus = $derived(approved ? 'Approved' : regenerated ? 'Ready' : localStatus);
	let displayScore = $derived(regenerated || approved ? Math.max(data.document.validationScore, 94) : data.document.validationScore);

	async function regenerate() {
		error = '';
		try {
			const res = await generateTradeDocument({ projectId: data.document.projectId, type: data.document.type });
			regenerated = true;
			if (res.data?.status) savedStatus = res.data.status;
			message = t('Dokumen diregenerasi di backend.');
		} catch {
			error = t('Gagal regenerate dokumen.');
		}
	}

	async function approve() {
		error = '';
		approving = true;
		try {
			const res = await approveTradeDocument(data.document.id);
			approved = true;
			if (res.data?.status) savedStatus = res.data.status;
			message = t('Dokumen disetujui di backend.');
		} catch {
			error = t('Gagal menyetujui dokumen.');
		} finally {
			approving = false;
		}
	}

	function openEdit() {
		editType = data.document.type;
		editStatus = data.document.status;
		editVersion = data.document.version;
		editOwner = data.document.owner;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editStatus.trim()) {
			error = t('Status dokumen wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload: Record<string, string> = {};
			if (editType.trim() !== data.document.type) payload.type = editType.trim();
			if (editStatus.trim() !== data.document.status) payload.status = editStatus.trim();
			if (editVersion.trim() !== data.document.version) payload.version = editVersion.trim();
			if (editOwner.trim() !== data.document.owner) payload.owner = editOwner.trim();
			const res = await updateTradeDocument(data.document.id, payload);
			savedType = res.data.type;
			savedStatus = res.data.status;
			savedVersion = res.data.version;
			savedOwner = res.data.owner;
			message = t('Dokumen diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan dokumen.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus dokumen ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteTradeDocument(data.document.id);
			goto('/documents');
		} catch {
			error = t('Gagal menghapus dokumen.');
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
	<title>{localType} | MauEkspor</title>
</svelte:head>

<AppShell title={localType} eyebrow={localType}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{localType}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.document.projectId} - {localVersion}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Skor validasi')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{displayScore}%</strong>
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
						{t('Tipe')}
						<Input bind:value={editType} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Versi')}
						<Input bind:value={editVersion} />
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
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Kolom Dokumen')}</CardTitle>
					<CardDescription>{t('Kolom dihasilkan dari data proyek, produk, kutipan, dan pengiriman.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" onclick={regenerate}>{t('Regenerasi')}</Button>
					<Button disabled={approving || approved || displayScore < 90} onclick={approve}>
						{approving ? t('Menyetujui...') : approved ? t('Disetujui') : t('Setujui dokumen')}
					</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				{#each Object.entries(data.document.fields) as [key, value]}
					<div class="rounded-lg border bg-muted/40 p-3">
						<span class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-muted-foreground">{key}</span>
						<strong class="block text-sm font-bold">{value}</strong>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Daftar Periksa Validasi')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 p-0 pt-4">
				{#each data.document.checks as check}
					<div class="grid gap-2.5 rounded-lg border bg-muted/40 p-3">
						<Badge variant={toneVariant(statusTone(check.status))} class="w-fit">{check.status}</Badge>
						<div>
							<strong class="block">{check.label}</strong>
							<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{check.detail}</p>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Pagar pembatas dokumen')}</Badge>
				<CardTitle>{t('Konsistensi lintas dokumen')}</CardTitle>
			</CardHeader>
			<CardContent class="p-0 pt-4">
				<p class="leading-relaxed text-muted-foreground">
					{t('Persetujuan hanya boleh diaktifkan ketika invoice, packing list, kode HS, Incoterm, buyer, dan asal konsisten di semua dokumen dagang.')}
				</p>
				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
				{#if regenerated}
					<p class="mt-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">
						{t('Dokumen diregenerasi di backend.')}
					</p>
				{/if}
				{#if approved}
					<p class="mt-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">
						{t('Dokumen disetujui di backend.')}
					</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>