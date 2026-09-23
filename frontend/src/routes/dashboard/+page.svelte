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
			})
			.catch(() => {});
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
			label: 'Lengkapi profil bisnis',
			href: '/business-profile',
			done: hasProfile && (profiles.items[0]?.status === 'Complete' || (profiles.items[0]?.readiness ?? 0) >= 80),
			detail: hasProfile ? 'Profil bisnis tersedia' : 'Tambahkan profil & sertifikasi'
		},
		{
			label: 'Tambahkan produk',
			href: '/products/new',
			done: products.items.length > 0,
			detail: products.items.length > 0 ? `${products.items.length} produk terdaftar` : 'Buat master data produk'
		},
		{
			label: 'Jalankan AI enrichment',
			href: '/products',
			done: products.items.some((p) => p.status === 'Enriched'),
			detail: products.items.some((p) => p.status === 'Enriched') ? 'HS code & SKU tersedia' : 'Enrich produk untuk HS & SKU'
		},
		{
			label: 'Buat export analysis',
			href: '/export-analysis/create',
			done: exportAnalyses.items.length > 0,
			detail: exportAnalyses.items.length > 0 ? `${exportAnalyses.items.length} analisis pasar` : 'Analisis kepatuhan & pasar tujuan'
		},
		{
			label: 'Publikasikan katalog',
			href: '/catalogs',
			done: summaryCounts ? (summaryCounts.catalogs ?? 0) > 0 : false,
			detail: summaryCounts && (summaryCounts.catalogs ?? 0) > 0 ? `${summaryCounts.catalogs} katalog dibuat` : 'Bangun katalog buyer-facing'
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
	<title>Dashboard | MauEkspor</title>
</svelte:head>

<AppShell title="Dashboard" eyebrow="Export workspace home">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-5 sm:p-6 md:p-8">
		<div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(260px,320px)] lg:items-start">
			<div>
				<Badge variant="secondary">Welcome back</Badge>
				<CardTitle class="mt-3 text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl">
					Export readiness at a glance.
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl leading-relaxed">
					Products, market analysis, costing, buyer requests, and forwarder coverage summarized from
					your live workspace data.
				</CardDescription>
				<div class="mt-6 flex flex-wrap gap-3">
					<Button href="/products">Manage products</Button>
					<Button href="/export-analysis" variant="outline">Run market analysis</Button>
				</div>
			</div>
			{#if !hasProfile || (profile && profile.status !== 'Complete')}
				<Card class="border-destructive/30 bg-destructive/5 p-4">
					<Badge variant="outline" class="w-fit border-destructive/30 text-destructive">Lengkapi Profil Bisnis!</Badge>
					<p class="mt-3 leading-relaxed text-muted-foreground">
						Lengkapi profil bisnis dan sertifikasi sebelum memulai analisis ekspor baru.
					</p>
					<Button href="/business-profile" variant="ghost" class="mt-2.5 w-fit">Complete profile</Button>
				</Card>
			{/if}
		</div>
	</Card>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<a href="/products" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Products</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{products.items.length}</strong>
					<small class="text-sm text-muted-foreground">{products.items.filter((p) => p.status === 'Enriched').length} enriched</small>
				</CardContent>
			</Card>
		</a>
		<a href="/export-analysis" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Market analyses</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{exportAnalyses.items.length}</strong>
					<small class="text-sm text-muted-foreground">avg {avgConfidence}% confidence</small>
				</CardContent>
			</Card>
		</a>
		<a href="/costing" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Pipeline value</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{currency.format(pipelineValue)}</strong>
					<small class="text-sm text-muted-foreground">{projects.items.length} active projects</small>
				</CardContent>
			</Card>
		</a>
		<a href="/buyer-requests" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Buyer requests</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{buyerRequests.items.length}</strong>
					<small class="text-sm text-muted-foreground">{buyerRequests.items.filter((r) => r.status === 'New').length} new</small>
				</CardContent>
			</Card>
		</a>
		<a href="/forwarders" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Forwarders</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{forwarders.items.length}</strong>
					<small class="text-sm text-muted-foreground">{forwarders.items.filter((f) => f.status === 'Verified').length} verified</small>
				</CardContent>
			</Card>
		</a>
		<a href="/compliance" class="rounded-lg p-1 transition-all hover:border-ring/40 hover:shadow-md">
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Risk review</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{openRisks}</strong>
					<small class="text-sm text-muted-foreground">need human review</small>
				</CardContent>
			</Card>
		</a>
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		<Card>
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Active export projects</CardTitle>
					<CardDescription>{projects.items.length} projects across Japan, EU, Singapore</CardDescription>
				</div>
				<Button href="/trade-projects" variant="outline">View all</Button>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each projects.items as project}
					<a href={`/trade-projects/${project.id}`} class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3 no-underline transition-colors hover:border-ring/40">
						<div>
							<strong class="block">{project.name}</strong>
							<span class="block text-sm text-muted-foreground">{project.product} - {project.buyer}</span>
						</div>
						<div class="grid justify-items-end gap-2 whitespace-nowrap">
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
					<CardTitle>Latest market analyses</CardTitle>
					<CardDescription>{exportAnalyses.items.length} analyses across target markets</CardDescription>
				</div>
				<Button href="/export-analysis" variant="outline">Run analysis</Button>
			</CardHeader>
			<CardContent class="grid gap-2">
				{#each exportAnalyses.items as analysis}
					<a href={`/export-analysis/${analysis.id}`} class="flex items-center justify-between gap-4 rounded-lg border bg-muted/30 p-3 no-underline transition-colors hover:border-ring/40">
						<div>
							<strong class="block">{analysis.productName}</strong>
							<span class="block text-sm text-muted-foreground">{analysis.destination} - HS {analysis.hsCode}</span>
						</div>
						<div class="grid justify-items-end gap-2 whitespace-nowrap">
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
					<CardTitle>Checklist kesiapan ekspor</CardTitle>
					<CardDescription>{checklistDone} dari {checklist.length} langkah selesai — {checklistPercent}%</CardDescription>
				</div>
				<div class="flex items-center gap-2">
					<div class="h-2 w-40 overflow-hidden rounded-full bg-muted">
						<div class="h-full rounded-full bg-emerald-500" style={`width:${checklistPercent}%`}></div>
					</div>
					<Badge variant={checklistPercent === 100 ? 'default' : 'outline'}>{checklistPercent}%</Badge>
				</div>
			</CardHeader>
			<CardContent class="grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
				{#each checklist as step}
					<a href={step.href} class="rounded-xl border bg-muted/30 p-3.5 no-underline transition-colors hover:border-ring/40">
						<div class="flex items-center justify-between gap-2">
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
				<CardTitle>Pipeline by stage</CardTitle>
				<CardDescription>Distribusi nilai proyek per tahap.</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each pipelineByStage as [stage, data] (stage)}
					<div>
						<div class="flex items-center justify-between text-xs font-bold">
							<span>{stage}</span>
							<span class="text-muted-foreground">{data.count} proyek · {currency.format(data.value)}</span>
						</div>
						<div class="mt-1.5 h-2.5 overflow-hidden rounded-full bg-muted">
							<div class="h-full rounded-full bg-[#0b3d91] dark:bg-sky-500" style={`width:${(data.value / maxStageValue) * 100}%`}></div>
						</div>
					</div>
				{/each}
				{#if pipelineByStage.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">Belum ada proyek dagang.</p>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>Compliance by severity</CardTitle>
				<CardDescription>Distribusi requirement kepatuhan.</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#each complianceBySeverity as [severity, count] (severity)}
					<div>
						<div class="flex items-center justify-between text-xs font-bold">
							<span class="capitalize">{severity}</span>
							<span class="text-muted-foreground">{count} item</span>
						</div>
						<div class="mt-1.5 h-2.5 overflow-hidden rounded-full bg-muted">
							<div class={`h-full rounded-full ${severityColor(severity)}`} style={`width:${(count / complianceTotal) * 100}%`}></div>
						</div>
					</div>
				{/each}
				{#if complianceBySeverity.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">Belum ada requirement kepatuhan.</p>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="flex-row items-center justify-between gap-3">
				<CardTitle>Market opportunity</CardTitle>
				<Button variant="outline" size="sm" href="/marketing">AI Marketing</Button>
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
					<p class="text-sm font-semibold text-muted-foreground">Belum ada analisis pasar. Jalankan di Export Analysis.</p>
				{/if}
			</CardContent>
		</Card>
	</div>

	<Card class="mt-4">
		<CardHeader class="flex-row flex-wrap items-center justify-between gap-3">
			<div>
				<CardTitle>Belajar ekspor</CardTitle>
				<CardDescription>Modul edukasi teratas untuk memperdalam kesiapan ekspor Anda.</CardDescription>
			</div>
			<Button variant="outline" size="sm" href="/educational">Semua modul</Button>
		</CardHeader>
		<CardContent class="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
			{#each eduModules.items.slice(0, 3) as module (module.id)}
				<a href={`/educational/modules/${module.id}`} class="rounded-xl border bg-muted/30 p-4 no-underline transition-colors hover:border-ring/40">
					<div class="flex items-center justify-between gap-2">
						<Badge variant="secondary">{module.level}</Badge>
						<span class="text-xs font-bold text-muted-foreground">{module.completion}% selesai</span>
					</div>
					<h3 class="mt-2 text-base font-bold">{module.title}</h3>
					<p class="mt-1 line-clamp-2 text-xs text-muted-foreground">{module.summary}</p>
					<div class="mt-3 h-2 overflow-hidden rounded-full bg-muted">
						<div class="h-full rounded-full bg-primary" style={`width:${module.completion ?? 0}%`}></div>
					</div>
				</a>
			{/each}
			{#if eduModules.items.length === 0}
				<p class="text-sm font-semibold text-muted-foreground sm:col-span-2 lg:col-span-3">Belum ada modul edukasi.</p>
			{/if}
		</CardContent>
	</Card>
</AppShell>