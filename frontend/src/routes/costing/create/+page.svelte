<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { products as seedProducts, projects as seedProjects } from '$lib/data/trade';
	import { listProducts } from '$lib/api/products';
	import { listTradeProjects } from '$lib/api/trade-projects';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { createCostingScenario } from '$lib/api/costing';
	import { t } from '$lib/i18n.svelte';

	let projects = createRemoteList(listTradeProjects, seedProjects);
	let products = createRemoteList(listProducts, seedProducts);
	projects.load();
	products.load();

	let projectId = $state('');
	let productId = $state('');
	let title = $state('');
	let destination = $state('');
	let incoterm = $state('FOB');
	let targetMargin = $state('22');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	const incoterms = ['EXW', 'FOB', 'CIF', 'DAP'];

	let valid = $derived(title.trim().length > 3 && productId && destination.trim().length > 1 && Number(targetMargin) > 0);

	async function create() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib: judul, produk, destination, dan target margin.');
			return;
		}
		creating = true;
		try {
			await createCostingScenario({
				title,
				projectId,
				productId,
				incoterm: incoterm as 'EXW' | 'FOB' | 'CIF' | 'DAP',
				margin: Number(targetMargin),
				destination
			});
			created = true;
		} catch {
			error = t('Gagal membuat skenario costing.');
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Buat Skenario Costing')} | MauEkspor</title>
</svelte:head>

<AppShell title="Costing" eyebrow={t('Create costing scenario')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Model harga')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Model margin dan biaya landed untuk sebuah pasar.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Mencakup EXW hingga DAP, kurs, freight, asuransi, dan biaya tujuan. Skenario disimpan ke backend.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card>
			<CardContent class="grid gap-2 p-6">
				<Badge variant="secondary" class="w-fit">{t('Skenario dibuat')}</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{title}</h3>
				<p class="text-sm text-muted-foreground">{destination} · {incoterm} · {t('margin target')} {targetMargin}%. {t('Skenario tersimpan di backend.')}</p>
				<Button href="/costing" class="mt-2 w-fit">{t('Kembali ke costing')}</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); create(); }}>
				<div class="grid gap-2">
					<Label>{t('Judul skenario')}</Label>
					<Input bind:value={title} placeholder="Japan Coffee FOB Base Case" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>{t('Proyek')}</Label>
						<NativeSelect bind:value={projectId}>
							<option value="">{t('Opsional...')}</option>
							{#each projects.items as project}<option value={project.id}>{project.name}</option>{/each}
						</NativeSelect>
					</div>
					<div class="grid gap-2">
						<Label>{t('Produk')}</Label>
						<NativeSelect bind:value={productId}>
							<option value="">{t('Opsional...')}</option>
							{#each products.items as product}<option value={product.id}>{product.name}</option>{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>{t('Tujuan')}</Label>
						<Input bind:value={destination} placeholder="Japan" />
					</div>
					<div class="grid gap-2">
						<Label>{t('Incoterm')}</Label>
						<NativeSelect bind:value={incoterm}>
							{#each incoterms as option}<option>{option}</option>{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-2">
					<Label>{t('Target margin %')}</Label>
					<Input bind:value={targetMargin} inputmode="decimal" />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href="/costing">{t('Batal')}</Button>
					<Button type="submit" disabled={creating}>{creating ? t('Membuat...') : t('Buat draf skenario')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>
