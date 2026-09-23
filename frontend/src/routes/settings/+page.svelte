<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getSettings, updateSettings } from '$lib/api/settings';
	import type { WorkspaceSettings } from '$lib/api/settings';

	let settings = $state<WorkspaceSettings | null>(null);
	let companyName = $state('');
	let country = $state('Indonesia');
	let entityType = $state('');
	let nib = $state('');
	let taxId = $state('');
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	$effect(() => {
		getSettings()
			.then((res) => {
				settings = res.data;
				companyName = res.data.companyName ?? '';
				country = res.data.country ?? 'Indonesia';
				entityType = res.data.entityType ?? '';
				nib = res.data.nib ?? '';
				taxId = res.data.taxId ?? '';
			})
			.catch(() => {});
	});

	async function save() {
		error = '';
		saving = true;
		try {
			await updateSettings({ companyName, country, entityType, nib, taxId });
			saved = true;
		} catch {
			error = 'Gagal menyimpan pengaturan.';
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Settings | MauEkspor</title>
</svelte:head>

<AppShell title="Settings" eyebrow="Organization and access control">
	<div class="grid gap-4 lg:grid-cols-[1.2fr_minmax(360px,0.8fr)]">
		<Card class="bg-gradient-to-br from-background to-secondary/30">
			<CardHeader><Badge>Verified exporter profile</Badge></CardHeader>
			<CardContent class="grid gap-4">
				<CardTitle class="text-3xl font-bold tracking-tight md:text-4xl">{companyName || 'Perusahaan Anda'}</CardTitle>
				<CardDescription class="leading-relaxed">
					Organization settings will hold legal identity, tax data, NIB, production sites,
					verification documents, team permissions, and security policies.
				</CardDescription>

				{#if saved}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Pengaturan tersimpan di backend.</p>
				{/if}
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}

				<form class="grid gap-3" onsubmit={(event) => { event.preventDefault(); save(); }}>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="grid gap-2">
							<Label for="s-name">Company name</Label>
							<Input id="s-name" bind:value={companyName} />
						</div>
						<div class="grid gap-2">
							<Label for="s-country">Country</Label>
							<Input id="s-country" bind:value={country} />
						</div>
					</div>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="grid gap-2">
							<Label for="s-type">Entity type</Label>
							<Input id="s-type" bind:value={entityType} placeholder="Manufacturer exporter" />
						</div>
						<div class="grid gap-2">
							<Label for="s-nib">NIB</Label>
							<Input id="s-nib" bind:value={nib} placeholder="Nomor Induk Berusaha" />
						</div>
					</div>
					<div class="grid gap-2">
						<Label for="s-tax">Tax ID (NPWP)</Label>
						<Input id="s-tax" bind:value={taxId} placeholder="00.000.000.0-000.000" />
					</div>
					<Button type="submit" disabled={saving} class="w-fit">{saving ? 'Saving...' : 'Save settings'}</Button>
				</form>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Organization info</CardTitle></CardHeader>
			<CardContent class="grid gap-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Country <strong class="mt-1 block text-sm font-bold text-foreground">{country || 'Indonesia'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Entity type <strong class="mt-1 block text-sm font-bold text-foreground">{entityType || '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					NIB <strong class="mt-1 block text-sm font-bold text-foreground">{nib || 'Belum diisi'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Security <strong class="mt-1 block text-sm font-bold text-foreground">{settings?.security?.sessionType ?? 'Cookie session'}</strong>
				</div>
			</CardContent>
		</Card>
	</div>
</AppShell>
