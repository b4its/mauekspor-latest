<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getMyBuyerProfile } from '$lib/api/buyers';
	import type { BuyerProfile } from '$lib/api/buyers';
	import { t } from '$lib/i18n.svelte';

	let profile = $state<BuyerProfile | null>(null);

	$effect(() => {
		getMyBuyerProfile()
			.then((res) => (profile = res.data))
			.catch(() => (profile = null));
	});

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{t('Profil Pembeli Saya')} | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Profile" eyebrow={t('Identitas importer saya')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">{t('Profil pembeli')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{profile?.companyName ?? t('Profil Pembeli')}
				</CardTitle>
				<CardDescription class="mt-2">
					{profile?.companyDescription ?? t('Identitas importer Anda akan tampil di sini.')}
				</CardDescription>
			</div>
			<div class="grid gap-2">
				<Button variant="outline" href="/buyers/profile">{t('Edit profil')}</Button>
			</div>
		</div>
	</Card>

	{#if !profile}
		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardContent class="grid gap-2 p-6">
				<CardTitle>{t('Belum ada profil buyer.')}</CardTitle>
				<p class="text-sm text-muted-foreground">{t('Buat profil importer Anda untuk menampilkan preferensi kategori, negara sumber, dan jenis usaha.')}</p>
				<Button href="/buyers/profile" class="w-fit">{t('Buat profil')}</Button>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-4 md:grid-cols-2">
			<Card class="md:col-span-2">
				<CardHeader class="p-0"><CardTitle>{t('Profil pembeli')}</CardTitle></CardHeader>
				<CardContent class="grid gap-3 pt-4 sm:grid-cols-2 lg:grid-cols-3">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Jenis usaha')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.businessType ?? '—'}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Volume impor tahunan')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.annualImportVolume ?? '—'}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.contactInfo?.email ?? profile.contactInfo?.phone ?? '—'}</strong>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader class="p-0"><CardTitle>{t('Kategori preferensi')}</CardTitle></CardHeader>
				<CardContent class="flex flex-wrap gap-2.5 p-0 pt-4">
					{#each profile.preferredProductCategories ?? [] as category}
						<Badge variant="outline">{category}</Badge>
					{/each}
				</CardContent>
			</Card>

			<Card>
				<CardHeader class="p-0"><CardTitle>{t('Negara sumber')}</CardTitle></CardHeader>
				<CardContent class="flex flex-wrap gap-2.5 p-0 pt-4">
					{#each profile.sourceCountries ?? [] as country}
						<Badge variant="outline">{country}</Badge>
					{/each}
				</CardContent>
			</Card>
		</div>
	{/if}
</AppShell>