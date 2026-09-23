<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { buyers } from '$lib/data/trade';

	const initial = buyers[0];
	let name = $state(initial.name);
	let segment = $state(initial.segment);
	let country = $state(initial.country);
	let paymentProfile = $state(initial.paymentProfile);
	let estimatedAnnualValue = $state(String(initial.estimatedAnnualValue));
	let saved = $state(false);
	let error = $state('');

	let valid = $derived(name.trim().length > 2 && country.trim().length > 1 && segment.trim().length > 1);

	function save() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib: nama, segment, dan negara.';
			return;
		}
		saved = true;
	}
</script>

<svelte:head>
	<title>Edit Buyer Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Buyer Profile" eyebrow="Edit importer identity">
	<Card class="grid gap-6 border bg-gradient-to-br from-background to-secondary/30 p-6 md:p-8">
		<div>
			<Badge variant="secondary">Profile</Badge>
			<h2 class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Update how exporters see your company.</h2>
			<p class="mt-2 max-w-2xl leading-relaxed text-muted-foreground">
				Segment, payment profile, and estimated pipeline shape exporter targeting.
			</p>
		</div>

		{#if saved}
			<Card>
				<CardContent class="grid gap-3 p-5">
					<Badge>Profile saved</Badge>
					<h3 class="text-2xl font-bold tracking-tight">{name}</h3>
					<p class="text-sm text-muted-foreground">Profil tersimpan.</p>
					<Button href="/buyers/my-profile" class="w-fit">Back to profile</Button>
				</CardContent>
			</Card>
		{:else}
			<form class="grid gap-4" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label>Company name</Label>
					<Input bind:value={name} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>Segment</Label>
						<Input bind:value={segment} />
					</div>
					<div class="grid gap-2">
						<Label>Country</Label>
						<Input bind:value={country} />
					</div>
				</div>
				<div class="grid gap-2">
					<Label>Payment profile</Label>
					<Input bind:value={paymentProfile} />
				</div>
				<div class="grid gap-2">
					<Label>Estimated annual value USD</Label>
					<Input bind:value={estimatedAnnualValue} inputmode="numeric" />
				</div>

				{#if error}<p class="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-semibold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-2">
					<Button variant="outline" href="/buyers/my-profile">Cancel</Button>
					<Button type="submit">Save profile</Button>
				</div>
			</form>
		{/if}
	</Card>
</AppShell>