<script lang="ts">
	import { untrack } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.scenario));
	let title = $state(initial.title);
	let destination = $state(initial.destination);
	let incoterm = $state(initial.incoterm);
	let margin = $state(String(initial.margin));
	let exchangeRate = $state(String(initial.exchangeRate));
	let saved = $state(false);
	let error = $state('');

	const incoterms = ['EXW', 'FOB', 'CIF', 'DAP'];

	let valid = $derived(title.trim().length > 3 && destination.trim().length > 1 && Number(margin) >= 0 && Number(exchangeRate) > 0);

	function save() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib dengan benar.';
			return;
		}
		saved = true;
	}
</script>

<svelte:head>
	<title>Edit {data.scenario.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.scenario.id} eyebrow="Edit costing scenario">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">Pricing model</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Update {data.scenario.title}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Adjust Incoterm, margin, and FX assumptions that drive landed cost.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card>
			<CardContent class="grid gap-2 p-6">
				<Badge variant="secondary" class="w-fit">Scenario saved</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{title}</h3>
				<p class="text-sm text-muted-foreground">{destination} · {incoterm} · margin {margin}%. Perubahan tersimpan.</p>
				<Button href={`/costing/${data.scenario.id}`} class="mt-2 w-fit">Back to scenario</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label>Scenario title</Label>
					<Input bind:value={title} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Destination</Label>
						<Input bind:value={destination} />
					</div>
					<div class="grid gap-2">
						<Label>Incoterm</Label>
						<NativeSelect bind:value={incoterm}>
							{#each incoterms as option}<option>{option}</option>{/each}
						</NativeSelect>
					</div>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Margin %</Label>
						<Input bind:value={margin} inputmode="decimal" />
					</div>
					<div class="grid gap-2">
						<Label>Exchange rate</Label>
						<Input bind:value={exchangeRate} inputmode="decimal" />
					</div>
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href={`/costing/${data.scenario.id}`}>Cancel</Button>
					<Button type="submit">Save scenario</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>
