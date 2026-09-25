<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { createBuyerProfile, updateBuyerProfile, getMyBuyerProfile } from '$lib/api/buyers';
	import type { BuyerProfile } from '$lib/api/buyers';

	let companyName = $state('');
	let companyDescription = $state('');
	let contactEmail = $state('');
	let contactPhone = $state('');
	let categories = $state('');
	let sourceCountries = $state('');
	let businessType = $state('');
	let annualImportVolume = $state('');
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');
	let existingId = $state('');

	$effect(() => {
		getMyBuyerProfile()
			.then((res) => {
				const p = res.data;
				existingId = p.id ?? '';
				companyName = p.companyName ?? companyName;
				companyDescription = p.companyDescription ?? '';
				contactEmail = p.contactInfo?.email ?? '';
				contactPhone = p.contactInfo?.phone ?? '';
				categories = (p.preferredProductCategories ?? []).join(', ');
				sourceCountries = (p.sourceCountries ?? []).join(', ');
				businessType = p.businessType ?? '';
				annualImportVolume = p.annualImportVolume ?? '';
			})
			.catch(() => {});
	});

	let valid = $derived(companyName.trim().length > 2 && contactEmail.trim().length > 4);

	async function save() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib: company name dan contact email.');
			return;
		}
		saving = true;
		const payload: Partial<BuyerProfile> = {
			companyName,
			companyDescription,
			contactInfo: { email: contactEmail, phone: contactPhone },
			preferredProductCategories: categories.split(',').map((s) => s.trim()).filter(Boolean),
			sourceCountries: sourceCountries.split(',').map((s) => s.trim()).filter(Boolean),
			businessType,
			annualImportVolume
		};
		try {
			if (existingId) await updateBuyerProfile(existingId, payload);
			else await createBuyerProfile(payload);
			saved = true;
		} catch {
			error = t('Gagal menyimpan profil buyer.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Edit Profil Pembeli')} | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Profile" eyebrow={t('Edit importer identity')}>
	<Card class="grid gap-6 border panel-hero p-6 md:p-8">
		<div>
			<Badge variant="secondary">{t('Profil')}</Badge>
			<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Perbarui cara eksportir melihat perusahaan Anda.')}</h2>
			<p class="mt-2 max-w-2xl leading-relaxed text-muted-foreground">
				{t('Kategori produk yang diminati, negara sumber, dan volume impor tahunan.')}
			</p>
		</div>

		{#if saved}
			<Card>
				<CardContent class="grid gap-3 p-5">
					<Badge>{t('Profil disimpan')}</Badge>
					<h3 class="text-2xl font-bold tracking-tight">{companyName}</h3>
					<p class="text-sm text-muted-foreground">{t('Profil tersimpan di backend.')}</p>
					<Button href="/buyers/my-profile" class="w-fit">{t('Kembali ke profil')}</Button>
				</CardContent>
			</Card>
		{:else}
			<form class="grid gap-4" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label for="b-name">{t('Nama perusahaan')}</Label>
					<Input id="b-name" bind:value={companyName} />
				</div>
				<div class="grid gap-2">
					<Label for="b-desc">{t('Deskripsi perusahaan')}</Label>
					<Textarea id="b-desc" bind:value={companyDescription} rows={2} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="b-email">{t('Email kontak')}</Label>
						<Input id="b-email" bind:value={contactEmail} />
					</div>
					<div class="grid gap-2">
						<Label for="b-phone">{t('Telepon kontak')}</Label>
						<Input id="b-phone" bind:value={contactPhone} />
					</div>
				</div>
				<div class="grid gap-2">
					<Label for="b-cat">{t('Preferred product categories (pisahkan dengan koma)')}</Label>
					<Input id="b-cat" bind:value={categories} placeholder="Makanan Olahan, Minuman" />
				</div>
				<div class="grid gap-2">
					<Label for="b-country">{t('Source countries (pisahkan dengan koma)')}</Label>
					<Input id="b-country" bind:value={sourceCountries} placeholder="Indonesia, Vietnam" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="b-type">{t('Jenis usaha')}</Label>
						<Input id="b-type" bind:value={businessType} placeholder="Importer / Distributor" />
					</div>
					<div class="grid gap-2">
						<Label for="b-volume">{t('Volume impor tahunan')}</Label>
						<Input id="b-volume" bind:value={annualImportVolume} placeholder="US$1-5M" />
					</div>
				</div>

				{#if error}<p class="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-semibold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-2">
					<Button variant="outline" href="/buyers/my-profile">{t('Batal')}</Button>
					<Button type="submit" disabled={saving}>{saving ? t('Menyimpan...') : t('Simpan profil')}</Button>
				</div>
			</form>
		{/if}
	</Card>
</AppShell>
