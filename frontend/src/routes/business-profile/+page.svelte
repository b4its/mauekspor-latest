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
	import { t } from '$lib/i18n.svelte';

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	$effect(() => {
		profiles.load();
	});
	let profile = $derived(profiles.items[0] ?? seedProfiles[0]);
	const certOptions = ['Halal', 'ISO 22000', 'HACCP', 'SVLK', 'Organic', 'Origin declaration', 'Nutrition facts'];

	function trCert(c: string) {
		return t(c === 'Organic' ? 'Organik' : c === 'Origin declaration' ? 'Deklarasi asal' : c === 'Nutrition facts' ? 'Informasi nilai gizi' : c);
	}

	function trStatus(s: string) {
		return t(s === 'Verified' ? 'Terverifikasi' : s === 'Archived' ? 'Diarsipkan' : 'Menunggu');
	}

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
	<title>{t('Profil Bisnis')} | MauEkspor</title>
</svelte:head>

<AppShell title="Business Profile" eyebrow={t('Identitas UMKM dan sertifikasi')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(profile.status))}>{trStatus(profile.status)}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{profile.companyName}
				</CardTitle>
				<CardDescription class="mt-2">{profile.address}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Kesiapan ekspor')}</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{profile.readiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Detail perusahaan')}</CardTitle>
					<CardDescription class="mt-1.5">{t('Identitas inti yang digunakan di seluruh alur kerja produk, kepatuhan, dan kutipan harga.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href="/business-profile/edit">{t('Edit profil')}</Button>
					<Button href="/business-profile/certifications">{t('Kelola sertifikasi')}</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kapasitas produksi')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.productionCapacity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tahun berdiri')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.yearEstablished}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Sertifikasi')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.certifications.length}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.owner}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>{t('Kelola sertifikasi')}</CardTitle>
				<CardDescription>{t('Centang kotak untuk menambah atau menghapus klaim sertifikasi pada profil bisnis.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-2.5 sm:grid-cols-2">
				{#each certOptions as cert}
					<label class="flex cursor-pointer items-center gap-2.5 rounded-lg border bg-muted/30 p-3">
						<Checkbox
							checked={profile.certifications.includes(cert)}
							onCheckedChange={() => toggleCert(cert)}
						/>
						<span class="text-sm font-bold">{trCert(cert)}</span>
					</label>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">{t('Wawasan kesiapan')}</Badge>
				<CardTitle>{t('Tingkatkan sisa')} {100 - profile.readiness}%</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					{t('Sertifikasi berbasis bukti, data produk yang konsisten, dan berkas kepatuhan yang lengkap adalah jalur tercepat menuju skor kesiapan profil yang lebih tinggi.')}
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>