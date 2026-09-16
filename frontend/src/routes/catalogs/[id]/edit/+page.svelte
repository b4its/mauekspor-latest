<script lang="ts">
	import { untrack } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Alert } from '$lib/components/ui/alert/index.js';
	import { updateCatalog } from '$lib/api/catalogs';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.catalog));
	let title = $state(initial.title);
	let targetMarket = $state(initial.targetMarket);
	let moq = $state(initial.moq);
	let leadTime = $state(initial.leadTime);
	let priceRange = $state(initial.priceRange);
	let description = $state(initial.description);
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	let valid = $derived(title.trim().length > 3 && targetMarket.trim().length > 1 && moq.trim().length > 1);

	async function save() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib sebelum menyimpan.');
			return;
		}
		saving = true;
		try {
			await updateCatalog(data.catalog.id, {
				title,
				targetMarket,
				moq,
				leadTime,
				priceRange,
				description
			});
			saved = true;
		} catch {
			error = t('Gagal menyimpan katalog ke backend.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Edit {data.catalog.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.catalog.id} eyebrow={t('Edit catalog')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Data master katalog')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Perbarui')} {data.catalog.title}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Perubahan copy, harga, dan pasar target memperbarui katalog yang menghadap pembeli.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge variant="secondary">{t('Katalog disimpan')}</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{title}</h3>
				<p class="text-muted-foreground">
					{t('Perubahan katalog tersimpan di backend.')}
				</p>
				<Button href={`/catalogs/${data.catalog.id}`}>{t('Kembali ke katalog')}</Button>
			</CardContent>
		</Card>
	{:else}
		<form
			class="grid gap-4 rounded-xl bg-card p-4 ring-1 ring-foreground/10"
			onsubmit={(event) => {
				event.preventDefault();
				save();
			}}
		>
			<div class="grid gap-2">
				<Label for="c-title">{t('Judul katalog')}</Label>
				<Input id="c-title" bind:value={title} />
			</div>
			<div class="grid gap-2">
				<Label for="c-market">{t('Pasar target')}</Label>
				<Input id="c-market" bind:value={targetMarket} />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label for="c-moq">{t('MOQ')}</Label><Input id="c-moq" bind:value={moq} /></div>
				<div class="grid gap-2"><Label for="c-lead">{t('Waktu tunggu')}</Label><Input id="c-lead" bind:value={leadTime} /></div>
			</div>
			<div class="grid gap-2">
				<Label for="c-price">{t('Rentang harga')}</Label>
				<Input id="c-price" bind:value={priceRange} />
			</div>
			<div class="grid gap-2">
				<Label for="c-desc">{t('Deskripsi untuk pembeli')}</Label>
				<Textarea id="c-desc" bind:value={description} rows={3} />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href={`/catalogs/${data.catalog.id}`}>{t('Batal')}</Button>
				<Button type="submit" disabled={saving}>{saving ? t('Menyimpan...') : t('Simpan katalog')}</Button>
			</div>
		</form>
	{/if}
</AppShell>