<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { businessProfiles as seedProfiles } from '$lib/data/trade';
	import { listBusinessProfiles, updateBusinessProfile } from '$lib/api/business-profile';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { t } from '$lib/i18n.svelte';

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	$effect(() => {
		profiles.load();
	});

	let loaded = $state(false);
	let companyName = $state(seedProfiles[0].companyName);
	let address = $state(seedProfiles[0].address);
	let productionCapacity = $state(seedProfiles[0].productionCapacity);
	let yearEstablished = $state(String(seedProfiles[0].yearEstablished));
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	// Isi form dari profil backend saat sudah dimuat (fallback ke seed bila API tak tersedia)
	$effect(() => {
		const p = profiles.items[0];
		if (!p) return;
		if (!loaded) {
			companyName = p.companyName;
			address = p.address;
			productionCapacity = p.productionCapacity;
			yearEstablished = String(p.yearEstablished);
			loaded = true;
		}
	});

	let profile = $derived(profiles.items[0] ?? seedProfiles[0]);
	let valid = $derived(companyName.trim().length > 2 && address.trim().length > 3 && Number(yearEstablished) > 1900);

	async function save() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib dengan benar sebelum menyimpan.');
			return;
		}
		saving = true;
		try {
			await updateBusinessProfile(profile.id, {
				companyName,
				address,
				productionCapacity,
				yearEstablished: Number(yearEstablished)
			});
			saved = true;
		} catch {
			error = t('Gagal menyimpan profil.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Edit Profil Bisnis')} | MauEkspor</title>
</svelte:head>

<AppShell title="Business Profile" eyebrow={t('Edit identitas UMKM')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Identitas')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Perbarui detail perusahaan yang digunakan di seluruh workspace.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Perubahan di sini tercermin di katalog produk, berkas kepatuhan, dan kutipan mendatang. Perubahan disimpan ke backend.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Tersimpan')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{companyName}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					{t('Profil tersimpan di backend.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/business-profile">{t('Kembali ke profil')}</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-1 sm:grid-cols-2" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label>{t('Nama perusahaan')}</Label>
					<Input bind:value={companyName} />
				</div>
				<div class="grid gap-2">
					<Label>{t('Alamat')}</Label>
					<Input bind:value={address} />
				</div>
				<div class="grid gap-2">
					<Label>{t('Kapasitas produksi per bulan')}</Label>
					<Input bind:value={productionCapacity} />
				</div>
				<div class="grid gap-2">
					<Label>{t('Tahun berdiri')}</Label>
					<Input bind:value={yearEstablished} inputmode="numeric" />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive sm:col-span-2">{error}</p>{/if}

				<div class="flex flex-wrap items-center gap-3 sm:col-span-2">
					<Button variant="outline" href="/business-profile">{t('Batal')}</Button>
					<Button type="submit" disabled={saving}>{saving ? t('Menyimpan...') : t('Simpan perubahan')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>