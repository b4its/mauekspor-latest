<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getSettings, updateSettings } from '$lib/api/settings';
	import type { WorkspaceSettings } from '$lib/api/settings';
	import { getCurrencyInfo, setDisplayCurrency, type CurrencySettings } from '$lib/api/currency';
	import { NativeSelect, NativeSelectOption } from '$lib/components/ui/native-select/index.js';
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

	let currency = $state<CurrencySettings | null>(null);
	let currencySaving = $state(false);
	let currencySaved = $state('');
	let currencyError = $state('');

	$effect(() => {
		getCurrencyInfo()
			.then((res) => { currency = res.data; })
			.catch(() => { /* diamkan — kartu opsional */ });
	});

	async function changeCurrency(code: string) {
		currencyError = '';
		currencySaved = '';
		currencySaving = true;
		try {
			const res = await setDisplayCurrency(code);
			if (currency) {
				currency = { ...currency, displayCurrency: res.data.displayCurrency, exchangeRate: res.data.exchangeRate, exchangeSource: res.data.exchangeSource };
			}
			currencySaved = t('Mata uang tampilan diperbarui.');
		} catch {
			currencyError = t('Gagal memperbarui mata uang.');
		} finally {
			currencySaving = false;
		}
	}

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
			const res = await updateSettings({ companyName, country, entityType, nib, taxId });
			if (res.data) {
				settings = res.data;
				companyName = res.data.companyName ?? companyName;
				country = res.data.country ?? country;
				entityType = res.data.entityType ?? entityType;
				nib = res.data.nib ?? nib;
				taxId = res.data.taxId ?? taxId;
			}
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
		<Card>
			<CardHeader>
				<CardTitle>{t('Mata uang tampilan')}</CardTitle>
				<CardDescription>{t('Semua harga (EXW/FOB/CIF) dihitung dan ditampilkan memakai mata uang ini.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if currencyError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{currencyError}</p>
				{/if}
				{#if currencySaved}
					<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{currencySaved}</p>
				{/if}
				{#if currency}
					<div class="grid gap-2">
						<Label for="s-currency">{t('Mata uang')}</Label>
						<NativeSelect
							id="s-currency"
							value={currency.displayCurrency}
							disabled={currencySaving}
							onchange={(e) => changeCurrency((e.currentTarget as HTMLSelectElement).value)}
						>
							{#each currency.available as cur}
								<NativeSelectOption value={cur.code}>{cur.code} — {cur.name} ({cur.symbol})</NativeSelectOption>
							{/each}
						</NativeSelect>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Kurs')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.baseCurrency} → {currency.displayCurrency} · {currency.exchangeRate} ({currency.exchangeSource})</strong>
					</div>
				{:else}
					<p class="text-sm text-muted-foreground">{t('Memuat...')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>
