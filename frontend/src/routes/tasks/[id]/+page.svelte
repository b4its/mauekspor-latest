<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { completeTask, assignTask, updateTask, deleteTask } from '$lib/api/tasks';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';
	let { data } = $props();
	let completed = $state(false);
	let reassigned = $state(false);
	let assignOpen = $state(false);
	let assignOwner = $state('');
	let assigning = $state(false);
	let error = $state('');
	let message = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let editTitle = $state('');
	let editStatus = $state('');
	let editPriority = $state('');
	let editOwner = $state('');
	let savedTitle = $state('');
	let savedStatus = $state('');
	let savedPriority = $state('');
	let savedOwner = $state('');
	let serverStatus = $state('');
	let serverOwner = $state('');
	let localTitle = $derived(savedTitle || data.task.title);
	let localOwner = $derived(serverOwner || savedOwner || data.task.owner);
	let localPriority = $derived(savedPriority || data.task.priority);
	let displayStatus = $derived(serverStatus || (completed ? 'Done' : savedStatus || data.task.status));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleComplete() {
		error = '';
		try {
			const res = await completeTask(data.task.id);
			completed = true;
			if (res.data) {
				serverStatus = res.data.status;
				if (res.data.owner) serverOwner = res.data.owner;
			}
			message = t('Tugas ditandai selesai.');
		} catch {
			error = t('Gagal menyelesaikan tugas.');
		}
	}

	function openAssign() {
		assignOwner = localOwner;
		error = '';
		assignOpen = true;
	}

	async function handleAssign() {
		error = '';
		if (!assignOwner.trim()) {
			error = t('Nama penanggung jawab wajib diisi.');
			return;
		}
		assigning = true;
		try {
			const res = await assignTask(data.task.id, assignOwner.trim());
			reassigned = true;
			if (res.data) {
				serverOwner = res.data.owner;
				serverStatus = res.data.status;
			}
			message = t('Penanggung jawab diperbarui.');
			assignOpen = false;
		} catch {
			error = t('Gagal mengubah penanggung jawab.');
		} finally {
			assigning = false;
		}
	}

	function openEdit() {
		editTitle = localTitle;
		editStatus = savedStatus || data.task.status;
		editPriority = localPriority;
		editOwner = localOwner;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editTitle.trim()) {
			error = t('Judul tugas wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await updateTask(data.task.id, {
				title: editTitle.trim(),
				status: editStatus.trim() as (typeof data.task.status),
				priority: editPriority.trim() as (typeof data.task.priority),
				owner: editOwner.trim()
			});
			savedTitle = res.data.title;
			savedStatus = res.data.status;
			savedPriority = res.data.priority;
			savedOwner = res.data.owner;
			message = t('Tugas diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan tugas.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus tugas ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteTask(data.task.id);
			goto('/tasks');
		} catch {
			error = t('Gagal menghapus tugas.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.task.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.task.id} eyebrow={t('Task detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{localTitle}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.task.module} · {data.project?.name ?? data.task.projectId}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Prioritas')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{localPriority}</strong></CardContent>
			</Card>
		</CardContent>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={editTitle} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Prioritas')}
						<Input bind:value={editPriority} />
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

	<div class="grid gap-4 lg:grid-cols-2">
		<Card class="lg:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Konteks Eksekusi')}</CardTitle>
					<CardDescription class="mt-2 leading-relaxed">{data.task.description}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2">
					<Button variant="outline" onclick={() => (assignOpen ? (assignOpen = false) : openAssign())}>{assignOpen ? t('Batal') : t('Tugaskan tugas')}</Button>
					<Button onclick={handleComplete}>{completed ? t('Selesai') : t('Tandai selesai')}</Button>
				</div>
				{#if assignOpen}
					<div class="mt-3 flex flex-wrap items-end gap-2">
						<label class="grid gap-1 text-sm font-semibold">
							{t('Penanggung jawab')}
							<Input bind:value={assignOwner} placeholder="Operations Lead" class="min-w-[220px]" />
						</label>
						<Button disabled={assigning} onclick={handleAssign}>{assigning ? t('Menyimpan...') : t('Tugaskan')}</Button>
					</div>
				{/if}
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid grid-cols-2 gap-2 md:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Pemilik')} <strong class="mt-1 block text-sm font-bold text-foreground">{localOwner}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Jatuh tempo')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.task.due}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Modul')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.task.module}</strong></div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Proyek')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.task.projectId}</strong></div>
			</CardContent>
		</Card>

		<Card class="lg:col-span-2">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Daftar Periksa')}</Badge>
				<CardTitle class="mt-3 text-2xl font-bold tracking-tight">{t('Pekerjaan yang Diperlukan')}</CardTitle>
			</CardHeader>
			<CardContent class="grid grid-cols-2 gap-2 md:grid-cols-4">
					{#each data.task.checklist ?? [] as item}
					<div class={completed || item.done ? 'rounded-lg border border-primary/30 bg-primary/10 p-3' : 'rounded-lg border bg-muted/40 p-3'}>
						<span class="text-xs font-bold text-muted-foreground">{completed || item.done ? t('Selesai') : t('Menunggu')}</span>
						<strong class="mt-1 block text-sm font-bold">{item.label}</strong>
					</div>
				{/each}
			</CardContent>
			<CardContent class="grid gap-2 p-0">
				{#if reassigned}<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-semibold text-primary">{t('Tugas ditugaskan di backend.')}</p>{/if}
				{#if completed}<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-semibold text-primary">{t('Tugas diselesaikan di backend.')}</p>{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>