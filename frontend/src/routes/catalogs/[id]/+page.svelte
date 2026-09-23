<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { generateCatalogDescription, publishCatalog } from '$lib/api/catalogs';

	let { data } = $props();
	let published = $state(false);
	let generated = $state(false);
	let error = $state('');

	$effect(() => {
		published = data.catalog.status === 'Published';
	});

	async function handleGenerate() {
		error = '';
		try {
			await generateCatalogDescription(data.catalog.id);
			generated = true;
		} catch {
			error = 'Gagal generate AI copy.';
		}
	}

	async function handlePublish() {
		error = '';
		try {
			await publishCatalog(data.catalog.id);
			published = true;
		} catch {
			error = 'Gagal mempublikasikan katalog.';
		}
	}

	let displayStatus = $derived(published ? 'Published' : generated ? 'Needs Review' : data.catalog.status);
	let displayReadiness = $derived(published ? Math.max(data.catalog.readiness, 95) : generated ? Math.min(data.catalog.readiness + 8, 100) : data.catalog.readiness);
	let displayDescription = $derived(
		generated
			? `${data.catalog.description} AI-enhanced buyer copy adds clearer commercial positioning, MOQ context, and export readiness cues for international sourcing teams.`
			: data.catalog.description
	);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.catalog.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.catalog.id} eyebrow="Catalog detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.catalog.title}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.catalog.projectId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Catalog readiness</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayReadiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Buyer-Facing Copy</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl leading-relaxed">{displayDescription}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/catalogs/${data.catalog.id}/edit`}>Edit catalog</Button>
					<Button variant="outline" onclick={handleGenerate}>Generate AI copy</Button>
					<Button disabled={published} onclick={handlePublish}>{published ? 'Published' : 'Publish catalog'}</Button>
				</div>
			</CardHeader>
			{#if error}
				<p class="rounded-lg bg-destructive/10 px-4 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Product <strong class="mt-1 block text-sm font-bold text-foreground">{data.product?.name ?? data.catalog.productId}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Target market <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.targetMarket}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					MOQ <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.moq}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Lead time <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.leadTime}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Price range <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.priceRange}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Images <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.images}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Marketing Highlights</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5">
				{#each data.catalog.highlights as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Variants and Incoterms</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5">
				{#each data.catalog.variants as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
				{#each data.catalog.incoterms as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">Specification sheet</Badge>
				<CardTitle>Technical Specifications</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3">
				<div class="grid gap-3 sm:grid-cols-2">
					{#each data.catalog.specifications as spec}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<span class="block text-xs font-bold uppercase tracking-wide text-muted-foreground">{spec.label}</span>
							<strong class="mt-1 block text-sm font-bold">{spec.value}</strong>
						</div>
					{/each}
				</div>
				{#if generated}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">AI copy dibuat di backend.</p>
				{/if}
				{#if published}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Katalog dipublikasikan di backend.</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>