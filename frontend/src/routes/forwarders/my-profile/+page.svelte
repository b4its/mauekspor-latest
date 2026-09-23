<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { forwarders as seedForwarders } from '$lib/data/trade';
	import { getMyForwarderProfile } from '$lib/api/forwarders';
	import type { ForwarderProfile } from '$lib/api/forwarders';

	let profile = $state<ForwarderProfile | null>(null);
	let fallback = $derived(seedForwarders[0]);

	$effect(() => {
		getMyForwarderProfile()
			.then((res) => (profile = res.data))
			.catch(() => (profile = null));
	});
</script>

<svelte:head>
	<title>My Forwarder Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarder Profile" eyebrow="My freight partner identity">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">Forwarder profile</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{profile?.companyName ?? fallback.name}
				</CardTitle>
				<CardDescription class="mt-2">{profile?.companyName ?? fallback.coverage}</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<Button variant="outline" href="/forwarders/profile">Edit profile</Button>
			</div>
		</div>
	</Card>

	{#if !profile}
		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardContent class="grid gap-2 p-6">
				<CardTitle>Belum ada profil forwarder.</CardTitle>
				<p class="text-sm text-muted-foreground">Buat profil untuk menampilkan rute spesialisasi dan tipe layanan Anda.</p>
				<Button href="/forwarders/profile" class="w-fit">Buat profil</Button>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-4 md:grid-cols-2">
			<Card class="md:col-span-2">
				<CardHeader><CardTitle>Forwarder profile</CardTitle></CardHeader>
				<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						Rating <strong class="mt-1 block text-sm font-bold text-foreground">{profile.averageRating ?? 0} ⭐ ({profile.totalReviews ?? 0} review)</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						Contact email <strong class="mt-1 block text-sm font-bold text-foreground">{profile.contactInfo?.email ?? '—'}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						Contact phone <strong class="mt-1 block text-sm font-bold text-foreground">{profile.contactInfo?.phone ?? '—'}</strong>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader><CardTitle>Specialization routes</CardTitle></CardHeader>
				<CardContent class="grid gap-2.5">
					{#each profile.specializationRoutes ?? [] as route}
						<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">Route</Badge><strong class="text-sm">{route}</strong></div>
					{/each}
				</CardContent>
			</Card>

			<Card>
				<CardHeader><CardTitle>Service types</CardTitle></CardHeader>
				<CardContent class="flex flex-wrap gap-2">
					{#each profile.serviceTypes ?? [] as service}
						<Badge variant="secondary">{service}</Badge>
					{/each}
				</CardContent>
			</Card>
		</div>
	{/if}
</AppShell>