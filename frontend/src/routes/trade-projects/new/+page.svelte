<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { createTradeProject } from '$lib/api/trade-projects';

	const projectTypes = ['Exporter-led', 'Buyer RFQ', 'Forwarder-supported'];
	const steps = ['Scope', 'Product & Buyer', 'Commercial Terms'];

	let step = $state(0);
	let projectType = $state('Exporter-led');
	let projectName = $state('');
	let destination = $state('');
	let product = $state('');
	let buyer = $state('');
	let incoterm = $state('');
	let targetValue = $state('');
	let eta = $state('');
	let created = $state(false);
	let error = $state('');

	let progress = $derived(Math.round(((step + 1) / steps.length) * 100));
	let currentValid = $derived(
		step === 0
			? projectName.trim().length > 2 && destination.trim().length > 1
			: step === 1
				? product.trim().length > 2 && buyer.trim().length > 1
				: incoterm.trim().length > 2 && Number(targetValue) > 0
	);

	async function next() {
		error = '';
		if (!currentValid) {
			error = 'Lengkapi field wajib pada langkah ini sebelum lanjut.';
			return;
		}

		if (step < steps.length - 1) {
			step += 1;
			return;
		}

		try {
			await createTradeProject({
				name: projectName,
				projectType,
				product,
				buyer,
				country: destination,
				incoterm,
				targetValue: Number(targetValue),
				eta: eta || undefined
			});
			created = true;
		} catch {
			error = 'Gagal membuat proyek. Coba lagi.';
		}
	}

	function back() {
		error = '';
		step = Math.max(0, step - 1);
	}
</script>

<svelte:head>
	<title>New Trade Project | MauEkspor</title>
</svelte:head>

<AppShell title="New Trade Project" eyebrow="Create export-import workspace">
	<div class="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(360px,0.72fr)]">
		<div class="space-y-6">
			<Badge>Guided setup</Badge>
			<h2 class="text-3xl font-bold tracking-tight md:text-4xl">Start with the commercial objective, then attach product and compliance data.</h2>
			<p class="leading-relaxed text-muted-foreground">
				This wizard creates the frontend contract for a future backend workflow: persist project,
				create initial tasks, and trigger HS/compliance jobs asynchronously.
			</p>

			<div class="stepper flex flex-wrap gap-2.5" aria-label="Wizard progress">
				{#each steps as item, index}
					<Button
						variant={step === index ? 'default' : 'outline'}
						onclick={() => (step = index)}
					>
						<span class="grid size-6 place-items-center rounded-full bg-primary/10 text-xs">{index + 1}</span>{item}
					</Button>
				{/each}
			</div>

			<Card class="p-5">
				<Badge variant="secondary">Draft preview</Badge>
				<h3 class="mt-3 text-2xl font-bold tracking-tight">{projectName || 'Untitled export project'}</h3>
				<div class="mt-4 grid grid-cols-2 gap-3">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Type<strong class="mt-1 block text-sm font-bold text-foreground">{projectType}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Destination<strong class="mt-1 block text-sm font-bold text-foreground">{destination || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Product<strong class="mt-1 block text-sm font-bold text-foreground">{product || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Buyer<strong class="mt-1 block text-sm font-bold text-foreground">{buyer || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Incoterm<strong class="mt-1 block text-sm font-bold text-foreground">{incoterm || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">Target<strong class="mt-1 block text-sm font-bold text-foreground">{targetValue ? `$${Number(targetValue).toLocaleString('en-US')}` : '-'}</strong></div>
				</div>
			</Card>
		</div>

		<Card class="h-fit">
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); next(); }}>
				<div class="progress-head flex items-center justify-between gap-3">
					<div>
						<span class="text-xs font-bold text-muted-foreground">Step {step + 1} of {steps.length}</span>
						<strong class="mt-0.5 block text-xl font-bold tracking-tight">{steps[step]}</strong>
					</div>
					<b class="text-xl font-bold tracking-tight">{progress}%</b>
				</div>
				<Progress value={progress} />

				{#if created}
					<div class="rounded-xl border bg-muted/30 p-5">
						<Badge>Draft created</Badge>
						<h3 class="mt-3 text-2xl font-bold tracking-tight">{projectName}</h3>
						<p class="mt-1 leading-relaxed text-muted-foreground">
							Proyek berhasil disimpan di backend. Selanjutnya timeline &amp; compliance jobs
							akan menempel ke proyek ini secara asinkron.
						</p>
						<Button href="/trade-projects" class="mt-3 w-fit">Back to projects</Button>
					</div>
				{:else}
					{#if step === 0}
						<div class="field grid gap-2">
							<Label>Project type</Label>
							<NativeSelect bind:value={projectType}>
								{#each projectTypes as type}
									<option>{type}</option>
								{/each}
							</NativeSelect>
						</div>
						<div class="field grid gap-2">
							<Label>Project name</Label>
							<Input bind:value={projectName} placeholder="Japan Coffee Trial Shipment" />
						</div>
						<div class="field grid gap-2">
							<Label>Destination country</Label>
							<Input bind:value={destination} placeholder="Japan" />
						</div>
					{:else if step === 1}
						<div class="field grid gap-2">
							<Label>Product</Label>
							<Input bind:value={product} placeholder="Gayo Arabica Coffee Beans" />
						</div>
						<div class="field grid gap-2">
							<Label>Buyer or prospect</Label>
							<Input bind:value={buyer} placeholder="Hikari Foods Co." />
						</div>
					{:else}
						<div class="field grid gap-2">
							<Label>Target Incoterm</Label>
							<Input bind:value={incoterm} placeholder="FOB Tanjung Priok" />
						</div>
						<div class="field grid gap-2">
							<Label>Target value USD</Label>
							<Input bind:value={targetValue} inputmode="decimal" placeholder="42800" />
						</div>
						<div class="field grid gap-2">
							<Label>Estimated delivery date</Label>
							<Input bind:value={eta} type="date" />
						</div>
					{/if}

					{#if error}
						<p class="form-alert rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}

					<div class="wizard-actions flex flex-wrap items-center justify-between gap-3">
						<Button variant="outline" disabled={step === 0} type="button" onclick={back}>Back</Button>
						<Button type="submit">{step === steps.length - 1 ? 'Create draft project' : 'Continue'}</Button>
					</div>
				{/if}
			</form>
		</Card>
	</div>
</AppShell>
