<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { businessProfiles as seedProfiles } from '$lib/data/trade';
	import { listBusinessProfiles, updateCertifications } from '$lib/api/business-profile';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { t } from '$lib/i18n.svelte';

	const certOptions = ['Halal', 'ISO 22000', 'HACCP', 'SVLK', 'Organic', 'Origin declaration', 'Nutrition facts'];

	let selected = $state(['Halal', 'Origin declaration']);
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	$effect(() => {
		profiles.load();
	});

	function toggleCert(cert: string) {
		selected = selected.includes(cert) ? selected.filter((item) => item !== cert) : [...selected, cert];
	}

	async function handleSave() {
		error = '';
		saving = true;
		try {
			const profile = profiles.items[0] ?? seedProfiles[0];
			if (profile) await updateCertifications(profile.id, selected);
			saved = true;
		} catch {
			error = t('Gagal menyimpan sertifikasi.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Kelola Sertifikasi')} | MauEkspor</title>
</svelte:head>

<AppShell title="Certifications" eyebrow={t('Manage business certification claims')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Berbasis bukti')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Aktifkan sertifikasi yang dapat dibuktikan bisnis Anda.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Klaim sertifikasi mengalir ke katalog produk dan analisis pasar dan disimpan di backend.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if saved}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Tersimpan')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{selected.length} {t('sertifikasi aktif')}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">{selected.join(' · ') || t('Tidak ada sertifikasi dipilih.')}</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/business-profile">{t('Kembali ke profil')}</Button>
			</CardContent>
		</Card>
	{:else}
		<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			{#each certOptions as cert}
				<label class="flex items-center gap-3 rounded-lg border bg-muted/30 px-4 py-3.5">
					<Checkbox checked={selected.includes(cert)} onCheckedChange={() => toggleCert(cert)} />
					<span class="text-sm font-semibold">{cert}</span>
				</label>
			{/each}
		</div>
		<div class="flex flex-wrap gap-3">
			<Button variant="outline" href="/business-profile">{t('Batal')}</Button>
			<Button onclick={handleSave} disabled={saving}>{saved ? t('Tersimpan') : saving ? t('Menyimpan...') : t('Simpan sertifikasi')}</Button>
		</div>
	{/if}
</AppShell>