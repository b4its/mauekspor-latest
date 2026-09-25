<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { pipeline as seedPipeline } from '$lib/data/trade';
	import { listComplianceRequirements } from '$lib/api/compliance';
	import { listTradeDocuments } from '$lib/api/documents';
	import { updateTradeProject, deleteTradeProject } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { ComplianceRequirement, TradeDocument } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';
	import { goto } from '$app/navigation';
	import { currency, statusTone } from '$lib/utils/format';

	let { data } = $props();
	let selectedTab = $state('Compliance');
	const tabs = ['Compliance', 'Quotation', 'Documents', 'Shipment'];
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let message = $state('');
	let error = $state('');
	let editName = $state('');
	let editStage = $state('');
	let editReadiness = $state('');
	let editRisk = $state('');
	let savedName = $state('');
	let savedStage = $state('');
	let savedReadiness = $state<number | null>(null);
	let savedRisk = $state('');
	let localName = $derived(savedName || data.project.name);
	let localStage = $derived(savedStage || data.project.stage);
	let localReadiness = $derived(savedReadiness ?? data.project.readiness);
	let localRisk = $derived(savedRisk || data.project.risk);

	let compliance = createRemoteList<ComplianceRequirement>(listComplianceRequirements, []);
	let docs = createRemoteList<TradeDocument>(listTradeDocuments, []);
	$effect(() => {
		compliance.load();
		docs.load();
	});

	let complianceTasks = $derived(
		compliance.items
			.filter((task) => task.projectId === data.project.id)
			.map((task) => ({ name: task.title, owner: task.owner, status: task.status, due: task.due }))
	);
	let documents = $derived(
		docs.items
			.filter((doc) => doc.projectId === data.project.id)
			.map((doc) => ({ name: doc.type, score: doc.validationScore, status: doc.status }))
	);

	let pipeline = $derived(
		seedPipeline.map((item) => {
			if (item.label === 'Compliance' && complianceTasks.length > 0) {
				const verified = complianceTasks.filter((task) => task.status === 'Verified').length;
				return { ...item, value: Math.round((verified / complianceTasks.length) * 100) };
			}
			if (item.label === 'Documents' && documents.length > 0) {
				const approved = documents.filter((doc) => doc.status === 'Approved').length;
				return { ...item, value: Math.round((approved / documents.length) * 100) };
			}
			return item;
		})
	);

	function trTab(x: string) {
		return t(x === 'Compliance' ? 'Kepatuhan' : x === 'Quotation' ? 'Kutipan' : x === 'Documents' ? 'Dokumen' : 'Pengiriman');
	}

	function trMilestone(m: string) {
		return t(m === 'Cargo Ready' ? 'Kargo Siap' : m === 'Picked Up' ? 'Diambil' : m === 'Customs Submitted' ? 'Bea Cukai Diajukan' : m === 'Loaded' ? 'Dimuat' : m === 'Departed' ? 'Berangkat' : 'Tiba');
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	function openEdit() {
		editName = data.project.name;
		editStage = data.project.stage;
		editReadiness = String(data.project.readiness);
		editRisk = data.project.risk;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editName.trim()) {
			error = t('Nama proyek wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload: Record<string, string | number> = {};
			if (editName.trim() !== data.project.name) payload.name = editName.trim();
			if (editStage.trim() !== data.project.stage) payload.stage = editStage.trim();
			if (editRisk.trim() !== data.project.risk) payload.risk = editRisk.trim();
			const readinessNum = Number(editReadiness);
			if (!Number.isNaN(readinessNum) && readinessNum !== data.project.readiness) payload.readiness = readinessNum;
			const res = await updateTradeProject(data.project.id, payload);
			savedName = res.data.name;
			savedStage = res.data.stage;
			savedRisk = res.data.risk;
			savedReadiness = res.data.readiness;
			message = t('Proyek diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan proyek.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus proyek ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteTradeProject(data.project.id);
			goto('/trade-projects');
		} catch {
			error = t('Gagal menghapus proyek.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{localName} | MauEkspor</title>
</svelte:head>

<AppShell title={data.project.id} eyebrow={localName}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(localRisk))}>{localRisk} {t('risiko')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{localName}
				</CardTitle>
				<CardDescription class="mt-2">{data.project.product} for {data.project.buyer} in {data.project.country}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Nilai kutipan')}</span>
				<strong class="mt-1 block text-3xl font-bold tracking-tight">{currency.format(data.project.value)}</strong>
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
						{t('Nama')}
						<Input bind:value={editName} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Tahap')}
						<Input bind:value={editStage} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kesiapan (%)')}
						<Input type="number" bind:value={editReadiness} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Risiko')}
						<Input bind:value={editRisk} />
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
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>{t('Pipeline Eksekusi')}</CardTitle>
				<Badge variant="secondary">{t('Tahap saat ini:')} {localStage} · {localReadiness}%</Badge>
			</CardHeader>
			<CardContent class="grid gap-4 sm:grid-cols-3">
				{#each pipeline as item}
					<div class="rounded-lg border bg-muted/30 p-3.5">
						<div class="flex items-center justify-between gap-3">
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{item.label}</span>
							<strong class="text-sm font-bold">{item.value}%</strong>
						</div>
						<Progress value={item.value} class="mt-3" />
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>{t('Commercial Terms')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Incoterm')}</span>
					<strong class="text-sm font-bold">{data.project.incoterm}</strong>
				</div>
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Payment')}</span>
					<strong class="text-sm font-bold">{data.project.payment}</strong>
				</div>
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Rute pelabuhan')}</span>
					<strong class="text-sm font-bold">{data.project.port}</strong>
				</div>
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('ETA')}</span>
					<strong class="text-sm font-bold">{data.project.eta}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>{t('Klasifikasi')}</CardTitle></CardHeader>
			<CardContent>
				<div class="rounded-xl border bg-primary/10 p-4">
					<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('HS yang Direkomendasikan')}</span>
					<strong class="mt-2 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{data.project.hsCode}</strong>
					<p class="mt-3 text-sm leading-relaxed text-muted-foreground">
						{t('Keyakinan AI 84%. Membutuhkan konfirmasi manusia sebelum pembuatan dokumen.')}
					</p>
				</div>
			</CardContent>
		</Card>
	</div>

	<Card class="mt-4">
		<CardContent class="pt-(--card-spacing)">
			<div class="mb-4 flex flex-wrap gap-2.5">
				{#each tabs as tab}
					<Button variant={selectedTab === tab ? 'default' : 'outline'} onclick={() => (selectedTab = tab)}>{trTab(tab)}</Button>
				{/each}
			</div>

			{#if selectedTab === 'Compliance'}
				<div class="grid gap-2.5">
					{#if complianceTasks.length === 0}
						<p class="rounded-lg border bg-muted/30 p-3.5 text-sm text-muted-foreground">{t('Belum ada persyaratan kepatuhan untuk proyek ini.')}</p>
					{/if}
					{#each complianceTasks as task}
						<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5">
							<div>
								<strong class="block text-sm font-bold">{task.name}</strong>
								<span class="mt-1 block text-xs font-semibold text-muted-foreground">{task.owner} - {t('jatuh tempo')} {task.due}</span>
							</div>
							<Badge variant={toneVariant(statusTone(task.status))}>{task.status}</Badge>
						</div>
					{/each}
				</div>
			{:else if selectedTab === 'Documents'}
				<div class="grid gap-2.5">
					{#if documents.length === 0}
						<p class="rounded-lg border bg-muted/30 p-3.5 text-sm text-muted-foreground">{t('Belum ada dokumen untuk proyek ini.')}</p>
					{/if}
					{#each documents as doc}
						<div class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3.5">
							<div class="w-full max-w-sm">
								<strong class="block text-sm font-bold">{doc.name}</strong>
								<Progress value={doc.score} class="mt-2.5" />
							</div>
							<Badge variant={toneVariant(statusTone(doc.status))}>{doc.status}</Badge>
						</div>
					{/each}
				</div>
			{:else if selectedTab === 'Quotation'}
				<div class="rounded-xl border bg-muted/30 p-5">
					<h3 class="text-2xl font-bold tracking-tight">{data.project.incoterm}</h3>
					<p class="mt-2 leading-relaxed text-muted-foreground">
						{currency.format(data.project.value)} {t('berlaku hingga')} 12 Sep 2026. {t('Termasuk pengepakan ekspor, penanganan asal, dan asumsi freight laut dasar.')}
					</p>
					<Button class="mt-4" onclick={openEdit}>{t('Siapkan revisi')}</Button>
				</div>
			{:else}
				<div class="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-6">
					{#each ['Cargo Ready', 'Picked Up', 'Customs Submitted', 'Loaded', 'Departed', 'Arrived'] as milestone, index}
						<div
							class={index < 3
								? 'rounded-lg border border-primary/40 bg-primary/10 p-3.5 text-center text-sm font-bold text-primary'
								: 'rounded-lg border bg-muted/30 p-3.5 text-center text-sm font-bold'}
						>
							{trMilestone(milestone)}
						</div>
					{/each}
				</div>
			{/if}
		</CardContent>
	</Card>
</AppShell>