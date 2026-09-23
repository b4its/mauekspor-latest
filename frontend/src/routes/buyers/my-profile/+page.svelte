<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { buyers } from '$lib/data/trade';
	import { currency, statusTone } from '$lib/utils/format';

	let profile = $derived(buyers[0]);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>My Buyer Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Profile" eyebrow="My importer identity">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(profile.status))}>{profile.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{profile.name}
				</CardTitle>
				<CardDescription class="mt-2">{profile.segment} - {profile.country}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Fit score</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{profile.fitScore}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="p-0"><CardTitle>Buyer profile</CardTitle></CardHeader>
			<CardContent class="grid gap-3 pt-4 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Country <strong class="mt-1 block text-sm font-bold text-foreground">{profile.country}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Segment <strong class="mt-1 block text-sm font-bold text-foreground">{profile.segment}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Annual pipeline <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(profile.estimatedAnnualValue)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Payment profile <strong class="mt-1 block text-sm font-bold text-foreground">{profile.paymentProfile}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Last contact <strong class="mt-1 block text-sm font-bold text-foreground">{profile.lastContact}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Next step <strong class="mt-1 block text-sm font-bold text-foreground">{profile.nextStep}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>Interested products</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5 p-0 pt-4">
				{#each profile.interestedProducts as product}
					<Badge variant="outline">{product}</Badge>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">Buyer signal</Badge>
				<CardTitle>What to do next</CardTitle>
			</CardHeader>
			<CardContent class="p-0 pt-4">
				<p class="leading-relaxed text-muted-foreground">
					{profile.signals?.[0]?.label ?? 'Prioritize the next active signal to keep this level moving through the funnel.'}
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>