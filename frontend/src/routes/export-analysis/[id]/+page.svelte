<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { reanalyzeExportAnalysis, deleteExportAnalysis, getRegulationRecommendations, runRegulationCheck, analysisPdfUrl } from '$lib/api/export-analysis';
	import { updateProduct, getProduct } from '$lib/api/products';
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
	let regRunning = $state(false);

	// ---------- Inline Compliance Editor ----------
	let editMode = $state(false);
	let savingEdit = $state(false);
	let editError = $state('');
	let editSaved = $state(false);
	let packaging = $state('');
	let material = $state('');
	let description = $state('');
	let qualitySpecs = $state<Record<string, string>>({});

	function openEditor() {
		const product = data.product as Record<string, unknown> | undefined;
		packaging = String((product?.packaging as string) ?? '');
		material = String((product?.material_composition as string) ?? '');
		description = String((product?.description as string) ?? '');
		const specs = (product?.quality_specs ?? {}) as Record<string, unknown>;
		qualitySpecs = Object.fromEntries(Object.entries(specs).map(([k, v]) => [k, String(v)]));
		editMode = true;
		editSaved = false;
	}

	function addSpecRow() {
		qualitySpecs = { ...qualitySpecs, '': '' };
	}

	function removeSpecRow(key: string) {
		const next = { ...qualitySpecs };
		delete next[key];
		qualitySpecs = next;
	}

	async function saveComplianceFix() {
		editError = '';
		savingEdit = true;
		try {
			const cleaned: Record<string, string> = {};
			for (const [k, v] of Object.entries(qualitySpecs)) {
				if (k.trim() && v.trim()) cleaned[k.trim()] = v.trim();
			}
			await updateProduct(data.analysis.productId, {
				packaging,
				material_composition: material,
				description,
				quality_specs: cleaned
			});
			data.product = (await getProduct(data.analysis.productId)).data;
			editSaved = true;
			editMode = false;
		} catch {
			editError = t('Gagal menyimpan perbaikan produk.');
		} finally {
			savingEdit = false;
		}
	}

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
			error = t('Gagal menjalankan ulang analisis.');
		} finally {
			rerunning = false;
		}
	}

	async function handleDelete() {
		if (!confirm(t('Hapus analisis ini?'))) return;
		error = '';
		deleting = true;
		try {
			await deleteExportAnalysis(data.analysis.id);
			window.location.href = '/export-analysis';
		} catch {
			error = t('Gagal menghapus analisis.');
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

	async function handleRunRegCheck() {
		error = '';
		regRunning = true;
		try {
			data.analysis = (await runRegulationCheck(data.analysis.id)).data;
			showRegs = true;
			regs = (await getRegulationRecommendations(data.analysis.id, 'id')).data;
		} catch {
			error = t('Gagal menjalankan pemeriksaan regulasi.');
		} finally {
			regRunning = false;
		}
	}
</script>

<svelte:head>
	<title>{data.analysis.productName} Export Analysis | MauEkspor</title>
</svelte:head>

<AppShell title={data.analysis.id} eyebrow={t('Market & compliance analysis detail')}>
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
				<CardDescription class="mt-2">HS <a class="font-bold text-primary hover:underline" href={`/hs-codes/${data.analysis.hsCode}`}>{data.analysis.hsCode}</a> - {t('keyakinan klasifikasi')} {data.analysis.confidence}%.</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Readiness score')}</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{data.analysis.score}</strong>
				<small class="text-xs font-bold text-muted-foreground">/ 100</small>
			</div>
		</div>
	</Card>

	{#if productChanged}
		<div class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm font-bold text-amber-700">
			{t('Produk berubah sejak analisis dijalankan. Jalankan ulang (re-analyze) untuk memperbarui snapshot produk & skor kepatuhan.')}
		</div>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Ringkasan kepatuhan')}</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl leading-relaxed">{data.analysis.summary}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/countries/${data.analysis.destination}`}>{t('Regulasi negara')}</Button>
					<Button variant="outline" href={analysisPdfUrl(data.analysis.id)}>{t('Unduh PDF')}</Button>
					<Button variant="outline" href={`/export-analysis/${data.analysis.id}/regulation-recommendations`}>{t('Lihat rekomendasi')}</Button>
					<Button variant="outline" onclick={handleRegs}>{t('Panduan 10 bagian')}</Button>
					<Button variant="outline" disabled={regRunning} onclick={handleRunRegCheck}>
						{regRunning ? t('Memeriksa regulasi...') : t('Periksa regulasi')}
					</Button>
					<Button variant="outline" disabled={rerunning} onclick={handleRerun}>
						{rerunning ? t('Menganalisis ulang...') : t('Analisis ulang')}
					</Button>
					<Button variant="destructive" disabled={deleting} onclick={handleDelete}>{t('Hapus')}</Button>
				</div>
			</CardHeader>
			{#if error}
				<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kode HS')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.hsCode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Permintaan pasar')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.marketDemand ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Keyakinan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.confidence}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Bea masuk')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.analysis.duties ?? '—'}</strong>
				</div>
			</CardContent>
		</Card>

		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Isu kepatuhan')} ({issues.length})</CardTitle>
					<CardDescription>{t('Ditemukan oleh compliance checker (bahan, spesifikasi, kemasan).')}</CardDescription>
				</div>
				<Button variant="outline" size="sm" onclick={openEditor} disabled={!data.product}>{t('Perbaiki kepatuhan')}</Button>
			</CardHeader>
			<CardContent class="grid gap-2.5">
				{#if issues.length === 0}
					<p class="rounded-lg border bg-muted/30 p-4 text-sm font-semibold text-muted-foreground">
						{t('Tidak ada isu kepatuhan. Produk siap untuk analisis pasar.')}
					</p>
				{/if}
				{#each issues as issue (issue.rule_key + issue.type)}
					<div class="rounded-lg border bg-muted/30 p-3.5">
						<div class="flex flex-wrap items-center justify-between gap-2">
							<strong class="text-sm">{issue.type}{issue.rule_key ? ` — ${issue.rule_key}` : ''}</strong>
							<Badge variant={severityTone(issue.severity)}>{issue.severity ?? 'minor'}</Badge>
						</div>
						{#if issue.your_value}
							<p class="mt-1.5 text-xs text-muted-foreground"><b>{t('Nilai saat ini:')}</b> {issue.your_value}</p>
						{/if}
						{#if issue.required_value}
							<p class="mt-1 text-xs text-muted-foreground"><b>{t('Diperlukan:')}</b> {issue.required_value}</p>
						{/if}
						{#if issue.description}
							<p class="mt-1 text-xs text-muted-foreground">{issue.description}</p>
						{/if}
					</div>
				{/each}

				{#if editMode}
					<div class="mt-2 rounded-xl border bg-background p-4">
						<h4 class="text-sm font-bold">{t('Editor produk (perbaikan kepatuhan)')}</h4>
						<p class="mt-1 text-xs text-muted-foreground">
							{t('Perbaiki data produk lalu klik "Simpan & Re-Analyze" agar snapshot dan skor diperbarui.')}
						</p>
						{#if editError}
							<p class="mt-2 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{editError}</p>
						{/if}
						{#if editSaved}
							<p class="mt-2 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Produk diperbarui. Jalankan Re-analyze untuk skor terbaru.')}</p>
						{/if}
						<div class="mt-3 grid gap-3 sm:grid-cols-2">
							<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
								{t('Kemasan')}
								<Input bind:value={packaging} placeholder="contoh: ISPM-15 pallet" />
							</label>
							<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
								{t('Komposisi bahan')}
								<Input bind:value={material} placeholder="contoh: 100% natural fiber" />
							</label>
						</div>
						<label class="mt-3 grid gap-1.5 text-xs font-bold text-muted-foreground">
							{t('Deskripsi')}
							<Textarea bind:value={description} rows={2} />
						</label>
						<div class="mt-3">
							<div class="flex items-center justify-between">
								<span class="text-xs font-bold text-muted-foreground">{t('Spesifikasi kualitas')}</span>
								<Button type="button" size="sm" variant="outline" onclick={addSpecRow}>{t('+ Tambah')}</Button>
							</div>
							<div class="mt-2 grid gap-2">
								{#each Object.entries(qualitySpecs) as [key, value]}
									<div class="flex gap-2">
										<Input
											placeholder={t('Label (mis. Allergen)')}
											value={key}
											oninput={(e) => {
												const newKey = (e.currentTarget as HTMLInputElement).value;
												const next: Record<string, string> = {};
												for (const [k, v] of Object.entries(qualitySpecs)) {
													next[k === key ? newKey : k] = v;
												}
												qualitySpecs = next;
											}}
										/>
										<Input
											placeholder={t('Nilai')}
											value={value}
											oninput={(e) => {
												qualitySpecs = { ...qualitySpecs, [key]: (e.currentTarget as HTMLInputElement).value };
											}}
										/>
										<Button type="button" size="icon" variant="ghost" onclick={() => removeSpecRow(key)}>✕</Button>
									</div>
								{/each}
							</div>
						</div>
						<div class="mt-4 flex flex-wrap gap-2">
							<Button type="button" variant="outline" onclick={() => (editMode = false)}>{t('Batal')}</Button>
							<Button type="button" onclick={saveComplianceFix} disabled={savingEdit}>
								{savingEdit ? t('Menyimpan...') : t('Simpan perubahan produk')}
							</Button>
						</div>
					</div>
				{/if}
			</CardContent>
		</Card>

		{#if typeof data.analysis.recommendations === 'string' && (data.analysis.recommendations as string).length > 0}
			<Card>
				<CardHeader>
					<Badge variant="secondary">{t('Rekomendasi')}</Badge>
					<CardTitle>{t('Langkah perbaikan')}</CardTitle>
				</CardHeader>
				<CardContent>
					<ul class="grid gap-2">
						{#each (data.analysis.recommendations as string).split('\n').filter((line: string) => line.trim()) as line}
							<li class="flex items-start gap-2 rounded-lg border bg-muted/30 p-2.5 text-sm">
								<span class="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary"></span>
								<span class="leading-relaxed">{line.replace(/^\d+\.\s*/, '')}</span>
							</li>
						{/each}
					</ul>
				</CardContent>
			</Card>
		{/if}

		{#if snapshot && Object.keys(snapshot).length > 0}
			<Card>
				<CardHeader>
					<CardTitle>{t('Snapshot produk')}</CardTitle>
					<CardDescription>{t('Data produk saat analisis dijalankan (audit trail).')}</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-2 text-xs">
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">{t('Nama')}</span><b>{snapshot.name}</b></div>
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">{t('Kategori')}</span><b>{snapshot.category}</b></div>
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">HS</span><b>{snapshot.hs ?? snapshot.hs_code}</b></div>
					<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">SKU</span><b>{snapshot.sku ?? '—'}</b></div>
					{#if snapshot.packaging}
						<div class="flex justify-between gap-3 rounded-lg border bg-muted/30 p-2.5"><span class="text-muted-foreground">{t('Kemasan')}</span><b>{snapshot.packaging}</b></div>
					{/if}
				</CardContent>
			</Card>
		{/if}

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">{t('Catatan AI')}</Badge>
				<CardTitle>{t('Tindakan terbaik berikutnya')}</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					{t('Perbaiki isu kepatuhan, lampirkan bukti, lalu lanjutkan ke costing & katalog. Gunakan tombol Re-analyze setelah memperbarui data produk agar snapshot dan skor terbaru.')}
				</p>
			</CardContent>
		</Card>
	</div>

	{#if showRegs}
		<Card class="mt-4">
			<CardHeader class="flex-row items-center justify-between">
				<CardTitle>{t('Panduan regulasi (10 bagian)')}</CardTitle>
				<Button variant="outline" size="sm" onclick={() => (showRegs = false)}>{t('Tutup')}</Button>
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
					<p class="text-sm font-semibold text-muted-foreground">{t('Memuat panduan regulasi...')}</p>
				{/if}
			</CardContent>
		</Card>
	{/if}
</AppShell>
