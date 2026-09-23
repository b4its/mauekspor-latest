<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';

	const members = [
		{ name: 'Ayu Pratama', role: 'Owner', access: 'Full access' },
		{ name: 'Rizal Hakim', role: 'Compliance', access: 'Evidence and documents' },
		{ name: 'Maya Santoso', role: 'Logistics', access: 'Shipments and forwarders' }
	];
</script>

<svelte:head>
	<title>Settings | MauEkspor</title>
</svelte:head>

<AppShell title="Settings" eyebrow="Organization and access control">
	<div class="grid gap-4 lg:grid-cols-[1.2fr_minmax(360px,0.8fr)]">
		<Card class="bg-gradient-to-br from-background to-secondary/30">
			<CardHeader><Badge>Verified exporter profile</Badge></CardHeader>
			<CardContent class="grid gap-4">
				<CardTitle class="text-3xl font-bold tracking-tight md:text-4xl">PT Kopi Gayo Nusantara</CardTitle>
				<CardDescription class="leading-relaxed">
					Organization settings will hold legal identity, tax data, NIB, production sites,
					verification documents, team permissions, and security policies.
				</CardDescription>
				<div class="grid gap-3 sm:grid-cols-2">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						Country <strong class="mt-1 block text-sm font-bold text-foreground">Indonesia</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						Entity type <strong class="mt-1 block text-sm font-bold text-foreground">Manufacturer exporter</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						NIB <strong class="mt-1 block text-sm font-bold text-foreground">Ready for backend</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						Security <strong class="mt-1 block text-sm font-bold text-foreground">Cookie session planned</strong>
					</div>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Team Access</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each members as member}
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<div>
							<strong class="block text-sm">{member.name}</strong>
							<span class="mt-1 block text-xs font-bold text-muted-foreground">{member.access}</span>
						</div>
						<Badge variant="secondary">{member.role}</Badge>
					</div>
				{/each}
			</CardContent>
		</Card>
	</div>
</AppShell>