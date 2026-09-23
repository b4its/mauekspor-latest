<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { createBusinessProfile } from '$lib/api/business-profile';
	import { t } from '$lib/i18n.svelte';

	const certOptions = ['Halal', 'ISO 22000', 'HACCP', 'SVLK'];

	let companyName = $state('');
	let address = $state('');
	let productionCapacity = $state('');
	let yearEstablished = $state('');
	let selectedCerts = $state(['Halal']);
	let created = $state(false);
	let error = $state('');

	let valid = $derived(companyName.trim().length > 2 && address.trim().length > 3 && Number(yearEstablished) > 1900 && productionCapacity.trim().length > 2);

	function toggleCert(cert: string) {
		selectedCerts = selectedCerts.includes(cert) ? selectedCerts.filter((item) => item !== cert) : [...selectedCerts, cert];
	}

	async function create() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib dengan benar sebelum membuat profil.');
			return;
		}
		try {
			await createBusinessProfile({
				companyName,
				address,
				productionCapacity,
				yearEstablished: Number(yearEstablished),
				certifications: selectedCerts
			});
			created = true;
		} catch {
			error = t('Gagal membuat profil bisnis. Coba lagi.');
		}
	}
</script>

<svelte:head>
	<title>{t('Buat Profil Bisnis')} | MauEkspor</title>
</svelte:head>

<AppShell title="Business Profile" eyebrow={t('Buat identitas UMKM')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Perusahaan baru')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Daftarkan bisnis di balik produk Anda.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
								{t('Profil adalah jangkar identitas untuk bukti sertifikasi, katalog, dan kutipan harga.')}
				
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Profil dibuat')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{companyName}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					{t('Sertifikasi terdaftar:')} {selectedCerts.length} {t('Profil berhasil disimpan di backend.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/business-profile">{t('Lihat profil')}</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-1 sm:grid-cols-2" onsubmit={(event) => { event.preventDefault(); create(); }}>
				<div class="grid gap-2">
					<Label>{t('Nama perusahaan')}</Label>
					<Input bind:value={companyName} placeholder="PT Kopi Gayo Nusantara" />
				</div>
				<div class="grid gap-2">
					<Label>{t('Alamat')}</Label>
					<Input bind:value={address} placeholder="Takengon, Aceh, Indonesia" />
				</div>
				<div class="grid gap-2">
					<Label>{t('Kapasitas produksi per bulan')}</Label>
					<Input bind:value={productionCapacity} placeholder={t('12.000 kantong ritel / bulan')} />
				</div>
				<div class="grid gap-2">
					<Label>{t('Tahun berdiri')}</Label>
					<Input bind:value={yearEstablished} inputmode="numeric" placeholder="2018" />
				</div>

				<fieldset class="grid gap-2 rounded-lg border p-4 sm:col-span-2">
					<legend class="px-1 text-sm font-semibold text-muted-foreground">{t('Sertifikasi awal')}</legend>
					<div class="grid gap-3 sm:grid-cols-2">
						{#each certOptions as cert}
							<label class="flex items-center gap-3 rounded-lg border bg-muted/30 px-3 py-2.5">
								<Checkbox checked={selectedCerts.includes(cert)} onCheckedChange={() => toggleCert(cert)} />
								<span class="text-sm font-semibold">{cert}</span>
							</label>
						{/each}
					</div>
				</fieldset>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive sm:col-span-2">{error}</p>{/if}

				<div class="flex flex-wrap gap-3 sm:col-span-2">
					<Button variant="outline" href="/business-profile">{t('Batal')}</Button>
					<Button type="submit">{t('Buat profil bisnis')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>