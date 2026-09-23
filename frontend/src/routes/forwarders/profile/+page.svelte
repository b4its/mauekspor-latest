<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { createForwarderProfile, updateForwarderProfile, getMyForwarderProfile } from '$lib/api/forwarders';
	import type { ForwarderProfile } from '$lib/api/forwarders';

	let companyName = $state('Nusantara Global Logistics');
	let contactEmail = $state('ops@ngl.example');
	let contactPhone = $state('+62 21 555 0100');
	let specializationRoutes = $state('ID-JP\nID-SG');
	let serviceTypes = $state('Ocean Freight\nCustoms Brokerage');
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');
	let existingId = $state('');

	$effect(() => {
		getMyForwarderProfile()
			.then((res) => {
				const p = res.data;
				existingId = p.id ?? '';
				companyName = p.companyName ?? companyName;
				contactEmail = p.contactInfo?.email ?? contactEmail;
				contactPhone = p.contactInfo?.phone ?? contactPhone;
				specializationRoutes = (p.specializationRoutes ?? []).join('\n');
				serviceTypes = (p.serviceTypes ?? []).join('\n');
			})
			.catch(() => {});
	});

	let valid = $derived(companyName.trim().length > 2 && contactEmail.trim().length > 4);

	async function save() {
		error = '';
		if (!valid) {
			error = 'Lengkapi kolom wajib: company name dan contact email.';
			return;
		}
		saving = true;
		const payload: Partial<ForwarderProfile> = {
			companyName,
			contactInfo: { email: contactEmail, phone: contactPhone },
			specializationRoutes: specializationRoutes.split('\n').map((s) => s.trim()).filter(Boolean),
			serviceTypes: serviceTypes.split('\n').map((s) => s.trim()).filter(Boolean)
		};
		try {
			if (existingId) await updateForwarderProfile(existingId, payload);
			else await createForwarderProfile(payload);
			saved = true;
		} catch {
			error = 'Gagal menyimpan profil forwarder.';
		} finally {
			saving = false;
		}
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
				Company name, rute spesialisasi (ID-JP), dan tipe layanan membentuk evaluasi buyer.
			</p>
		</div>

		{#if saved}
			<Card>
				<CardContent class="grid gap-3 p-5">
					<Badge variant="secondary">Profile saved</Badge>
					<h3 class="text-2xl font-bold tracking-tight">{companyName}</h3>
					<p class="text-sm text-muted-foreground">Profil berhasil disimpan ke backend.</p>
					<Button href="/forwarders/my-profile" class="w-fit">Back to profile</Button>
				</CardContent>
			</Card>
		{:else}
			<form class="grid gap-4 sm:grid-cols-2" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2 sm:col-span-2">
					<Label for="f-company">Company name</Label>
					<Input id="f-company" bind:value={companyName} />
				</div>
				<div class="grid gap-2">
					<Label for="f-email">Contact email</Label>
					<Input id="f-email" bind:value={contactEmail} />
				</div>
				<div class="grid gap-2">
					<Label for="f-phone">Contact phone</Label>
					<Input id="f-phone" bind:value={contactPhone} />
				</div>
				<div class="grid gap-2">
					<Label for="f-routes">Specialization routes (one per line, format ID-XX)</Label>
					<Textarea id="f-routes" bind:value={specializationRoutes} rows={3} />
				</div>
				<div class="grid gap-2">
					<Label for="f-services">Service types (one per line)</Label>
					<Textarea id="f-services" bind:value={serviceTypes} rows={3} />
				</div>

				{#if error}<p class="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-semibold text-destructive sm:col-span-2">{error}</p>{/if}

				<div class="flex flex-wrap gap-2 sm:col-span-2">
					<Button variant="outline" href="/forwarders/my-profile">Cancel</Button>
					<Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save profile'}</Button>
				</div>
			</form>
		{/if}
	</Card>
</AppShell>
