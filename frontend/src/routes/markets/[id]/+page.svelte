<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { refreshMarketInsight, updateMarketInsight, deleteMarketInsight } from '$lib/api/markets';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let refreshed = $state(false);
	let refreshing = $state(false);
	let error = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let message = $state('');
	let editCountry = $state('');
	let editStatus = $state('');
	let editScore = $state('');
	let savedCountry = $state('');
	let savedStatus = $state('');
	let savedScore = $state<number | null>(null);
	let serverScore = $state<number | null>(null);
	let serverStatus = $state('');
	let localCountry = $derived(savedCountry || data.market.country);
	let localStatus = $derived(serverStatus || savedStatus || data.market.status);
	let selectedScenario = $state('Base');
	const scenarios = ['Base', 'Optimistic', 'Conservative'];

	function trScenario(s: string) {
		return t(s === 'Base' ? 'Dasar' : s === 'Optimistic' ? 'Optimis' : 'Konservatif');
	}

	let displayScore = $derived(
		selectedScenario === 'Optimistic'
			? Math.min((serverScore ?? savedScore ?? data.market.marketScore) + 6, 100)
			: selectedScenario === 'Conservative'
				? Math.max((serverScore ?? savedScore ?? data.market.marketScore) - 8, 0)
				: refreshed
					? Math.min((serverScore ?? savedScore ?? data.market.marketScore) + 2, 100)
					: (serverScore ?? savedScore ?? data.market.marketScore)
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleRefresh() {
		error = '';
		refreshing = true;
		try {
			const res = await refreshMarketInsight(data.market.id);
			refreshed = true;
			if (res.data) {
				if (typeof res.data.marketScore === 'number') serverScore = res.data.marketScore;
				serverStatus = res.data.status;
			}
			message = t('Insight pasar diperbarui.');
		} catch {
			error = t('Gagal refresh insight pasar.');
		} finally {
			refreshing = false;
		}
	}

	function openEdit() {
		editCountry = data.market.country;
		editStatus = data.market.status;
		editScore = String(data.market.marketScore);
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editCountry.trim()) {
			error = t('Negara wajib diisi.');
			return;
		}
		saving = true;
		try {
			const payload: Record<string, string | number> = {};
			if (editCountry.trim() !== data.market.country) payload.country = editCountry.trim();
			if (editStatus.trim() !== data.market.status) payload.status = editStatus.trim();
			const scoreNum = Number(editScore);
			if (!Number.isNaN(scoreNum) && scoreNum !== data.market.marketScore) payload.marketScore = scoreNum;
			const res = await updateMarketInsight(data.market.id, payload);
			savedCountry = res.data.country;
			savedStatus = res.data.status;
			savedScore = res.data.marketScore;
			message = t('Insight pasar diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan insight pasar.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus insight pasar ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteMarketInsight(data.market.id);
			goto('/markets');
		} catch {
			error = t('Gagal menghapus insight pasar.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{localCountry} Market | MauEkspor</title>
</svelte:head>

<AppShell title={localCountry} eyebrow={t('Market insight detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(localStatus))}>{localStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.product?.name ?? data.market.productId}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.market.projectId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Market score')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{displayScore}%</strong>
			</div>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Negara')}
						<Input bind:value={editCountry} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Skor pasar')}
						<Input type="number" bind:value={editScore} />
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
					<CardTitle>{t('Market Decision Summary')}</CardTitle>
					<CardDescription>{data.market.entryStrategy ?? '—'}</CardDescription>
				</div>
				<div class="flex flex-wrap items-center gap-2.5">
					<NativeSelect bind:value={selectedScenario} class="w-40">
						{#each scenarios as scenario}
							<option value={scenario}>{trScenario(scenario)}</option>
						{/each}
					</NativeSelect>
					<Button onclick={handleRefresh} disabled={refreshing}>{refreshed ? t('Dimuat ulang') : refreshing ? t('Memuat ulang...') : t('Muat ulang wawasan')}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Import value')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.importValue ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Pertumbuhan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.growth ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tarif/kepatuhan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.tariff ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kompleksitas')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.complianceComplexity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Logistik')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.logisticsFeasibility}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Margin')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.market.estimatedMargin}%</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Peluang')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 p-0 pt-4">
				{#each data.market.opportunities ?? [] as item}
					<span class="rounded-lg bg-primary/10 px-3 py-3 font-bold leading-relaxed text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Risks')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 p-0 pt-4">
				{#each data.market.risks ?? [] as item}
					<span class="rounded-lg bg-orange-500/10 px-3 py-3 font-bold leading-relaxed text-orange-700">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Asal usul bukti')}</Badge>
				<CardTitle>{t('Sumber dan tanggal pengambilan')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.market.sources ?? [] as source}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<strong class="block text-sm font-bold">{source.name}</strong>
							<span class="mt-1 block text-sm text-muted-foreground">{source.date}</span>
						</div>
					{/each}
				</div>
				{#if refreshed}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Insight diperbarui di backend.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>