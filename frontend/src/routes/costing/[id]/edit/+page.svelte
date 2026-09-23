<script lang="ts">
	import { untrack } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { updateCostingScenario } from '$lib/api/costing';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.scenario));
	let title = $state(initial.title);
	let destination = $state(initial.destination);
	let incoterm = $state(initial.incoterm);
	let margin = $state(String(initial.margin));
	let exchangeRate = $state(String(initial.exchangeRate));
	let cogs = $state(String(initial.cogs_per_unit_idr ?? 0));
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	const incoterms = ['EXW', 'FOB', 'CIF', 'DAP'];

	let valid = $derived(title.trim().length > 3 && destination.trim().length > 1 && Number(margin) >= 0 && Number(exchangeRate) > 0);

	async function save() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib dengan benar.');
			return;
		}
		saving = true;
		try {
			await updateCostingScenario(data.scenario.id, {
				title,
				destination,
				incoterm: incoterm as 'EXW' | 'FOB' | 'CIF' | 'DAP',
				margin: Number(margin),
				exchange_rate: Number(exchangeRate),
				cogs_per_unit_idr: Number(cogs) || undefined
			});
			saved = true;
		} catch {
			error = t('Gagal menyimpan skenario ke backend.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Edit {data.scenario.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.scenario.id} eyebrow={t('Edit costing scenario')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Model harga')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Perbarui')} {data.scenario.title}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Sesuaikan Incoterm, margin, dan asumsi FX yang menggerakkan biaya landed.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card>
			<CardContent class="grid gap-2 p-6">
				<Badge variant="secondary" class="w-fit">{t('Skenario disimpan')}</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{title}</h3>
				<p class="text-sm text-muted-foreground">{destination} · {incoterm} · {t('margin target')} {margin}%. {t('Perubahan tersimpan & dihitung ulang di backend.')}</p>
				<Button href={`/costing/${data.scenario.id}`} class="mt-2 w-fit">{t('Kembali ke skenario')}</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label for="cs-title">{t('Judul skenario')}</Label>
					<Input id="cs-title" bind:value={title} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="cs-dest">{t('Tujuan')}</Label>
						<Input id="cs-dest" bind:value={destination} />
					</div>
					<div class="grid gap-2">
						<Label for="cs-inc">{t('Incoterm')}</Label>
						<NativeSelect id="cs-inc" bind:value={incoterm}>
							{#each incoterms as option}<option>{option}</option>{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-4 sm:grid-cols-3">
					<div class="grid gap-2">
						<Label for="cs-cogs">{t('COGS per unit (IDR)')}</Label>
						<Input id="cs-cogs" bind:value={cogs} inputmode="decimal" />
					</div>
					<div class="grid gap-2">
						<Label for="cs-margin">{t('Margin %')}</Label>
						<Input id="cs-margin" bind:value={margin} inputmode="decimal" />
					</div>
					<div class="grid gap-2">
						<Label for="cs-fx">{t('Kurs')}</Label>
						<Input id="cs-fx" bind:value={exchangeRate} inputmode="decimal" />
					</div>
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href={`/costing/${data.scenario.id}`}>{t('Batal')}</Button>
					<Button type="submit" disabled={saving}>{saving ? t('Menyimpan...') : t('Simpan skenario')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>
