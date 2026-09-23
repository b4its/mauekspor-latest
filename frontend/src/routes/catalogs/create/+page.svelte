<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Alert } from '$lib/components/ui/alert/index.js';
	import { products, projects } from '$lib/data/trade';
	import { createCatalog } from '$lib/api/catalogs';

	let productId = $state('');
	let projectId = $state('');
	let title = $state('');
	let targetMarket = $state('');
	let moq = $state('');
	let leadTime = $state('');
	let priceRange = $state('');
	let created = $state(false);
	let error = $state('');

	let valid = $derived(title.trim().length > 3 && productId && targetMarket.trim().length > 1 && moq.trim().length > 1);

	async function create() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib: judul, produk, target market, dan MOQ.';
			return;
		}
		try {
			await createCatalog({
				productId,
				projectId: projectId || products[0]?.id,
				title,
				targetMarket,
				moq,
				leadTime: leadTime || 'TBD'
			});
			created = true;
		} catch {
			error = 'Gagal membuat katalog. Coba lagi.';
		}
	}
</script>

<svelte:head>
	<title>Create Catalog | MauEkspor</title>
</svelte:head>

<AppShell title="Catalogs" eyebrow="Create buyer-facing catalog">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Catalog setup</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Package a product for a target market.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				The catalog carries the buyer-facing copy, pricing, MOQ, and spec sheet that quotations
				reuse.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge variant="secondary">Catalog draft created</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{title}</h3>
				<p class="text-muted-foreground">
					Katalog berhasil disimpan di backend.
				</p>
				<Button href="/catalogs">Back to catalogs</Button>
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
					<Label>Product</Label>
					<NativeSelect bind:value={productId}>
						<option value="">Select product...</option>
						{#each products as product}
							<option value={product.id}>{product.name}</option>
						{/each}
					</NativeSelect>
				</div>
				<div class="grid gap-2">
					<Label>Project</Label>
					<NativeSelect bind:value={projectId}>
						<option value="">Optional...</option>
						{#each projects as project}
							<option value={project.id}>{project.name}</option>
						{/each}
					</NativeSelect>
				</div>
			</div>
			<div class="grid gap-2">
				<Label>Catalog title</Label>
				<Input bind:value={title} placeholder="Premium Gayo Arabica Coffee Beans 250g" />
			</div>
			<div class="grid gap-2">
				<Label>Target market</Label>
				<Input bind:value={targetMarket} placeholder="Japan specialty importers" />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label>MOQ</Label><Input bind:value={moq} placeholder="2,000 bags" /></div>
				<div class="grid gap-2"><Label>Lead time</Label><Input bind:value={leadTime} placeholder="21 days after deposit" /></div>
			</div>
			<div class="grid gap-2">
				<Label>Price range</Label>
				<Input bind:value={priceRange} placeholder="FOB USD 20.80-21.40 per bag" />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href="/catalogs">Cancel</Button>
				<Button type="submit">Create catalog draft</Button>
			</div>
		</form>
	{/if}
</AppShell>