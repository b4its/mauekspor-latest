<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { statusTone } from '$lib/utils/format';
	import { generateReport, scheduleReport, updateReport, deleteReport } from '$lib/api/reports';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';
	let { data } = $props();
	let generated = $state(false);
	let scheduled = $state(false);
	let busy = $state(false);
	let error = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let message = $state('');
	let editTitle = $state('');
	let editStatus = $state('');
	let editPeriod = $state('');
	let savedTitle = $state('');
	let savedStatus = $state('');
	let savedPeriod = $state('');
	let localTitle = $derived(savedTitle || data.report.title);
	let localStatus = $derived(savedStatus || data.report.status);
	let localPeriod = $derived(savedPeriod || data.report.period);
	let displayStatus = $derived(scheduled ? 'Scheduled' : generated ? 'Ready' : localStatus);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleGenerate() {
		error = '';
		busy = true;
		try {
			await generateReport(data.report.id);
			generated = true;
		} catch {
			error = 'Gagal generate laporan.';
		} finally {
			busy = false;
		}
	}

	async function handleSchedule() {
		error = '';
		busy = true;
		try {
			await scheduleReport(data.report.id);
			scheduled = true;
		} catch {
			error = t('Gagal menjadwalkan laporan.');
		} finally {
			busy = false;
		}
	}

	function openEdit() {
		editTitle = data.report.title;
		editStatus = data.report.status;
		editPeriod = data.report.period;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editTitle.trim()) {
			error = t('Judul laporan wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload: Record<string, string> = {};
			if (editTitle.trim() !== data.report.title) payload.title = editTitle.trim();
			if (editStatus.trim() !== data.report.status) payload.status = editStatus.trim();
			if (editPeriod.trim() !== data.report.period) payload.period = editPeriod.trim();
			const res = await updateReport(data.report.id, payload);
			savedTitle = res.data.title;
			savedStatus = res.data.status;
			savedPeriod = res.data.period;
			message = t('Laporan diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan laporan.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus laporan ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteReport(data.report.id);
			goto('/reports');
		} catch {
			error = t('Gagal menghapus laporan.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{localTitle} | MauEkspor</title>
</svelte:head>

<AppShell title={data.report.id} eyebrow={t('Report detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(displayStatus))} class="w-fit">{displayStatus}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{localTitle}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.report.type} · {localPeriod} · {data.report.owner}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Bagian')}<strong class="mt-1 block text-sm font-bold text-foreground">{data.report.sections.length}</strong></div>
		</CardContent>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={editTitle} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Periode')}
						<Input bind:value={editPeriod} />
					</label>
				</div>
				<Button class="w-fit" disabled={saving} onclick={handleSave}>{saving ? t('Menyimpan...') : t('Simpan perubahan')}</Button>
			</div>
		{/if}
		{#if message}
			<p class="mt-4 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
		{/if}
	</Card>

	<div class="grid gap-4">
		<Card>
			<CardContent class="grid gap-4 p-5">
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div>
						<h3 class="text-xl font-bold tracking-tight">{t('Pembuat laporan')}</h3>
						<p class="mt-1 text-sm text-muted-foreground">{t('Updated')} {data.report.updatedAt}. {t('Buat laporan baru atau jadwalkan pengiriman berulang.')}</p>
					</div>
					<div class="flex flex-wrap gap-2">
						<Button variant="outline" onclick={handleSchedule} disabled={busy}>{scheduled ? t('Dijadwalkan') : t('Jadwalkan')}</Button>
						<Button onclick={handleGenerate} disabled={busy}>{generated ? t('Laporan berhasil dibuat') : busy ? t('Bekerja...') : t('Buat sekarang')}</Button>
					</div>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				{#if generated}
					<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
						{#each data.report.sections as section}
							{#if typeof section === 'object' && section !== null}
								<div class="rounded-lg border bg-muted/40 p-3">
									<span class="text-[10px] font-bold uppercase tracking-wide text-muted-foreground">{section.title}</span>
									<strong class="mt-1 block text-xl font-bold">{section.value}</strong>
									<small class="text-xs text-muted-foreground">{section.detail}</small>
								</div>
							{:else}
								<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{section}</span>
							{/if}
						{/each}
					</div>
				{:else}
					<div class="flex flex-wrap gap-2">
						{#each data.report.sections as section}
							{#if typeof section === 'object' && section !== null}
								<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{section.title}</span>
							{:else}
								<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{section}</span>
							{/if}
						{/each}
					</div>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-5">
				<Badge variant="secondary" class="w-fit">{t('Wawasan')}</Badge>
				<CardTitle>{t('Catatan Eksekutif')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 p-5">
				<div class="grid gap-3 sm:grid-cols-3">
					{#each data.report.insights as insight}
						<div class="rounded-lg border bg-muted/40 p-3 text-sm font-semibold text-muted-foreground">{insight}</div>
					{/each}
				</div>
				{#if generated}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Laporan dibuat di backend.')}</p>
				{/if}
				{#if scheduled}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Laporan dijadwalkan di backend.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>