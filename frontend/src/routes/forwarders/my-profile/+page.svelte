<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { forwarders as seedForwarders } from '$lib/data/trade';
	import { getMyForwarderProfile, getForwarderStatistics } from '$lib/api/forwarders';
	import type { ForwarderProfile, ForwarderStatistics } from '$lib/api/forwarders';
	import { t } from '$lib/i18n.svelte';

	let profile = $state<ForwarderProfile | null>(null);
	let stats = $state<ForwarderStatistics | null>(null);
	let fallback = $derived(seedForwarders[0]);

	$effect(() => {
		getMyForwarderProfile()
			.then((res) => (profile = res.data))
			.catch(() => (profile = null));
		// Statistik dari forwarder seed (untuk demo role Forwarder)
		getForwarderStatistics(seedForwarders[0].id)
			.then((res) => (stats = res.data))
			.catch((e) => console.error("API error:", e));
	});
</script>

<svelte:head>
	<title>{t('Profil Forwarder Saya')} | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarder Profile" eyebrow={t('Identitas mitra freight saya')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">{t('Profil forwarder')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{profile?.companyName ?? fallback.name}
				</CardTitle>
				<CardDescription class="mt-2">{profile?.companyName ?? fallback.coverage}</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<Button variant="outline" href="/forwarders/profile">{t('Edit profil')}</Button>
			</div>
		</div>
	</Card>

	{#if !profile}
		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardContent class="grid gap-2 p-6">
				<CardTitle>{t('Belum ada profil forwarder.')}</CardTitle>
				<p class="text-sm text-muted-foreground">{t('Buat profil untuk menampilkan rute spesialisasi dan tipe layanan Anda.')}</p>
				<Button href="/forwarders/profile" class="w-fit">{t('Buat profil')}</Button>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-4 md:grid-cols-2">
			<Card class="md:col-span-2">
				<CardHeader><CardTitle>{t('Profil forwarder')}</CardTitle></CardHeader>
				<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Rating')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.averageRating ?? 0} ⭐ ({profile.totalReviews ?? 0} {t('ulasan')})</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Email kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.contactInfo?.email ?? '—'}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Telepon kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.contactInfo?.phone ?? '—'}</strong>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader><CardTitle>{t('Rute spesialisasi')}</CardTitle></CardHeader>
				<CardContent class="grid gap-2.5">
					{#each profile.specializationRoutes ?? [] as route}
						<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">{t('Route')}</Badge><strong class="text-sm">{route}</strong></div>
					{/each}
				</CardContent>
			</Card>

			<Card>
				<CardHeader><CardTitle>{t('Tipe layanan')}</CardTitle></CardHeader>
				<CardContent class="flex flex-wrap gap-2">
					{#each profile.serviceTypes ?? [] as service}
						<Badge variant="secondary">{service}</Badge>
					{/each}
				</CardContent>
			</Card>

			{#if stats}
				<Card class="md:col-span-2">
					<CardHeader>
						<CardTitle>{t('Statistik rating')}</CardTitle>
						<CardDescription>{t('Kinerja Anda menurut buyer/UMKM.')}</CardDescription>
					</CardHeader>
					<CardContent class="grid gap-4 sm:grid-cols-3">
						<div class="rounded-lg border bg-muted/40 p-4 text-center">
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Rating rata-rata')}</span>
							<strong class="mt-1 block text-3xl font-bold">{stats.averageRating} ⭐</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-4 text-center">
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Total review')}</span>
							<strong class="mt-1 block text-3xl font-bold">{stats.totalReviews}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-4 text-center">
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Kemitraan unik')}</span>
							<strong class="mt-1 block text-3xl font-bold">{stats.uniquePartnerships}</strong>
						</div>
						{#if stats.ratingDistribution}
							<div class="grid gap-1.5 sm:col-span-3">
								{#each Object.entries(stats.ratingDistribution) as [star, percent]}
									<div class="flex items-center gap-2 text-xs">
										<span class="w-4 font-bold">{star}★</span>
										<div class="h-2 flex-1 overflow-hidden rounded-full bg-muted">
											<div class="h-full bg-primary" style={`width:${percent}%`}></div>
										</div>
										<span class="w-8 text-right text-muted-foreground">{percent}%</span>
									</div>
								{/each}
							</div>
						{/if}
					</CardContent>
				</Card>
			{/if}
		</div>
	{/if}
</AppShell>