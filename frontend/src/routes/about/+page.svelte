<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';

	const pillars = [
		{ title: 'Readiness', text: 'Structured product data, business profile, and certifications as the foundation of every export flow.' },
		{ title: 'Analysis', text: 'HS classification, duties, restrictions, and regulation recommendations before commercial commitment.' },
		{ title: 'Execution', text: 'RFQ, quotation, costing, documents, payments, and shipment milestones in one workspace.' }
	];
</script>

<svelte:head>
	<title>About | MauEkspor</title>
</svelte:head>

<AppShell title="About" eyebrow="Trade operating system">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Indonesia to global markets</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">One workspace from product readiness to shipment delivery.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				MauEkspor unifies product data, HS classification, compliance evidence, RFQ, quotation,
				document validation, forwarder rates, and shipment milestones for Indonesian exporters.
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<div class="grid justify-items-center gap-2.5">
				<div class="grid size-16 place-items-center rounded-2xl bg-gradient-to-br from-primary to-blue-950 text-xl font-black text-white tracking-tight">ME</div>
				<strong>MauEkspor Trade OS</strong>
			</div>
		</CardContent>
	</Card>

	<div class="grid gap-4 md:grid-cols-3">
		{#each pillars as pillar}
			<Card class="grid content-start gap-3">
				<Badge variant="secondary" class="w-fit">{pillar.title}</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{pillar.title}</h3>
				<p class="leading-relaxed text-muted-foreground">{pillar.text}</p>
			</Card>
		{/each}
	</div>

	<Card>
		<h3 class="text-2xl font-bold tracking-tight">Built for the export workflow</h3>
		<div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/dashboard">Start at the dashboard</a>
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/business-profile">Complete the business profile</a>
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/educational">Learn the export process</a>
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/export-analysis">Analyze a target market</a>
		</div>
	</Card>
</AppShell>
