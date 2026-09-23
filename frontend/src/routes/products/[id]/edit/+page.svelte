<script lang="ts">
	import { untrack } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Alert } from '$lib/components/ui/alert/index.js';

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.product));
	let name = $state(initial.name);
	let category = $state(initial.category);
	let origin = $state(initial.origin);
	let packaging = $state(initial.packaging);
	let netWeight = $state(initial.netWeight);
	let grossWeight = $state(initial.grossWeight);
	let moq = $state(initial.moq);
	let leadTime = $state(initial.leadTime);
	let certificates = $state([...initial.certificates]);
	let certificatesText = $state(certificates.join(', '));
	let saved = $state(false);
	let error = $state('');

	let valid = $derived(name.trim().length > 2 && category.trim().length > 1 && origin.trim().length > 1);

	function save() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib sebelum menyimpan.';
			return;
		}
		saved = true;
	}
</script>

<svelte:head>
	<title>Edit {data.product.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.product.id} eyebrow="Edit product">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Product master data</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Update {data.product.name}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Every field here feeds HS classification, compliance, catalog, and quotation.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge>Product saved</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{name}</h3>
				<p class="text-muted-foreground">
					Perubahan produk tersimpan.
				</p>
				<Button href={`/products/${data.product.id}`}>Back to product</Button>
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
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label>Name</Label>
					<Input bind:value={name} />
				</div>
				<div class="grid gap-2">
					<Label>Category</Label>
					<Input bind:value={category} />
				</div>
			</div>
			<div class="grid gap-2">
				<Label>Origin</Label>
				<Input bind:value={origin} />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label>Net weight</Label>
					<Input bind:value={netWeight} />
				</div>
				<div class="grid gap-2">
					<Label>Gross weight</Label>
					<Input bind:value={grossWeight} />
				</div>
			</div>
			<div class="grid gap-2">
				<Label>Packaging</Label>
				<Input bind:value={packaging} />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2">
					<Label>MOQ</Label>
					<Input bind:value={moq} />
				</div>
				<div class="grid gap-2">
					<Label>Lead time</Label>
					<Input bind:value={leadTime} />
				</div>
			</div>
			<div class="grid gap-2">
				<Label>Certificates (comma separated)</Label>
				<Input bind:value={certificatesText} />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href={`/products/${data.product.id}`}>Cancel</Button>
				<Button type="submit">Save product</Button>
			</div>
		</form>
	{/if}
</AppShell>