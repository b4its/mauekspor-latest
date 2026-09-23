<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { businessProfiles as seedProfiles, exportAnalyses as seedAnalyses, projects as seedProjects, products as seedProducts, buyerRequests as seedRequests, forwarders as seedForwarders } from '$lib/data/trade';
	import { listBusinessProfiles } from '$lib/api/business-profile';
	import { listExportAnalyses } from '$lib/api/export-analysis';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { listProducts } from '$lib/api/products';
	import { listBuyerRequests } from '$lib/api/buyer-requests';
	import { listForwarders } from '$lib/api/forwarders';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { currency, statusTone } from '$lib/utils/format';

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	let projects = createRemoteList(listTradeProjects, seedProjects);
	let products = createRemoteList(listProducts, seedProducts);
	let exportAnalyses = createRemoteList(listExportAnalyses, seedAnalyses);
	let buyerRequests = createRemoteList(listBuyerRequests, seedRequests);
	let forwarders = createRemoteList(listForwarders, seedForwarders);

	$effect(() => {
		profiles.load();
		projects.load();
		products.load();
		exportAnalyses.load();
		buyerRequests.load();
		forwarders.load();
	});

	let profile = $derived(profiles.items[0]);
	let openRisks = $derived(projects.items.filter((project) => project.risk !== 'Low').length);
	let pipelineValue = $derived(projects.items.reduce((sum, project) => sum + project.value, 0));
	let avgConfidence = $derived(
		exportAnalyses.items.length
			? Math.round(exportAnalyses.items.reduce((sum, item) => sum + item.confidence, 0) / exportAnalyses.items.length)
			: 0
	);

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
			{#if profile && profile.status !== 'Complete'}
				<Card class="border-destructive/30 bg-destructive/5 p-4">
					<Badge variant="outline" class="w-fit border-destructive/30 text-destructive">Profile incomplete</Badge>
					<p class="mt-3 leading-relaxed text-muted-foreground">
						Complete your business profile and certifications before starting a new export analysis.
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
</AppShell>