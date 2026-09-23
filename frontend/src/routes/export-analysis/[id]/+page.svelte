<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { reanalyzeExportAnalysis, deleteExportAnalysis, getRegulationRecommendations } from '$lib/api/export-analysis';
	import type { RegulationRecommendations } from '$lib/api/export-analysis';

	let { data } = $props();

	type Issue = {
		type: string;
		rule_key?: string;
		your_value?: string;
		required_value?: string;
		description?: string;
		severity?: string;
	};

	let issues = $derived((data.analysis.complianceIssues ?? []) as Issue[]);
	let grade = $derived((data.analysis.statusGrade ?? (data.analysis.score >= 80 ? 'Ready' : data.analysis.score >= 50 ? 'Warning' : 'Critical')) as string);
	let productChanged = $derived(data.analysis.productChanged === true);
	let snapshot = $derived((data.analysis.productSnapshot ?? {}) as Record<string, unknown>);

	let rerunning = $state(false);
	let deleting = $state(false);
	let error = $state('');
	let regs = $state<RegulationRecommendations | null>(null);
	let showRegs = $state(false);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	function gradeTone(g: string) {
		if (g === 'Ready') return 'default';
		if (g === 'Warning') return 'outline';
		return 'destructive';
	}

	function severityTone(s?: string) {
		if (s === 'critical') return 'destructive';
		if (s === 'major') return 'outline';
		return 'secondary';
	}

	async function handleRerun() {
		error = '';
		rerunning = true;
		try {
			data.analysis = (await reanalyzeExportAnalysis(data.analysis.id)).data;
		} catch {
			error = 'Gagal menjalankan ulang analisis.';
		} finally {
			rerunning = false;
		}
	}

	async function handleDelete() {
		if (!confirm('Hapus analisis ini?')) return;
		error = '';
		deleting = true;
		try {
			await deleteExportAnalysis(data.analysis.id);
			window.location.href = '/export-analysis';
		} catch {
			error = 'Gagal menghapus analisis.';
		} finally {
			deleting = false;
		}
	}

	async function handleRegs() {
		showRegs = true;
		try {
			regs = (await getRegulationRecommendations(data.analysis.id, 'id')).data;
		} catch {
			regs = null;
		}
	}
</script>

<svelte:head>
	<title>{data.analysis.productName} Export Analysis | MauEkspor</title>
</svelte:head>

<AppShell title={data.analysis.id} eyebrow="Market & compliance analysis detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<div class="flex flex-wrap gap-2">
					<Badge variant={toneVariant(statusTone(data.analysis.status))}>{data.analysis.status}</Badge>
					<Badge variant={gradeTone(grade)}>{grade}</Badge>
				</div>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.analysis.productName} to {data.analysis.destination}
				</CardTitle>
				<CardDescription class="mt-2">HS {data.analysis.hsCode} - classification confidence {data.analysis.confidence}%.</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Readiness score</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{data.analysis.score}</strong>
				<small class="text-xs font-bold text-muted-foreground">/ 100</small>
			</div>
		</div>
	</Card>

	{#if productChanged}
		<div class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm font-bold text-amber-700">
			Produk berubah sejak analisis dijalankan. Jalankan ulang (re-analyze) untuk memperbarui snapshot produk & skor kepatuhan.
		</div>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Compliance summary</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl leading-relaxed">{data.analysis.summary}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/export-analysis/${data.analysis.id}/regulation-recommendations`}>View recommendations</Button>
					<Button variant="outline" onclick={handleRegs}>10-section guidance</Button>
					<Button variant="outline" disabled={rerunning} onclick={handleRerun}>
						{rerunning ? 'Re-analyzing...' : 'Re-analyze'}
					</Button>
					<Button variant="destructive" disabled={deleting} onclick={handleDelete}>Delete</Button>
				</div>
			</CardHeader>
			{#if error}
				<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					HS Code <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.hsCode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Market demand <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.marketDemand ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Confidence <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.confidence}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Duties <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.duties ?? '—'}</strong>
				</div>
			</CardContent>
		</Card>

		<Card class="md:col-span-2">
			<CardHeader>
				<CardTitle>Compliance issues ({issues.length})</CardTitle>
				<CardDescription>Ditemukan oleh compliance checker (bahan, spesifikasi, kemasan).</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-2.5">
				{#if issues.length === 0}
					<p class="rounded-lg border bg-muted/30 p-4 text-sm font-semibold text-muted-foreground">
						Tidak ada isu kepatuhan. Produk siap untuk analisis pasar.
					</p>
				{/if}
				{#each issues as issue (issue.rule_key + issue.type)}
					<div class="rounded-lg border bg-muted/30 p-3.5">
						<div class="flex flex-wrap items-center justify-between gap-2">
							<strong class="text-sm">{issue.type}{issue.rule_key ? ` — ${issue.rule_key}` : ''}</strong>
							<Badge variant={severityTone(issue.severity)}>{issue.severity ?? 'minor'}</Badge>
						</div>
						{#if issue.your_value}
							<p class="mt-1.5 text-xs text-muted-foreground"><b>Nilai saat ini:</b> {issue.your_value}</p>
						{/if}
						{#if issue.required_value}
							<p class="mt-1 text-xs text-muted-foreground"><b>Diperlukan:</b> {issue.required_value}</p>
						{/if}
						{#if issue.description}
							<p class="mt-1 text-xs text-muted-foreground">{issue.description}</p>
						{/if}
					</div>
				{/each}
			</CardContent>
		</Card>

		{#if snapshot && Object.keys(snapshot).length > 0}
			<Card>
				<CardHeader>
					<CardTitle>Product snapshot</CardTitle>
					<CardDescription>Data produk saat analisis dijalankan (audit trail).</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-2 text-xs">
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">Nama</span><b>{snapshot.name}</b></div>
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">Kategori</span><b>{snapshot.category}</b></div>
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">HS</span><b>{snapshot.hs ?? snapshot.hs_code}</b></div>
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">SKU</span><b>{snapshot.sku ?? '—'}</b></div>
					{#if snapshot.packaging}
						<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">Kemasan</span><b>{snapshot.packaging}</b></div>
					{/if}
				</CardContent>
			</Card>
		{/if}

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">AI note</Badge>
				<CardTitle>Next best action</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					Perbaiki isu kepatuhan, lampirkan bukti, lalu lanjutkan ke costing & katalog.
					Gunakan tombol Re-analyze setelah memperbarui data produk agar snapshot dan skor terbaru.
				</p>
			</CardContent>
		</Card>
	</div>

	{#if showRegs}
		<Card class="mt-4">
			<CardHeader class="flex-row items-center justify-between">
				<CardTitle>Regulation guidance (10 sections)</CardTitle>
				<Button variant="outline" size="sm" onclick={() => (showRegs = false)}>Tutup</Button>
			</CardHeader>
			<CardContent class="grid gap-3 md:grid-cols-2">
				{#if regs}
					{#each regs.sections as section}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<strong class="text-sm">{section.title}</strong>
							<p class="mt-1 text-xs leading-relaxed text-muted-foreground">{section.body}</p>
						</div>
					{/each}
				{:else}
					<p class="text-sm font-semibold text-muted-foreground">Memuat panduan regulasi...</p>
				{/if}
			</CardContent>
		</Card>
	{/if}
</AppShell>
