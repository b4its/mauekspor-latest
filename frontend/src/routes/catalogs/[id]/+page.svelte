<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import {
		generateCatalogDescription,
		publishCatalog,
		unpublishCatalog,
		listCatalogImages,
		listVariantTypes,
		generateCatalogAiDescription,
		addCatalogImage,
		deleteCatalogImage
	} from '$lib/api/catalogs';
	import { uploadFileBinary, fileDownloadUrl } from '$lib/api/files';
	import type { CatalogImage, VariantType, CatalogAIDescription } from '$lib/api/catalogs';

	let { data } = $props();
	let published = $state(false);
	let error = $state('');

	let images = $state<CatalogImage[]>([]);
	let variantTypes = $state<VariantType[]>([]);
	let aiDesc = $state<CatalogAIDescription | null>(null);
	let loadingAi = $state(false);
	let newImageUrl = $state('');
	let uploading = $state(false);

	$effect(() => {
		published = data.catalog.status === 'Published';
	});

	$effect(() => {
		listCatalogImages(data.catalog.id)
			.then((res) => (images = res.data))
			.catch(() => {});
		listVariantTypes(data.catalog.id)
			.then((res) => (variantTypes = res.data.data))
			.catch(() => {});
	});

	async function handleUploadImage(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		error = '';
		uploading = true;
		try {
			const res = await uploadFileBinary(file, 'Catalog Image', data.catalog.projectId ?? '', []);
			const url = fileDownloadUrl(res.data.id);
			await addCatalogImage(data.catalog.id, { image_url: url, alt_text: file.name });
			const imgs = (await listCatalogImages(data.catalog.id)).data;
			images = imgs;
		} catch {
			error = 'Gagal mengunggah gambar.';
		} finally {
			uploading = false;
			input.value = '';
		}
	}

	async function handleAddImageUrl() {
		error = '';
		if (!newImageUrl.trim()) return;
		try {
			await addCatalogImage(data.catalog.id, { image_url: newImageUrl.trim(), alt_text: '' });
			newImageUrl = '';
			images = (await listCatalogImages(data.catalog.id)).data;
		} catch {
			error = 'Gagal menambahkan gambar dari URL.';
		}
	}

	async function handleRemoveImage(imageId: string) {
		error = '';
		try {
			await deleteCatalogImage(data.catalog.id, imageId);
			images = images.filter((img) => img.id !== imageId);
		} catch {
			error = 'Gagal menghapus gambar.';
		}
	}

	async function handleGenerate() {
		error = '';
		loadingAi = true;
		try {
			const res = await generateCatalogAiDescription(data.catalog.id, false);
			aiDesc = res.data;
		} catch {
			try {
				await generateCatalogDescription(data.catalog.id);
			} catch {
				error = 'Gagal generate AI copy.';
			}
		} finally {
			loadingAi = false;
		}
	}

	async function handlePublish() {
		error = '';
		try {
			await publishCatalog(data.catalog.id);
			published = true;
		} catch {
			error = 'Gagal mempublikasikan katalog.';
		}
	}

	async function handleUnpublish() {
		error = '';
		try {
			await unpublishCatalog(data.catalog.id);
			published = false;
		} catch {
			error = 'Gagal menarik publikasi katalog.';
		}
	}

	let displayStatus = $derived(published ? 'Published' : data.catalog.status);
	let displayReadiness = $derived(published ? Math.max(data.catalog.readiness, 95) : data.catalog.readiness);
	let displayDescription = $derived(aiDesc?.export_description || data.catalog.description || '');

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.catalog.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.catalog.id} eyebrow="Catalog detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.catalog.title}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.catalog.projectId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Catalog readiness</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayReadiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Buyer-Facing Copy</CardTitle>
					<CardDescription class="mt-1.5 max-w-2xl leading-relaxed">{displayDescription || 'Belum ada deskripsi katalog.'}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href={`/catalogs/${data.catalog.id}/edit`}>Edit catalog</Button>
					<Button variant="outline" onclick={handleGenerate} disabled={loadingAi}>
						{loadingAi ? 'Generating...' : aiDesc ? 'Regenerate AI copy' : 'Generate AI copy'}
					</Button>
					{#if published}
						<Button variant="outline" onclick={handleUnpublish}>Unpublish</Button>
					{:else}
						<Button onclick={handlePublish}>Publish catalog</Button>
					{/if}
				</div>
			</CardHeader>
			{#if error}
				<p class="rounded-lg bg-destructive/10 px-4 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Product <strong class="mt-1 block text-sm font-bold text-foreground">{data.product?.name ?? data.catalog.productId}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Target market <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.targetMarket}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					MOQ <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.moq}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Lead time <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.leadTime}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Price range <strong class="mt-1 block text-sm font-bold text-foreground">{data.catalog.priceRange}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Images <strong class="mt-1 block text-sm font-bold text-foreground">{images.length}</strong>
				</div>
			</CardContent>
		</Card>

		{#if images.length > 0}
			<Card>
				<CardHeader class="flex-row items-center justify-between gap-3">
					<CardTitle>Catalog Images</CardTitle>
					<Badge variant="secondary">{images.length}</Badge>
				</CardHeader>
				<CardContent class="grid gap-3">
					<div class="grid grid-cols-3 gap-2.5">
						{#each images as image}
							<div class="overflow-hidden rounded-lg border bg-muted/40">
								{#if image.imageUrl}
									<img src={image.imageUrl} alt={image.altText || data.catalog.title} class="h-24 w-full object-cover" />
								{:else}
									<div class="flex h-24 items-center justify-center text-xs font-bold text-muted-foreground">No image</div>
								{/if}
								<div class="flex items-center justify-between px-2 py-1">
									{#if image.isPrimary}
										<span class="text-[10px] font-bold text-primary">Primary</span>
									{:else}
										<span class="text-[10px] text-muted-foreground">{image.altText || '—'}</span>
									{/if}
									<button class="text-[10px] font-bold text-destructive hover:underline" onclick={() => handleRemoveImage(image.id)}>Hapus</button>
								</div>
							</div>
						{/each}
					</div>
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader>
				<CardTitle>Add Image</CardTitle>
				<CardDescription>Unggah file (max 25MB) atau tambahkan lewat URL.</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
					Upload file
					<input type="file" accept="image/*,application/pdf" class="rounded-lg border bg-muted/30 px-3 py-2 text-sm" onchange={handleUploadImage} disabled={uploading} />
				</label>
				<div class="flex gap-2">
					<input
						type="text"
						placeholder="Atau URL gambar..."
						class="h-10 flex-1 rounded-md border bg-background px-3 text-sm"
						bind:value={newImageUrl}
					/>
					<Button variant="outline" size="sm" onclick={handleAddImageUrl} disabled={!newImageUrl.trim()}>Tambah URL</Button>
				</div>
				{#if uploading}
					<p class="text-xs font-semibold text-muted-foreground">Mengunggah...</p>
				{/if}
			</CardContent>
		</Card>

		{#if variantTypes.length > 0}
			<Card>
				<CardHeader><CardTitle>Variants</CardTitle></CardHeader>
				<CardContent class="grid gap-2.5">
					{#each variantTypes as vt}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<strong class="text-sm">{vt.typeName}</strong>
							<div class="mt-1.5 flex flex-wrap gap-1.5">
								{#each vt.options ?? [] as option}
									<span class="rounded-full border bg-background/60 px-2.5 py-1 text-xs font-bold">{option.optionName}</span>
								{/each}
							</div>
						</div>
					{/each}
				</CardContent>
			</Card>
		{/if}

		{#if aiDesc}
			<Card class="md:col-span-2">
				<CardHeader>
					<Badge variant="secondary">AI description</Badge>
					<CardTitle>Export description (AI)</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-3">
					<p class="rounded-lg border bg-muted/30 p-3.5 text-sm leading-relaxed">{aiDesc.export_description}</p>
					{#if aiDesc.technical_specs.length > 0}
						<div class="grid gap-2 sm:grid-cols-2">
							{#each aiDesc.technical_specs as spec}
								<div class="rounded-lg border bg-muted/30 p-3 text-xs">
									<span class="text-muted-foreground">{spec.label}</span><br /><b>{spec.value}</b>
								</div>
							{/each}
						</div>
					{/if}
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader><CardTitle>Marketing Highlights</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5">
				{#each data.catalog.highlights ?? [] as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Variants and Incoterms</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5">
				{#each data.catalog.variants ?? [] as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
				{#each data.catalog.incoterms ?? [] as item}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{item}</span>
				{/each}
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">Specification sheet</Badge>
				<CardTitle>Technical Specifications</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3">
				<div class="grid gap-3 sm:grid-cols-2">
					{#each data.catalog.specifications ?? [] as spec}
						<div class="rounded-lg border bg-muted/30 p-3.5">
							<span class="block text-xs font-bold uppercase tracking-wide text-muted-foreground">{spec.label}</span>
							<strong class="mt-1 block text-sm font-bold">{spec.value}</strong>
						</div>
					{/each}
				</div>
				{#if aiDesc}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">AI description siap digunakan. Simpan via edit catalog.</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>
