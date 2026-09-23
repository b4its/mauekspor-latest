<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { buyers, products } from '$lib/data/trade';
	import { createBuyerRequest } from '$lib/api/buyer-requests';

	let subject = $state('');
	let buyerId = $state('');
	let productId = $state('');
	let destination = $state('');
	let quantity = $state('');
	let deadline = $state('');
	let requirements = $state('');
	let created = $state(false);
	let creating = $state(false);
	let error = $state('');

	let valid = $derived(subject.trim().length > 4 && buyerId && productId && destination.trim().length > 1 && quantity.trim().length > 1 && deadline);

	async function create() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib pada permintaan ini.';
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
				requirements: requirements.split('\n').filter(Boolean)
			});
			created = true;
		} catch {
			error = 'Gagal membuat permintaan buyer.';
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>New Buyer Request | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Requests" eyebrow="Log inbound demand">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Inbound demand</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Log a buyer request before it goes stale.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Attach a buyer, product candidate, destination, quantity, and deadline so the matching engine
				can propose next steps. Permintaan disimpan ke backend.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">Request logged</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{subject}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					{quantity} to {destination}. Permintaan tersimpan di backend.
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/buyer-requests">Back to requests</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-1" onsubmit={(event) => { event.preventDefault(); create(); }}>
				<div class="grid gap-2">
					<Label>Subject</Label>
					<Input bind:value={subject} placeholder="Trial shipment for Gayo Arabica coffee" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Buyer</Label>
						<NativeSelect bind:value={buyerId}>
							<option value="">Select buyer...</option>
							{#each buyers as buyer}
								<option value={buyer.id}>{buyer.name}</option>
							{/each}
						</NativeSelect>
					</div>
					<div class="grid gap-2">
						<Label>Product</Label>
						<NativeSelect bind:value={productId}>
							<option value="">Select product...</option>
							{#each products as product}
								<option value={product.id}>{product.name}</option>
							{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-2">
					<Label>Destination</Label>
					<Input bind:value={destination} placeholder="Japan" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Quantity</Label>
						<Input bind:value={quantity} placeholder="2,000 bags" />
					</div>
					<div class="grid gap-2">
						<Label>Deadline</Label>
						<Input bind:value={deadline} type="date" />
					</div>
				</div>
				<div class="grid gap-2">
					<Label>Requirements (one per line)</Label>
					<Textarea bind:value={requirements} rows={3} placeholder="Japanese label&#10;Lab report&#10;FOB quote" />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href="/buyer-requests">Cancel</Button>
					<Button type="submit" disabled={creating}>{creating ? 'Saving...' : 'Log buyer request'}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>