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

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.catalog));
	let title = $state(initial.title);
	let targetMarket = $state(initial.targetMarket);
	let moq = $state(initial.moq);
	let leadTime = $state(initial.leadTime);
	let priceRange = $state(initial.priceRange);
	let description = $state(initial.description);
	let saved = $state(false);
	let error = $state('');

	let valid = $derived(title.trim().length > 3 && targetMarket.trim().length > 1 && moq.trim().length > 1);

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
	<title>Edit {data.catalog.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.catalog.id} eyebrow="Edit catalog">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Catalog master data</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Update {data.catalog.title}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Copy, pricing, and target market changes refresh the buyer-facing catalog.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge variant="secondary">Catalog saved</Badge>
				<h3 class="text-xl font-semibold tracking-tight">{title}</h3>
				<p class="text-muted-foreground">
					Perubahan katalog tersimpan.
				</p>
				<Button href={`/catalogs/${data.catalog.id}`}>Back to catalog</Button>
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
				<Label>Catalog title</Label>
				<Input bind:value={title} />
			</div>
			<div class="grid gap-2">
				<Label>Target market</Label>
				<Input bind:value={targetMarket} />
			</div>
			<div class="grid gap-4 sm:grid-cols-2">
				<div class="grid gap-2"><Label>MOQ</Label><Input bind:value={moq} /></div>
				<div class="grid gap-2"><Label>Lead time</Label><Input bind:value={leadTime} /></div>
			</div>
			<div class="grid gap-2">
				<Label>Price range</Label>
				<Input bind:value={priceRange} />
			</div>
			<div class="grid gap-2">
				<Label>Buyer-facing description</Label>
				<Textarea bind:value={description} rows={3} />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href={`/catalogs/${data.catalog.id}`}>Cancel</Button>
				<Button type="submit">Save catalog</Button>
			</div>
		</form>
	{/if}
</AppShell>