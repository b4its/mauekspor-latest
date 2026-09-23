<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { businessProfiles } from '$lib/data/trade';
	import { updateBusinessProfile } from '$lib/api/business-profile';

	let profile = $state(businessProfiles[0]);
	let companyName = $state(profile.companyName);
	let address = $state(profile.address);
	let productionCapacity = $state(profile.productionCapacity);
	let yearEstablished = $state(String(profile.yearEstablished));
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	let valid = $derived(companyName.trim().length > 2 && address.trim().length > 3 && Number(yearEstablished) > 1900);

	async function save() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib dengan benar sebelum menyimpan.';
			return;
		}
		saving = true;
		try {
			await updateBusinessProfile(profile.id, {
				companyName,
				address,
				productionCapacity,
				yearEstablished: Number(yearEstablished)
			});
			saved = true;
		} catch {
			error = 'Gagal menyimpan profil.';
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Edit Business Profile | MauEkspor</title>
</svelte:head>

<AppShell title="Business Profile" eyebrow="Edit UMKM identity">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">Identity</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Update company details used across the workspace.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				Changes here are reflected in product catalogs, compliance files, and future quotations.
				Perubahan disimpan ke backend.
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">Saved</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{companyName}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					Profil tersimpan di backend.
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href="/business-profile">Back to profile</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-1 sm:grid-cols-2" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label>Company name</Label>
					<Input bind:value={companyName} />
				</div>
				<div class="grid gap-2">
					<Label>Address</Label>
					<Input bind:value={address} />
				</div>
				<div class="grid gap-2">
					<Label>Production capacity per month</Label>
					<Input bind:value={productionCapacity} />
				</div>
				<div class="grid gap-2">
					<Label>Year established</Label>
					<Input bind:value={yearEstablished} inputmode="numeric" />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive sm:col-span-2">{error}</p>{/if}

				<div class="flex flex-wrap items-center gap-3 sm:col-span-2">
					<Button variant="outline" href="/business-profile">Cancel</Button>
					<Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>