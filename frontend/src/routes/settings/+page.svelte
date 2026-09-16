<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getSettings, updateSettings } from '$lib/api/settings';
	import type { WorkspaceSettings } from '$lib/api/settings';
	import { t } from '$lib/i18n.svelte';

	let settings = $state<WorkspaceSettings | null>(null);
	let companyName = $state('');
	let country = $state('Indonesia');
	let entityType = $state('');
	let nib = $state('');
	let taxId = $state('');
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	$effect(() => {
		getSettings()
			.then((res) => {
				settings = res.data;
				companyName = res.data.companyName ?? '';
				country = res.data.country ?? 'Indonesia';
				entityType = res.data.entityType ?? '';
				nib = res.data.nib ?? '';
				taxId = res.data.taxId ?? '';
			})
			.catch(() => { error = t('Gagal memuat pengaturan.'); });
	});

	async function save() {
		error = '';
		saving = true;
		try {
			await updateSettings({ companyName, country, entityType, nib, taxId });
			saved = true;
		} catch {
			error = t('Gagal menyimpan pengaturan.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Settings')} | MauEkspor</title>
</svelte:head>

<AppShell title="Settings" eyebrow={t('Organisasi dan kontrol akses')}>
	<div class="grid gap-4 lg:grid-cols-[1.2fr_minmax(360px,0.8fr)]">
		<Card class="panel-hero">
			<CardHeader><Badge>{t('Profil eksportir terverifikasi')}</Badge></CardHeader>
			<CardContent class="grid gap-4">
				<CardTitle class="font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{companyName || t('Perusahaan Anda')}</CardTitle>
				<CardDescription class="leading-relaxed">
					{t('Pengaturan organisasi akan memuat identitas legal, data pajak, NIB, lokasi produksi, dokumen verifikasi, izin tim, dan kebijakan keamanan.')}
				</CardDescription>

				{#if saved}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Pengaturan tersimpan di backend.')}</p>
				{/if}
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}

				<form class="grid gap-3" onsubmit={(event) => { event.preventDefault(); save(); }}>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="grid gap-2">
							<Label for="s-name">{t('Nama perusahaan')}</Label>
							<Input id="s-name" bind:value={companyName} />
						</div>
						<div class="grid gap-2">
							<Label for="s-country">{t('Negara')}</Label>
							<Input id="s-country" bind:value={country} />
						</div>
					</div>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="grid gap-2">
							<Label for="s-type">{t('Jenis entitas')}</Label>
							<Input id="s-type" bind:value={entityType} placeholder={t('Eksportir produsen')} />
						</div>
						<div class="grid gap-2">
							<Label for="s-nib">{t('NIB')}</Label>
							<Input id="s-nib" bind:value={nib} placeholder={t('Nomor Induk Berusaha')} />
						</div>
					</div>
					<div class="grid gap-2">
						<Label for="s-tax">{t('NPWP')}</Label>
						<Input id="s-tax" bind:value={taxId} placeholder="00.000.000.0-000.000" />
					</div>
					<Button type="submit" disabled={saving} class="w-fit">{saving ? t('Menyimpan...') : t('Simpan pengaturan')}</Button>
				</form>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>{t('Informasi organisasi')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Negara')} <strong class="mt-1 block text-sm font-bold text-foreground">{country || 'Indonesia'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Jenis entitas')} <strong class="mt-1 block text-sm font-bold text-foreground">{entityType || '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('NIB')} <strong class="mt-1 block text-sm font-bold text-foreground">{nib || t('Belum diisi')}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Keamanan')} <strong class="mt-1 block text-sm font-bold text-foreground">{settings?.security?.sessionType ?? t('Sesi cookie')}</strong>
				</div>
			</CardContent>
		</Card>
	</div>
</AppShell>
