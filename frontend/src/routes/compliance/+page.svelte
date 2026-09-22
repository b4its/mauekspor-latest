<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { complianceRequirements as seedRequirements, projects as seedProjects } from '$lib/data/trade';
	import { listComplianceRequirements, createComplianceRequirement } from '$lib/api/compliance';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';

	const filters = ['All', 'Blocked', 'In Review', 'Evidence Uploaded', 'Verified'];
	let activeFilter = $state('All');
	let query = $state('');
	let message = $state('');
	let showForm = $state(false);
	let saving = $state(false);
	let formError = $state('');
	let fTitle = $state('');
	let fCategory = $state('');
	let fSeverity = $state('Medium');
	let fOwner = $state('');
	let fSource = $state('');
	let fRequiredEvidence = $state('');
	let error = $state('');

	let complianceRequirements = createRemoteList(listComplianceRequirements, seedRequirements);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	$effect(() => {
		complianceRequirements.load();
		projects.load();
	});

	let filteredRequirements = $derived(
		complianceRequirements.items.filter((item) => {
			const matchesFilter = activeFilter === 'All' || item.status === activeFilter;
			const matchesQuery = [item.title, item.category, item.owner, item.source, item.projectId]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesFilter && matchesQuery;
		})
	);

	let criticalCount = $derived(complianceRequirements.items.filter((item) => item.severity === 'Critical').length);
	let verifiedCount = $derived(complianceRequirements.items.filter((item) => item.status === 'Verified').length);

	function projectName(projectId: string) {
		return projects.items.find((project) => project.id === projectId)?.name ?? projectId;
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	function openCreate() {
		fTitle = '';
		fCategory = '';
		fSeverity = 'Medium';
		fOwner = '';
		fSource = '';
		fRequiredEvidence = '';
		formError = '';
		showForm = true;
	}

	async function handleCreate() {
		formError = '';
		if (!fTitle.trim()) {
			formError = t('Judul wajib diisi.');
			return;
		}
		saving = true;
		try {
			await createComplianceRequirement({
				title: fTitle.trim(),
				category: fCategory.trim(),
				severity: fSeverity,
				owner: fOwner.trim(),
				source: fSource.trim(),
				requiredEvidence: fRequiredEvidence.trim()
			});
			await complianceRequirements.load();
			message = `Persyaratan "${fTitle.trim()}" ditambahkan.`;
			showForm = false;
		} catch {
			formError = t('Gagal membuat persyaratan kepatuhan.');
		} finally {
			saving = false;
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredRequirements ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredRequirements?.length ?? 0, paginationPageSize));

</script>

<svelte:head>
	<title>{t('Kepatuhan')} | MauEkspor</title>
</svelte:head>

<AppShell title="Compliance" eyebrow={t('Evidence-based export readiness')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Source-backed workflow')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Turn regulatory gaps into verified action items.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Track source, severity, owner, evidence, human verification, and confidence for each export requirement before documents or quotation are finalized.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button variant="outline" onclick={() => (showForm ? (showForm = false) : openCreate())}>{showForm ? t('Batal') : t('Tambah persyaratan')}</Button>
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Critical')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{criticalCount}</strong></CardContent>
			</Card>
			<Card class="w-fit">
				<CardContent class="p-5"><span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Verified')}</span><strong class="mt-2 block text-3xl font-bold tracking-tight">{verifiedCount}</strong></CardContent>
			</Card>
		</CardContent>
		{#if showForm}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Judul')}
						<Input bind:value={fTitle} placeholder={t('Sertifikat fitosanitasi')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kategori')}
						<Input bind:value={fCategory} placeholder={t('Dokumen')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Severity')}
						<select bind:value={fSeverity} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each ['Low', 'Medium', 'High', 'Critical'] as severity}
								<option value={severity}>{severity}</option>
							{/each}
						</select>
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Owner')}
						<Input bind:value={fOwner} placeholder="compliance" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Sumber')}
						<Input bind:value={fSource} placeholder={t('Peraturan pemerintah')} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Bukti wajib')}
						<Input bind:value={fRequiredEvidence} placeholder={t('Sertifikat resmi')} />
					</label>
				</div>
				{#if formError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{formError}</p>
				{/if}
				<Button class="w-fit" disabled={saving} onclick={handleCreate}>{saving ? t('Menyimpan...') : t('Simpan persyaratan')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if message}
		<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if complianceRequirements.error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{complianceRequirements.error}</p>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search requirement, source, project...')} class="w-[min(390px,100%)]" />
	</div>

	{#if complianceRequirements.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-5 w-16 rounded-full" />
					</div>
					<Skeleton class="mt-4 h-7 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<Skeleton class="mt-4 h-4 w-1/3" />
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as item}
				<Card class="transition-all hover:border-ring/40 hover:shadow-md">
					<a href={`/compliance/${item.id}`} class="block h-full p-5 no-underline">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(item.status))}>{item.status}</Badge>
							<span class={item.severity.toLowerCase() === 'critical' ? 'rounded-full bg-destructive/10 px-2.5 py-0.5 text-xs font-semibold text-destructive' : item.severity.toLowerCase() === 'major' ? 'rounded-full bg-orange-500/10 px-2.5 py-0.5 text-xs font-semibold text-orange-600' : 'rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary'}>{item.severity}</span>
						</div>
						<h3 class="mt-4 text-2xl font-bold tracking-tight">{item.title}</h3>
						<p class="mt-2 text-sm text-muted-foreground">{projectName(item.projectId)}</p>
						<div class="mt-4 grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Category')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.category}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Owner')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.owner}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Due')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.due}</strong></div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Confidence')} <strong class="mt-1 block text-sm font-bold text-foreground">{item.confidence}%</strong></div>
						</div>
						<p class="mt-4 text-xs font-semibold text-muted-foreground">{t('Source:')} {item.source}</p>
					</a>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No compliance requirement matched your search.')}</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredRequirements?.length ?? 0} />

</AppShell>