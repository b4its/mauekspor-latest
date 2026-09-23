<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { products, projects } from '$lib/data/trade';
	import { createCostingScenario } from '$lib/api/costing';

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
			error = 'Lengkapi kolom wajib: judul, produk, destination, dan target margin.';
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
			error = 'Gagal membuat skenario costing.';
		} finally {
			creating = false;
		}
	}
</script>

<svelte:head>
	<title>Create Costing Scenario | MauEkspor</title>
</svelte:head>

<AppShell title="Costing" eyebrow="Create costing scenario">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Pricing model</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Model margin and landed cost for a market.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Covers EXW through DAP, exchange rates, freight, insurance, and destination fees.
				Skenario disimpan ke backend.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if created}
		<Card>
			<CardContent class="grid gap-2 p-6">
				<Badge variant="secondary" class="w-fit">Scenario drafted</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{title}</h3>
				<p class="text-sm text-muted-foreground">{destination} · {incoterm} · target margin {targetMargin}%. Skenario tersimpan di backend.</p>
				<Button href="/costing" class="mt-2 w-fit">Back to costing</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); create(); }}>
				<div class="grid gap-2">
					<Label>Scenario title</Label>
					<Input bind:value={title} placeholder="Japan Coffee FOB Base Case" />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Project</Label>
						<NativeSelect bind:value={projectId}>
							<option value="">Optional...</option>
							{#each projects as project}<option value={project.id}>{project.name}</option>{/each}
						</NativeSelect>
					</div>
					<div class="grid gap-2">
						<Label>Product</Label>
						<NativeSelect bind:value={productId}>
							<option value="">Optional...</option>
							{#each products as product}<option value={product.id}>{product.name}</option>{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Destination</Label>
						<Input bind:value={destination} placeholder="Japan" />
					</div>
					<div class="grid gap-2">
						<Label>Incoterm</Label>
						<NativeSelect bind:value={incoterm}>
							{#each incoterms as option}<option>{option}</option>{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-2">
					<Label>Target margin %</Label>
					<Input bind:value={targetMargin} inputmode="decimal" />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href="/costing">Cancel</Button>
					<Button type="submit" disabled={creating}>{creating ? 'Creating...' : 'Create scenario draft'}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>
