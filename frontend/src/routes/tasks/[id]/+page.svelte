<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { completeTask, assignTask } from '$lib/api/tasks';
	import { t } from '$lib/i18n.svelte';
	let { data } = $props();
	let completed = $state(false);
	let reassigned = $state(false);
	let error = $state('');
	let displayStatus = $derived(completed ? 'Done' : data.task.status);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleComplete() {
		error = '';
		try {
			await completeTask(data.task.id);
			completed = true;
		} catch {
			error = t('Gagal menyelesaikan tugas.');
		}
	}

	async function handleAssign() {
		error = '';
		try {
			await assignTask(data.task.id, 'Operations Lead');
			reassigned = true;
		} catch {
			error = t('Gagal mengubah penanggung jawab.');
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
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{data.task.title}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{data.task.module} · {data.project?.name ?? data.task.projectId}</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Prioritas')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{data.task.priority}</strong></CardContent>
			</Card>
		</CardContent>
	</Card>

	<div class="grid gap-4 lg:grid-cols-2">
		<Card class="lg:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Konteks Eksekusi')}</CardTitle>
					<CardDescription class="mt-2 leading-relaxed">{data.task.description}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2">
					<Button variant="outline" onclick={handleAssign}>{reassigned ? t('Ditugaskan') : t('Tugaskan tugas')}</Button>
					<Button onclick={handleComplete}>{completed ? t('Selesai') : t('Tandai selesai')}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid grid-cols-2 gap-2 md:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Pemilik')} <strong class="mt-1 block text-sm font-bold text-foreground">{reassigned ? 'Operations Lead' : data.task.owner}</strong></div>
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
				{#each data.task.checklist as item}
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