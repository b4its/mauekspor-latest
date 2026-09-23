<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Alert } from '$lib/components/ui/alert/index.js';
	import { products as seedProducts, projects as seedProjects } from '$lib/data/trade';
	import { createCatalog, addCatalogImage } from '$lib/api/catalogs';
	import { listProducts, generateCatalogDescription } from '$lib/api/products';
	import { uploadFileBinary, fileDownloadUrl } from '$lib/api/files';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import type { Product } from '$lib/data/trade';

	let products = createRemoteList<Product>(listProducts, seedProducts);
	products.load();
	let productId = $state('');
	let projectId = $state('');
	let title = $state('');
	let targetMarket = $state('');
	let moq = $state('');
	let leadTime = $state('');
	let priceRange = $state('');
	let description = $state('');
	let tags = $state('');
	let created = $state(false);
	let creating = $state(false);
	let generating = $state(false);
	let error = $state('');
	let createdId = $state('');
	let imageFile = $state<File | null>(null);

	let valid = $derived(title.trim().length > 3 && productId && targetMarket.trim().length > 1 && moq.trim().length > 1);

	async function create() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib: judul, produk, target market, dan MOQ.');
			return;
		}
		creating = true;
		try {
			const res = await createCatalog({
				productId,
				projectId: projectId || '',
				title,
				targetMarket,
				moq,
				leadTime: leadTime || 'TBD',
				priceRange,
				description,
				tags: tags.split(',').map((t) => t.trim()).filter(Boolean)
			});
			createdId = res.data.id;
			// Upload gambar opsional dan tautkan ke katalog yang baru dibuat
			if (imageFile) {
				try {
					const fileRes = await uploadFileBinary(imageFile, 'Catalog Image', projectId || '', []);
					await addCatalogImage(createdId, { image_url: fileDownloadUrl(fileRes.data.id), alt_text: imageFile.name, is_primary: true });
				} catch {
					// gambar gagal diunggah — katalog tetap jadi
				}
			}
			created = true;
		} catch {
			error = t('Gagal membuat katalog. Coba lagi.');
		} finally {
			creating = false;
		}
	}

	async function getAiRecommendations() {
		error = '';
		if (!productId) {
			error = t('Pilih produk dulu untuk mengambil rekomendasi AI.');
			return;
		}
		generating = true;
		try {
			const res = await generateCatalogDescription(productId);
			const ai = res.data;
			if (!title) title = products.items.find((p) => p.id === productId)?.name ?? 'Katalog Ekspor';
			if (!description) description = ai.export_description;
			if (ai.technical_specs.length > 0) {
				const specText = ai.technical_specs.map((s) => `${s.label}: ${s.value}`).join('\n');
				if (!tags) tags = ai.technical_specs.slice(0, 3).map((s) => s.value).join(', ');
			}
		} catch {
			error = t('Gagal mengambil rekomendasi AI.');
		} finally {
			generating = false;
		}
	}
</script>

<svelte:head>
	<title>Create Catalog | MauEkspor</title>
</svelte:head>

<AppShell title="Catalogs" eyebrow={t('Create buyer-facing catalog')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Penyiapan katalog')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Kemas produk untuk pasar target.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Katalog memuat konten untuk pembeli, harga, MOQ, dan lembar spesifikasi yang dipakai ulang kutipan. Gunakan tombol AI untuk mengisi deskripsi secara otomatis.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge variant="secondary">{t('Draf katalog dibuat')}</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{title}</h3>
				<p class="text-muted-foreground">
					{t('Katalog berhasil disimpan di backend')}{imageFile ? ` ${t('beserta gambar utama')}` : ''}.
				</p>
				<div class="flex flex-wrap gap-2">
					<Button href={createdId ? `/catalogs/${createdId}` : '/catalogs'}>{t('Buka katalog')}</Button>
					<Button variant="outline" href="/catalogs">{t('Kembali ke katalog')}</Button>
				</div>
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
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label for="cat-product">{t('Produk')}</Label>
					<NativeSelect id="cat-product" bind:value={productId}>
						<option value="">{t('Pilih produk...')}</option>
						{#each products.items as product}
							<option value={product.id}>{product.name} (HS {product.hs})</option>
						{/each}
					</NativeSelect>
				</div>
				<div class="grid gap-2">
					<Label for="cat-project">{t('Proyek')}</Label>
					<NativeSelect id="cat-project" bind:value={projectId}>
						<option value="">{t('Opsional...')}</option>
						{#each seedProjects as project}
							<option value={project.id}>{project.name}</option>
						{/each}
					</NativeSelect>
				</div>
			</div>
			<div class="flex flex-wrap items-center justify-between gap-3">
				<Button type="button" variant="outline" onclick={getAiRecommendations} disabled={generating}>
					{generating ? t('Menghasilkan...') : t('Dapatkan Rekomendasi AI')}
				</Button>
				{#if productId}
					<span class="text-xs font-semibold text-muted-foreground">{t('Deskripsi akan diisi otomatis dari produk.')}</span>
				{/if}
			</div>
			<div class="grid gap-2">
				<Label for="cat-title">{t('Judul katalog')}</Label>
				<Input id="cat-title" bind:value={title} placeholder="Premium Gayo Arabica Coffee Beans 250g" />
			</div>
			<div class="grid gap-2">
				<Label for="cat-market">{t('Pasar target')}</Label>
				<Input id="cat-market" bind:value={targetMarket} placeholder={t('Importir khusus Jepang')} />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label for="cat-moq">{t('MOQ')}</Label><Input id="cat-moq" bind:value={moq} placeholder="2,000 bags" /></div>
				<div class="grid gap-2"><Label for="cat-lead">{t('Waktu tunggu')}</Label><Input id="cat-lead" bind:value={leadTime} placeholder={t('21 hari setelah deposit')} /></div>
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label for="cat-price">{t('Rentang harga')}</Label><Input id="cat-price" bind:value={priceRange} placeholder="FOB USD 20.80-21.40 per bag" /></div>
				<div class="grid gap-2"><Label for="cat-tags">{t('Tag (dipisahkan koma)')}</Label><Input id="cat-tags" bind:value={tags} placeholder="coffee, single-origin" /></div>
			</div>
			<div class="grid gap-2">
				<Label for="cat-desc">{t('Deskripsi untuk pembeli')}</Label>
				<Textarea id="cat-desc" bind:value={description} rows={3} placeholder={t('Deskripsi untuk buyer internasional...')} />
			</div>
			<div class="grid gap-2">
				<Label for="cat-img">{t('Gambar utama (opsional)')}</Label>
				<input id="cat-img" type="file" accept="image/*" class="rounded-lg border bg-muted/30 px-3 py-2 text-sm" onchange={(e) => (imageFile = (e.currentTarget as HTMLInputElement).files?.[0] ?? null)} />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href="/catalogs">{t('Batal')}</Button>
				<Button type="submit" disabled={creating}>{creating ? t('Membuat...') : t('Buat draf katalog')}</Button>
			</div>
		</form>
	{/if}
</AppShell>
