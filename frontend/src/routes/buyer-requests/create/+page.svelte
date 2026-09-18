<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';
	import { Input } from '$lib/components/ui/input/index.js';
	
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { buyers as seedBuyers, products as seedProducts } from '$lib/data/trade';
	import { listBuyers } from '$lib/api/buyers';
	import { listProducts } from '$lib/api/products';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { createBuyerRequest } from '$lib/api/buyer-requests';

	let buyers = createRemoteList(listBuyers, seedBuyers);
	let products = createRemoteList(listProducts, seedProducts);
	buyers.load();
	products.load();

	let subject = $state('');
	let buyerId = $state('');
	let productId = $state('');
	let destination = $state('');
	let quantity = $state('');
	let deadline = $state('');
	let requirements = $state('');
	let productCategory = $state('');
	let hsCodeTarget = $state('');
	let specRequirements = $state('');
	let keywordTags = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let valid = $derived(subject.trim().length > 4 && buyerId && productId && destination.trim().length > 1 && quantity.trim().length > 1 && deadline);

	async function create() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib pada permintaan ini.');
			return;
		}
		creating = true;
		try {
			await createBuyerRequest({
				subject,
				buyerId,
				productId,
				destination,
				quantity,
				deadline,
				requirements: requirements.split('\n').filter(Boolean),
				product_category: productCategory,
				hs_code_target: hsCodeTarget,
				spec_requirements: specRequirements,
				keyword_tags: keywordTags.split(',').map((t) => t.trim()).filter(Boolean)
			});
			created = true;
		} catch {
			error = t('Gagal membuat permintaan buyer.');
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Permintaan Buyer Baru')} | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Requests" eyebrow={t('Log inbound demand')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Permintaan inbound')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Catat permintaan buyer sebelum basi.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Lampirkan buyer, kandidat produk, tujuan, jumlah, dan batas waktu agar mesin pencocokan dapat mengusulkan langkah berikutnya. Permintaan disimpan ke backend.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Permintaan tercatat')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{subject}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					{quantity} {t('ke')} {destination}. {t('Permintaan tersimpan di backend.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/buyer-requests">{t('Kembali ke permintaan')}</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-1" onsubmit={(event) => { event.preventDefault(); create(); }}>
				<div class="grid gap-2">
					<Label for="br-subject">{t('Subjek')}</Label>
					<Input id="br-subject" bind:value={subject} placeholder="Trial shipment for Gayo Arabica coffee" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="br-buyer">{t('Pembeli')}</Label>
						<SearchableSelect bind:value={buyerId} options={buyers.items.map((b) => ({ value: b.id, label: b.name, sub: b.country }))} />
					</div>
					<div class="grid gap-2">
						<Label for="br-product">{t('Produk')}</Label>
						<SearchableSelect bind:value={productId} options={products.items.map((p) => ({ value: p.id, label: p.name, sub: p.hs ? `HS ${p.hs}` : '' }))} />
					</div>
				</div>
				<div class="grid gap-2">
					<Label for="br-dest">{t('Tujuan')}</Label>
					<Input id="br-dest" bind:value={destination} placeholder="Japan" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="br-qty">{t('Jumlah')}</Label>
						<Input id="br-qty" bind:value={quantity} placeholder="2,000 bags" />
					</div>
					<div class="grid gap-2">
						<Label for="br-deadline">{t('Batas waktu')}</Label>
						<Input id="br-deadline" bind:value={deadline} type="date" />
					</div>
				</div>
				<div class="grid gap-2">
					<Label for="br-req">{t('Persyaratan (satu per baris)')}</Label>
					<Textarea id="br-req" bind:value={requirements} rows={3} placeholder="Japanese label&#10;Lab report&#10;FOB quote" />
				</div>

				<div class="rounded-xl border bg-muted/30 p-4">
					<h4 class="text-sm font-bold">{t('Detail matching (opsional)')}</h4>
					<p class="mt-1 text-xs text-muted-foreground">{t('Semakin detail, semakin akurat skor kecocokan dengan katalog.')}</p>
					<div class="mt-3 grid gap-4 sm:grid-cols-2">
						<div class="grid gap-2">
							<Label for="br-cat">{t('Kategori produk')}</Label>
							<Input id="br-cat" bind:value={productCategory} placeholder="Makanan Olahan / Coffee" />
						</div>
						<div class="grid gap-2">
							<Label for="br-hs">{t('HS code target')}</Label>
							<Input id="br-hs" bind:value={hsCodeTarget} placeholder="0901.21" />
						</div>
					</div>
					<div class="grid gap-2">
						<Label for="br-spec">{t('Persyaratan spesifikasi')}</Label>
						<Textarea id="br-spec" bind:value={specRequirements} rows={2} placeholder="contoh: single origin, fully washed" />
					</div>
					<div class="grid gap-2">
						<Label for="br-tags">{t('Tag kata kunci (dipisahkan koma)')}</Label>
						<Input id="br-tags" bind:value={keywordTags} placeholder="arabica, specialty, single-origin" />
					</div>
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href="/buyer-requests">{t('Batal')}</Button>
					<Button type="submit" disabled={creating}>{creating ? t('Menyimpan...') : t('Catat permintaan buyer')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>