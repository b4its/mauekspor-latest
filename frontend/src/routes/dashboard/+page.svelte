<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { businessProfiles as seedProfiles, exportAnalyses as seedAnalyses, projects as seedProjects, products as seedProducts, buyerRequests as seedRequests, forwarders as seedForwarders, complianceRequirements as seedCompliance, educationalModules as seedModulesEdu } from '$lib/data/trade';
	import { listBusinessProfiles, getDashboardSummary, type DashboardSummary } from '$lib/api/business-profile';
	import { listExportAnalyses } from '$lib/api/export-analysis';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { listProducts } from '$lib/api/products';
	import { listBuyerRequests } from '$lib/api/buyer-requests';
	import { listForwarders } from '$lib/api/forwarders';
	import { listComplianceRequirements } from '$lib/api/compliance';
	import { listEducationalModulesV2 } from '$lib/api/educational';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import VillagePotentialMap from '$lib/components/VillagePotentialMap.svelte';
	import { t } from '$lib/i18n.svelte';

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	let products = createRemoteList(listProducts, seedProducts);
	let exportAnalyses = createRemoteList(listExportAnalyses, seedAnalyses);
	let buyerRequests = createRemoteList(listBuyerRequests, seedRequests);
	let forwarders = createRemoteList(listForwarders, seedForwarders);
	let compliance = createRemoteList(listComplianceRequirements, seedCompliance);
	let eduModules = createRemoteList(listEducationalModulesV2, seedModulesEdu);

	let hasProfile = $state(true);
	let summaryCounts = $state<DashboardSummary['counts'] | null>(null);
	let summaryError = $state('');

	$effect(() => {
		profiles.load();
		projects.load();
		products.load();
		exportAnalyses.load();
		buyerRequests.load();
		forwarders.load();
		compliance.load();
		eduModules.load();
		getDashboardSummary()
			.then((res) => {
				hasProfile = res.data.has_business_profile;
				summaryCounts = res.data.counts;
				summaryError = '';
			})
			.catch((err) => {
				summaryError = t('Gagal memuat ringkasan dashboard.');
			});
	});

	let profile = $derived(profiles.items[0]);
	let openRisks = $derived(projects.items.filter((project) => project.risk !== 'Low').length);
	let pipelineValue = $derived(projects.items.reduce((sum, project) => sum + project.value, 0));
	let avgConfidence = $derived(
		exportAnalyses.items.length
			? Math.round(exportAnalyses.items.reduce((sum, item) => sum + item.confidence, 0) / exportAnalyses.items.length)
			: 0
	);

	// ---------- Chart data ----------
	let pipelineByStage = $derived(
		Object.entries(
			projects.items.reduce<Record<string, { count: number; value: number }>>((acc, p) => {
				const stage = p.stage || 'Unknown';
				acc[stage] = acc[stage] ?? { count: 0, value: 0 };
				acc[stage].count += 1;
				acc[stage].value += p.value ?? 0;
				return acc;
			}, {})
		)
	);
	let maxStageValue = $derived(Math.max(1, ...pipelineByStage.map(([, s]) => s.value)));

	let complianceBySeverity = $derived(
		Object.entries(
			compliance.items.reduce<Record<string, number>>((acc, r) => {
				const sev = (r.severity as string) || 'Minor';
				acc[sev] = (acc[sev] ?? 0) + 1;
				return acc;
			}, {})
		)
	);
	let complianceTotal = $derived(Math.max(1, compliance.items.length));

	let marketScores = $derived(exportAnalyses.items.slice(0, 5));

	// ---------- Onboarding checklist ----------
	type ChecklistStep = {
		label: string;
		href: string;
		done: boolean;
		detail: string;
	};
	let checklist = $derived<ChecklistStep[]>([
		{
			label: t('Lengkapi profil bisnis'),
			href: '/business-profile',
			done: hasProfile && (profiles.items[0]?.status === 'Complete' || (profiles.items[0]?.readiness ?? 0) >= 80),
			detail: hasProfile ? t('Profil bisnis tersedia') : t('Tambahkan profil & sertifikasi')
		},
		{
			label: t('Tambahkan produk'),
			href: '/products/new',
			done: products.items.length > 0,
			detail: products.items.length > 0 ? `${products.items.length} ${t('produk terdaftar')}` : t('Buat master data produk')
		},
		{
			label: t('Jalankan AI enrichment'),
			href: '/products',
			done: products.items.some((p) => p.status === 'Enriched'),
			detail: products.items.some((p) => p.status === 'Enriched') ? t('HS code & SKU tersedia') : t('Enrich produk untuk HS & SKU')
		},
		{
			label: t('Buat export analysis'),
			href: '/export-analysis/create',
			done: exportAnalyses.items.length > 0,
			detail: exportAnalyses.items.length > 0 ? `${exportAnalyses.items.length} ${t('analisis pasar')}` : t('Analisis kepatuhan & pasar tujuan')
		},
		{
			label: t('Publikasikan katalog'),
			href: '/catalogs',
			done: summaryCounts ? (summaryCounts.catalogs ?? 0) > 0 : false,
			detail: summaryCounts && (summaryCounts.catalogs ?? 0) > 0 ? `${summaryCounts.catalogs} ${t('katalog dibuat')}` : t('Bangun katalog buyer-facing')
		}
	]);
	let checklistDone = $derived(checklist.filter((s) => s.done).length);
	let checklistPercent = $derived(Math.round((checklistDone / checklist.length) * 100));

	function scoreColor(score: number) {
		if (score >= 80) return 'bg-emerald-500';
		if (score >= 50) return 'bg-amber-500';
		return 'bg-red-500';
	}

	function severityColor(sev: string) {
		if (sev === 'Critical') return 'bg-red-500';
		if (sev === 'Major') return 'bg-amber-500';
		return 'bg-emerald-500';
	}

	function badgeVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
		const tone = statusTone(status);
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		if (tone === 'green') return 'default';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{t('Dashboard')} | MauEkspor</title>
</svelte:head>

<AppShell title="Dashboard" eyebrow={t('Export workspace home')}>
	{#if summaryError}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{summaryError}</p>
	{/if}
	<Card class="panel-hero p-5 sm:p-6 md:p-8">
		<div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(260px,320px)] lg:items-start">
			<div>
				<Badge variant="secondary">{t('Selamat datang kembali')}</Badge>
				<CardTitle class="mt-3 font-display text-3xl font-black tracking-tight text-[#0b1d3a] sm:text-4xl md:text-5xl dark:text-white">
					{t('Export readiness at a glance.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed">
					{t('Produk, analisis pasar, costing, permintaan pembeli, dan cakupan forwarder dirangkum dari data workspace langsung Anda.')}
				</CardDescription>
				<div class="mt-6 flex flex-wrap gap-3">
					<Button href="/products">{t('Kelola produk')}</Button>
					<Button href="/export-analysis" variant="outline">{t('Jalankan analisis pasar')}</Button>
				</div>
			</div>
			{#if !hasProfile || (profile && profile.status !== 'Complete')}
				<Card class="border-destructive/30 bg-destructive/5 p-4">
					<Badge variant="outline" class="w-fit border-destructive/30 text-destructive">{t('Lengkapi Profil Bisnis!')}</Badge>
					<p class="mt-3 leading-relaxed text-muted-foreground">
						{t('Lengkapi profil bisnis dan sertifikasi sebelum memulai analisis ekspor baru.')}
					</p>
					<Button href="/business-profile" variant="ghost" class="mt-2.5 w-fit">{t('Lengkapi profil')}</Button>
				</Card>
			{/if}
		</div>
	</Card>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#if products.loading && projects.loading}
			{#each [1,2,3,4,5,6] as _}
				<div class="rounded-lg border bg-muted/30 p-5">
					<Skeleton class="mb-2 h-3 w-16" />
					<Skeleton class="h-8 w-20" />
				</div>
			{/each}
		{:else}
		<a href="/products" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-6">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Komoditas Unggulan Desa')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{products.items.length}</strong>
					<small class="text-sm text-muted-foreground">{products.items.filter((p) => p.status === 'Enriched').length} {t('ter-enrich')}</small>
				</CardContent>
			</Card>
		</a>
		<a href="/export-analysis" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-6">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Analisis pasar')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{exportAnalyses.items.length}</strong>
					<small class="text-sm text-muted-foreground">{t('rata-rata')} {avgConfidence}% {t('keyakinan')}</small>
				</CardContent>
			</Card>
		</a>
		<a href="/costing" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-6">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Nilai pipeline')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(pipelineValue)}</strong>
					<small class="text-sm text-muted-foreground">{projects.items.length} {t('proyek aktif')}</small>
				</CardContent>
			</Card>
		</a>
		<a href="/buyer-requests" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-6">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Permintaan pembeli')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{buyerRequests.items.length}</strong>
					<small class="text-sm text-muted-foreground">{buyerRequests.items.filter((r) => r.status === 'New').length} {t('baru')}</small>
				</CardContent>
			</Card>
		</a>
		<a href="/forwarders" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-6">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Forwarder')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{forwarders.items.length}</strong>
					<small class="text-sm text-muted-foreground">{forwarders.items.filter((f) => f.status === 'Verified').length} {t('terverifikasi')}</small>
				</CardContent>
			</Card>
		</a>
		<a href="/compliance" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-6">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Tinjauan risiko')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{openRisks}</strong>
					<small class="text-sm text-muted-foreground">{t('perlu tinjauan manusia')}</small>
				</CardContent>
			</Card>
		</a>
	{/if}
	</div>

	<!-- Peta Potensi Desa -->
	<VillagePotentialMap />

	<!-- Quick Actions -->
	<Card class="bg-gradient-to-br from-primary/5 to-secondary/20 shadow-sm">
		<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
			<div>
				<Badge variant="secondary">{t('Aksi Cepat')}</Badge>
				<CardTitle class="mt-2 text-xl font-bold tracking-tight">{t('Langkah selanjutnya')}</CardTitle>
			</div>
		</CardHeader>
		<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
			<Button href="/products/new" class="h-auto flex-col gap-3 py-5 text-left">
				<span class="text-lg font-bold">{t('+ Produk Baru')}</span>
				<small class="font-normal text-muted-foreground text-white">{t('Tambah produk untuk analisis')}</small>
			</Button>
			<Button href="/catalogs/create" variant="secondary" class="h-auto flex-col gap-3 py-5 text-left">
				<span class="text-lg font-bold">{t('Buat Katalog')}</span>
				<small class="font-normal text-muted-foreground">{t('Publikasikan produk Anda')}</small>
			</Button>
			<Button href="/marketing" variant="secondary" class="h-auto flex-col gap-3 py-5 text-left">
				<span class="text-lg font-bold">{t('Analisis Pasar')}</span>
				<small class="font-normal text-muted-foreground">{t('Market intelligence + pricing')}</small>
			</Button>
			<Button href="/buyer-requests" variant="secondary" class="h-auto flex-col gap-3 py-5 text-left">
				<span class="text-lg font-bold">{t('Permintaan Buyer')}</span>
				<small class="font-normal text-muted-foreground">{t('Cocokkan dengan katalog Anda')}</small>
			</Button>
		</CardContent>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card>
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Proyek ekspor aktif')}</CardTitle>
					<CardDescription>{projects.items.length} {t('proyek di Jepang, EU, Singapura')}</CardDescription>
				</div>
				<Button href="/trade-projects" variant="outline">{t('Lihat semua')}</Button>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each projects.items.slice(0, 5) as project}
					<a href={`/trade-projects/${project.id}`} class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3 no-underline transition-colors hover:border-ring/40">
						<div>
							<strong class="block">{project.name}</strong>
							<span class="block text-sm text-muted-foreground">{project.product} - {project.buyer}</span>
						</div>
						<div class="grid justify-items-end gap-3 whitespace-nowrap">
							<Badge variant={badgeVariant(project.risk)}>{project.risk}</Badge>
							<b class="text-xl font-bold tracking-tight">{project.readiness}%</b>
						</div>
					</a>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Analisis pasar terbaru')}</CardTitle>
					<CardDescription>{exportAnalyses.items.length} {t('analisis di pasar tujuan')}</CardDescription>
				</div>
				<Button href="/export-analysis" variant="outline">{t('Jalankan analisis')}</Button>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each exportAnalyses.items.slice(0, 5) as analysis}
					<a href={`/export-analysis/${analysis.id}`} class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3 no-underline transition-colors hover:border-ring/40">
						<div>
							<strong class="block">{analysis.productName}</strong>
							<span class="block text-sm text-muted-foreground">{analysis.destination} - HS {analysis.hsCode}</span>
						</div>
						<div class="grid justify-items-end gap-3 whitespace-nowrap">
							<Badge variant={badgeVariant(analysis.status)}>{analysis.status}</Badge>
							<b class="text-xl font-bold tracking-tight">{analysis.score}</b>
						</div>
					</a>
				{/each}
			</CardContent>
		</Card>
	</div>

	<div class="grid gap-4 lg:grid-cols-3">
		<Card class="lg:col-span-3">
			<CardHeader class="flex-row flex-wrap items-center justify-between gap-3">
				<div>
					<CardTitle>{t('Checklist kesiapan ekspor')}</CardTitle>
					<CardDescription>{checklistDone} dari {checklist.length} {t('langkah selesai')} — {checklistPercent}%</CardDescription>
				</div>
				<div class="flex items-center gap-3">
					<div class="h-2 w-40 overflow-hidden rounded-full bg-muted">
						<div class="h-full rounded-full bg-emerald-500" style={`width:${checklistPercent}%`}></div>
					</div>
					<Badge variant={checklistPercent === 100 ? 'default' : 'outline'}>{checklistPercent}%</Badge>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
				{#each checklist as step}
					<a href={step.href} class="rounded-xl border bg-muted/30 p-3.5 no-underline transition-colors hover:border-ring/40">
						<div class="flex items-center justify-between gap-3">
							<span class={`size-5 rounded-full grid place-items-center text-xs font-bold ${step.done ? 'bg-emerald-500 text-white' : 'border bg-background text-muted-foreground'}`}>
								{step.done ? '✓' : ''}
							</span>
							<span class="text-xs font-bold text-muted-foreground">{step.detail}</span>
						</div>
						<strong class="mt-2 block text-sm">{step.label}</strong>
					</a>
				{/each}
			</CardContent>
		</Card>
	</div>

	<div class="grid gap-4 lg:grid-cols-3">
		<Card>
			<CardHeader>
				<CardTitle>{t('Pipeline per tahap')}</CardTitle>
				<CardDescription>{t('Distribusi nilai proyek per tahap.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each pipelineByStage as [stage, data] (stage)}
					<div>
						<div class="flex items-center justify-between text-xs font-bold">
							<span>{stage}</span>
							<span class="text-muted-foreground">{data.count} {t('proyek')} · {currency.format(data.value)}</span>
						</div>
						<div class="mt-1.5 h-2.5 overflow-hidden rounded-full bg-muted">
							<div class="h-full rounded-full bg-[#0b3d91] dark:bg-sky-500" style={`width:${(data.value / maxStageValue) * 100}%`}></div>
						</div>
					</div>
				{/each}
				{#if pipelineByStage.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">{t('Belum ada proyek dagang.')}</p>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>{t('Kepatuhan per tingkat')}</CardTitle>
				<CardDescription>{t('Distribusi requirement kepatuhan.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each complianceBySeverity as [severity, count] (severity)}
					<div>
						<div class="flex items-center justify-between text-xs font-bold">
							<span class="capitalize">{severity}</span>
							<span class="text-muted-foreground">{count} {t('item')}</span>
						</div>
						<div class="mt-1.5 h-2.5 overflow-hidden rounded-full bg-muted">
							<div class={`h-full rounded-full ${severityColor(severity)}`} style={`width:${(count / complianceTotal) * 100}%`}></div>
						</div>
					</div>
				{/each}
				{#if complianceBySeverity.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">{t('Belum ada requirement kepatuhan.')}</p>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>{t('Peluang pasar')}</CardTitle>
				<Button variant="outline" size="sm" href="/marketing">{t('Pemasaran AI')}</Button>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each marketScores as analysis (analysis.id)}
					<div>
						<div class="flex items-center justify-between text-xs font-bold">
							<span>{analysis.destination}</span>
							<span class="text-muted-foreground">{analysis.productName} · {analysis.score}</span>
						</div>
						<div class="mt-1.5 h-2.5 overflow-hidden rounded-full bg-muted">
							<div class={`h-full rounded-full ${scoreColor(analysis.score)}`} style={`width:${analysis.score}%`}></div>
						</div>
					</div>
				{/each}
				{#if marketScores.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">{t('Belum ada analisis pasar. Jalankan di Export Analysis.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>

	<Card class="mt-4">
		<CardHeader class="flex-row flex-wrap items-center justify-between gap-3">
			<div>
				<CardTitle>{t('Belajar ekspor')}</CardTitle>
				<CardDescription>{t('Modul edukasi teratas untuk memperdalam kesiapan ekspor Anda.')}</CardDescription>
			</div>
			<Button variant="outline" size="sm" href="/educational">{t('Semua modul')}</Button>
		</CardHeader>
		<CardContent class="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
			{#each eduModules.items.slice(0, 3) as module (module.id)}
				<a href={`/educational/modules/${module.id}`} class="rounded-xl border bg-muted/30 p-4 no-underline transition-colors hover:border-ring/40">
					<div class="flex items-center justify-between gap-3">
						<Badge variant="secondary">{module.level}</Badge>
						<span class="text-xs font-bold text-muted-foreground">{module.completion}% {t('selesai')}</span>
					</div>
					<h3 class="mt-2 text-base font-bold">{module.title}</h3>
					<p class="mt-1 line-clamp-2 text-xs text-muted-foreground">{module.summary}</p>
					<div class="mt-3 h-2 overflow-hidden rounded-full bg-muted">
						<div class="h-full rounded-full bg-primary" style={`width:${module.completion ?? 0}%`}></div>
					</div>
				</a>
			{/each}
			{#if eduModules.items.length === 0}
				<p class="text-sm font-semibold text-muted-foreground sm:col-span-2 lg:col-span-3">{t('Belum ada modul edukasi.')}</p>
			{/if}
		</CardContent>
	</Card>
</AppShell>