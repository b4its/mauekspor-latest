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
			error = 'Lengkapi kolom wajib: nama produk, kategori, dan asal.';
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
				leadTime: leadTime.trim() || undefined
			});
			createdId = res.data.id;
			created = true;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Gagal membuat produk.';
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>New Product | MauEkspor</title>
</svelte:head>

<AppShell title="Products" eyebrow="Add export product">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>Product creation</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Capture the product data every export step needs.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Structured specs here drive HS classification, compliance checks, catalogs, and costing.
				Endpoint prepared in <code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">createProduct()</code>.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge>Product created</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{name}</h3>
				<p class="text-muted-foreground">
					Produk berhasil disimpan ke backend
					{#if createdId}<code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">{createdId}</code>{/if}
					dan siap digunakan di HS classification, compliance, dan katalog.
				</p>
				<Button href="/products">Back to products</Button>
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
				<Label>Name</Label>
				<Input bind:value={name} placeholder="Gayo Arabica Coffee Beans" />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label>Category</Label>
					<NativeSelect bind:value={category}>
						{#each categories as option}
							<option>{option}</option>
						{/each}
					</NativeSelect>
				</div>
				<div class="grid gap-2">
					<Label>Origin</Label>
					<Input bind:value={origin} placeholder="Aceh, Indonesia" />
				</div>
			</div>
			<div class="grid gap-2">
				<Label>Packaging</Label>
				<Input bind:value={packaging} placeholder="250g valve bag, 24 bags per carton" />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label>Net weight</Label><Input bind:value={netWeight} placeholder="250g" /></div>
				<div class="grid gap-2"><Label>Gross weight</Label><Input bind:value={grossWeight} placeholder="280g" /></div>
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label>MOQ</Label><Input bind:value={moq} placeholder="2,000 bags" /></div>
				<div class="grid gap-2"><Label>Lead time</Label><Input bind:value={leadTime} placeholder="21 days" /></div>
			</div>
			<div class="grid gap-2">
				<Label>Certificates (comma separated)</Label>
				<Input bind:value={certificates} placeholder="Halal, Organic in progress" />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href="/products">Cancel</Button>
				<Button type="submit" disabled={creating}>{creating ? 'Creating...' : 'Create product'}</Button>
			</div>
		</form>
	{/if}
</AppShell>