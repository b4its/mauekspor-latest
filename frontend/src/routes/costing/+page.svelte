<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { costingScenarios as seedScenarios, projects as seedProjects } from '$lib/data/trade';
	import { listCostingScenarios, compareCostingScenarios, type CostingCompare } from '$lib/api/costing';
import { listTradeProjects } from '$lib/api/trade-projects';
import { csvExportUrl } from '$lib/api/client';
import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Ready', 'Needs Review', 'Draft'];
	let activeFilter = $state('All');
	let query = $state('');

	let costingScenarios = createRemoteList(listCostingScenarios, seedScenarios);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		costingScenarios.load();
		projects.load();
	});

	let filteredScenarios = $derived(
		costingScenarios.items.filter((scenario) => {
			const matchesFilter = activeFilter === 'All' || scenario.status === activeFilter;
			const matchesQuery = [scenario.id, scenario.title, scenario.destination, scenario.incoterm, scenario.projectId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let totalLanded = $derived(costingScenarios.items.reduce((sum, item) => sum + item.landedCost, 0));
	let averageMargin = $derived(Math.round(costingScenarios.items.reduce((sum, item) => sum + item.margin, 0) / (costingScenarios.items.length || 1)));

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}

	// ---------- Compare mode ----------
	let selected = $state<string[]>([]);
	let compareResult = $state<CostingCompare | null>(null);
	let comparing = $state(false);
	let compareError = $state('');

	function toggleSelect(id: string) {
		selected = selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id];
	}

	async function runCompare() {
		compareError = '';
		comparing = true;
		try {
			const res = await compareCostingScenarios(selected);
			compareResult = res.data;
		} catch {
			compareError = 'Gagal membandingkan skenario costing.';
		} finally {
			comparing = false;
		}
	}

	function columnLabel(col: string) {
		const labels: Record<string, string> = {
			id: 'ID',
			title: 'Skenario',
			destination: 'Negara tujuan',
			incoterm: 'Incoterm',
			margin: 'Margin (%)',
			exchangeRate: 'Kurs (IDR/USD)',
			exwPrice: 'EXW (USD)',
			fobPrice: 'FOB (USD)',
			cifPrice: 'CIF (USD)',
			status: 'Status'
		};
		return labels[col] ?? col;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{t('Costing')} | MauEkspor</title>
</svelte:head>

<AppShell title="Costing" eyebrow={t('Incoterm pricing and landed cost')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Kontrol biaya')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Pisahkan harga penjual, estimasi freight, dan biaya landed pembeli.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">{t('Model EXW, FOB, CIF, DAP, validitas freight, eksposur kurs, biaya tujuan, cadangan pajak, dan margin sebelum penerimaan kutipan.')}</CardDescription>
		</CardHeader>
<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button href="/costing/create">{t('Create scenario')}</Button>
			<Button href={csvExportUrl('/costing/export.csv')} variant="outline">{t('Ekspor CSV')}</Button>
			<Button variant="secondary" disabled={selected.length < 2 || comparing} onclick={runCompare}>
				{comparing ? t('Membandingkan...') : `${t('Bandingkan')} (${selected.length})`}
			</Button>
			<Badge variant="secondary">{t('Avg margin')} {averageMargin}%</Badge>
		</CardContent>
	</Card>

	{#if compareError}
		<p class="mt-3 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{compareError}</p>
	{/if}

	{#if compareResult && compareResult.rows.length > 0}
		<Card>
			<CardHeader>
				<div class="flex flex-wrap items-center justify-between gap-3">
					<div>
						<CardTitle>{t('Perbandingan')} {compareResult.count} {t('skenario')}</CardTitle>
						<CardDescription>
							{#if compareResult.recommendation}
								Rekomendasi: <strong>{compareResult.recommendation.title}</strong> — {compareResult.recommendation.reason}
							{:else}
								Pilih minimal 2 skenario untuk rekomendasi otomatis.
							{/if}
						</CardDescription>
					</div>
					<Button size="sm" variant="outline" onclick={() => (compareResult = null)}>{t('Tutup')}</Button>
				</div>
			</CardHeader>
			<CardContent class="overflow-x-auto p-0">
				<table class="w-full text-sm">
					<thead class="bg-muted/50">
						<tr>
							{#each compareResult.columns as col}
								<th class="px-4 py-2 text-left font-bold">{columnLabel(col)}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each compareResult.rows as row, i}
							<tr class="border-t hover:bg-muted/30">
								{#each row as value, j}
									<td class="px-4 py-2">
										{#if j === 1}
											<a href={`/costing/${String(compareResult!.rows[i][0])}`} class="font-bold underline-offset-2 hover:underline">{String(value)}</a>
										{:else}
											{value}
										{/if}
									</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</CardContent>
		</Card>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search scenario, country, incoterm..." class="max-w-xs" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Skenario')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{costingScenarios.items.length}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total estimasi landed')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(totalLanded)}</strong></CardContent></Card>
		<Card><CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Margin rata-rata')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{averageMargin}%</strong></CardContent></Card>
	</div>

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredScenarios as scenario}
			<Card class="transition-all hover:border-ring/40 hover:shadow-md">
				<label class="block h-full p-5">
					<div class="flex items-center justify-between gap-3">
						<div class="flex items-center gap-2">
							<Checkbox checked={selected.includes(scenario.id)} onCheckedChange={() => toggleSelect(scenario.id)} />
							<Badge variant={toneVariant(statusTone(scenario.status))}>{scenario.status}</Badge>
						</div>
						<strong class="text-2xl font-bold tracking-tight">{scenario.confidence}%</strong>
					</div>
					<a href={`/costing/${scenario.id}`} class="no-underline">
						<h3 class="mt-3 text-2xl font-bold tracking-tight">{scenario.title}</h3>
						<p class="mt-1 text-sm text-muted-foreground">{projectName(scenario.projectId)}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{scenario.incoterm}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Tujuan')}<strong class="mt-1 block text-sm font-bold text-foreground">{scenario.destination}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">FOB<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(scenario.fobPrice)}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Landed')}<strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(scenario.landedCost)}</strong></div>
						</div>
					</a>
				</label>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('Tidak ada skenario costing yang cocok dengan pencarian.')}</div>
		{/each}
	</div>
</AppShell>
