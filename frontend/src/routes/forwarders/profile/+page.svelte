<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { forwarders } from '$lib/data/trade';

	const initial = forwarders[0];
	let coverage = $state(initial.coverage);
	let mode = $state(initial.mode);
	let onTimeRate = $state(String(initial.onTimeRate));
	let quoteSpeed = $state(initial.quoteSpeed);
	let contact = $state(initial.contact);
	let lanes = $state(initial.lanes.join('\n'));
	let saved = $state(false);
	let error = $state('');

	let valid = $derived(coverage.trim().length > 2 && contact.trim().length > 4);

	function save() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib: coverage dan contact.';
			return;
		}
		saved = true;
	}
</script>

<svelte:head>
	<title>Edit Forwarder Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Forwarder Profile" eyebrow="Edit freight partner identity">
	<Card class="grid gap-6 border bg-gradient-to-br from-background to-secondary/30 p-6 md:p-8">
		<div>
			<Badge variant="secondary">Profile</Badge>
			<h2 class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Update how buyers see your freight network.</h2>
			<p class="mt-2 max-w-2xl leading-relaxed text-muted-foreground">
				Coverage, mode, lanes, quote speed, and on-time performance shape buyer evaluation.
			</p>
		</div>

		{#if saved}
			<Card>
				<CardContent class="grid gap-3 p-5">
					<Badge variant="secondary">Profile saved</Badge>
					<h3 class="text-2xl font-bold tracking-tight">{coverage}</h3>
					<p class="text-sm text-muted-foreground">Profil berhasil disimpan.</p>
					<Button href="/forwarders/my-profile" class="w-fit">Back to profile</Button>
				</CardContent>
			</Card>
		{:else}
			<form class="grid gap-4 sm:grid-cols-2" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label>Coverage</Label>
					<Input bind:value={coverage} />
				</div>
				<div class="grid gap-2">
					<Label>Primary mode</Label>
					<Input bind:value={mode} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label>On-time rate %</Label>
						<Input bind:value={onTimeRate} inputmode="numeric" />
					</div>
					<div class="grid gap-2">
						<Label>Quote speed</Label>
						<Input bind:value={quoteSpeed} placeholder="4 hours" />
					</div>
				</div>
				<div class="grid gap-2">
					<Label>Contact email</Label>
					<Input bind:value={contact} />
				</div>
				<div class="grid gap-2">
					<Label>Lanes (one per line)</Label>
					<Textarea bind:value={lanes} rows={3} />
				</div>

				{#if error}<p class="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-semibold text-destructive sm:col-span-2">{error}</p>{/if}

				<div class="flex flex-wrap gap-2 sm:col-span-2">
					<Button variant="outline" href="/forwarders/my-profile">Cancel</Button>
					<Button type="submit">Save profile</Button>
				</div>
			</form>
		{/if}
	</Card>
</AppShell>
