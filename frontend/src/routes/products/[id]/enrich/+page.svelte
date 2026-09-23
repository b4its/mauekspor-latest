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
	import { updateProduct } from '$lib/api/products';

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.product));
	let hsCode = $state(initial.hs);
	let sku = $state(initial.sku ?? `MEK-${initial.id.split('-').pop()}`);
	let descriptionEn = $state(initial.description_english_b2b ?? `${initial.name} - premium export grade, suitable for B2B distribution.`);
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	let valid = $derived(/^\d{4}(\.\d{2})?$/.test(hsCode.trim()));

	async function save() {
		error = '';
		if (!valid) {
			error = 'HS Code harus 4 digit atau 6 digit (misal 0901 atau 0901.21).';
			return;
		}
		saving = true;
		try {
			await updateProduct(data.product.id, {
				hs: hsCode.trim(),
				hs_code: hsCode.trim(),
				sku,
				description_english_b2b: descriptionEn
			});
			saved = true;
		} catch {
			error = 'Gagal menyimpan override enrichment ke backend.';
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Override AI Enrichment | MauEkspor</title>
</svelte:head>

<AppShell title="Enrichment Override" eyebrow={`${data.product.name} - AI result edit`}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Manual override</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				Reviews and overrides the AI enrichment results.
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				A human checkpoint keeps the HS recommendation accurate before it touches commercial documents.
				Endpoint prepared in <code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">overrideEnrichment()</code>.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardContent class="grid gap-4 p-0">
				<Badge>Override saved</Badge>
				<h3 class="text-xl font-semibold tracking-tight">Manually edited</h3>
				<p class="text-muted-foreground">
					HS {hsCode} is now the approved recommendation for {data.product.name}. Badge will show
					"Manually Edited" on the product detail page.
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
			<div class="grid gap-2">
				<Label>HS Code recommendation</Label>
				<Input bind:value={hsCode} placeholder="0901.21" />
				<small class="text-xs text-muted-foreground">8-digit validation ready; current value must match 4 or 6 digit format.</small>
			</div>
			<div class="grid gap-2">
				<Label>Generated SKU</Label>
				<Input bind:value={sku} />
			</div>
			<div class="grid gap-2">
				<Label>Description (English B2B)</Label>
				<Textarea bind:value={descriptionEn} rows={4} />
			</div>

			{#if error}<Alert variant="destructive">{error}</Alert>{/if}

			<div class="flex flex-wrap gap-2">
				<Button variant="outline" href={`/products/${data.product.id}`}>Cancel</Button>
				<Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save override'}</Button>
			</div>
		</form>
	{/if}
</AppShell>