<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { businessProfiles as seedProfiles } from '$lib/data/trade';
	import { listBusinessProfiles } from '$lib/api/business-profile';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	$effect(() => {
		profiles.load();
	});
	let profile = $derived(profiles.items[0] ?? seedProfiles[0]);
	const certOptions = ['Halal', 'ISO 22000', 'HACCP', 'SVLK', 'Organic', 'Origin declaration', 'Nutrition facts'];

	function toggleCert(cert: string) {
		profile.certifications = profile.certifications.includes(cert)
			? profile.certifications.filter((item) => item !== cert)
			: [...profile.certifications, cert];
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Business Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Business Profile" eyebrow="UMKM identity and certifications">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(profile.status))}>{profile.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{profile.companyName}
				</CardTitle>
				<CardDescription class="mt-2">{profile.address}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Export readiness</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{profile.readiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Company details</CardTitle>
					<CardDescription class="mt-1.5">Core identity used across product, compliance, and quotation workflows.</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href="/business-profile/edit">Edit profile</Button>
					<Button href="/business-profile/certifications">Manage certifications</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Production capacity <strong class="mt-1 block text-sm font-bold text-foreground">{profile.productionCapacity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Year established <strong class="mt-1 block text-sm font-bold text-foreground">{profile.yearEstablished}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Certifications <strong class="mt-1 block text-sm font-bold text-foreground">{profile.certifications.length}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Contact <strong class="mt-1 block text-sm font-bold text-foreground">{profile.owner}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>Manage certifications</CardTitle>
				<CardDescription>Toggle checkboxes to add or remove certification claims on the business profile.</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-2.5 sm:grid-cols-2">
				{#each certOptions as cert}
					<label class="flex cursor-pointer items-center gap-2.5 rounded-lg border bg-muted/30 p-3">
						<Checkbox
							checked={profile.certifications.includes(cert)}
							onCheckedChange={() => toggleCert(cert)}
						/>
						<span class="text-sm font-bold">{cert}</span>
					</label>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">Readiness insight</Badge>
				<CardTitle>Improve the next {100 - profile.readiness}%</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					Evidence-backed certifications, consistent product data, and a completed compliance file are
					the fastest path to a higher profile readiness score.
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>