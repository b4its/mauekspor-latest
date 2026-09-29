<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Alert } from '$lib/components/ui/alert/index.js';
	import { createProduct } from '$lib/api/products';
	import { t } from '$lib/i18n.svelte';

	let name = $state('');
	let category = $state('Food & Beverage');
	let origin = $state('');
	let packaging = $state('');
	let netWeight = $state('');
	let grossWeight = $state('');
	let moq = $state('');
	let leadTime = $state('');
	let certificates = $state('');
	let created = $state(false);
	let createdId = $state<string | null>(null);
	let error = $state('');
	let creating = $state(false);

	const categories = ['Food & Beverage', 'Furniture & Craft', 'Apparel & Textile', 'Electronics', 'Agro & Spice'];

	let valid = $derived(name.trim().length > 2 && origin.trim().length > 1 && category);

	async function create() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib: nama produk, kategori, dan asal.');
			return;
		}
		creating = true;
		try {
			const res = await createProduct({
				name: name.trim(),
				category,
				origin: origin.trim(),
				packaging: packaging.trim() || undefined,
				netWeight: netWeight.trim() || undefined,
				grossWeight: grossWeight.trim() || undefined,
				moq: moq.trim() || undefined,
				leadTime: leadTime.trim() || undefined,
				certificates: certificates.trim()
					? certificates.split(',').map((c) => c.trim()).filter(Boolean)
					: undefined
			});
			createdId = res.data.id;
			created = true;
		} catch (err) {
			error = err instanceof Error ? err.message : t('Gagal membuat produk.');
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Produk Baru')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Products')} eyebrow={t('Add export product')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Pembuatan produk')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Tangkap data produk yang dibutuhkan setiap langkah ekspor.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Spesifikasi terstruktur di sini menggerakkan klasifikasi HS, pemeriksaan kepatuhan, katalog, dan costing.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge>{t('Produk dibuat')}</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{name}</h3>
				<p class="text-muted-foreground">
					{t('Produk berhasil disimpan ke backend dan siap digunakan di HS classification, compliance, dan katalog.')}
					{#if createdId}<code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">{createdId}</code>{/if}
				</p>
				<Button href="/products">{t('Kembali ke produk')}</Button>
			</CardContent>
		</Card>
	{:else}
		<form
			class="grid gap-4 rounded-xl bg-card p-4 ring-1 ring-foreground/10"
			onsubmit={(event) => {
				event.preventDefault();
				create();
			}}
		>
			<div class="grid gap-2">
				<Label for="p-name">{t('Nama')}</Label>
				<Input id="p-name" bind:value={name} placeholder="Gayo Arabica Coffee Beans" />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label for="p-category">{t('Kategori')}</Label>
					<NativeSelect id="p-category" bind:value={category}>
						{#each categories as option}
							<option>{option}</option>
						{/each}
					</NativeSelect>
				</div>
				<div class="grid gap-2">
					<Label for="p-origin">{t('Asal')}</Label>
					<Input id="p-origin" bind:value={origin} placeholder="Aceh, Indonesia" />
				</div>
			</div>
			<div class="grid gap-2">
				<Label for="p-packaging">{t('Kemasan')}</Label>
				<Input id="p-packaging" bind:value={packaging} placeholder={t('Kantong valve 250g, 24 kantong per karton')} />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label for="p-net">{t('Berat bersih')}</Label><Input id="p-net" bind:value={netWeight} placeholder="250g" /></div>
				<div class="grid gap-2"><Label for="p-gross">{t('Berat kotor')}</Label><Input id="p-gross" bind:value={grossWeight} placeholder="280g" /></div>
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label for="p-moq">{t('MOQ')}</Label><Input id="p-moq" bind:value={moq} placeholder={t('2.000 kantong')} /></div>
				<div class="grid gap-2"><Label for="p-lead">{t('Waktu tunggu')}</Label><Input id="p-lead" bind:value={leadTime} placeholder={t('21 hari')} /></div>
			</div>
			<div class="grid gap-2">
				<Label for="p-certs">{t('Sertifikat (dipisahkan koma)')}</Label>
				<Input id="p-certs" bind:value={certificates} placeholder={t('Halal, Organik sedang berjalan')} />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href="/products">{t('Batal')}</Button>
				<Button type="submit" disabled={creating}>{creating ? t('Membuat...') : t('Buat produk')}</Button>
			</div>
		</form>
	{/if}
</AppShell>