<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';

	let { data } = $props();

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.user.fullName} | MauEkspor</title>
</svelte:head>

<AppShell title={data.user.id} eyebrow="User detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.user.status))}>{data.user.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.user.fullName}
				</CardTitle>
				<CardDescription class="mt-2">{data.user.email}</CardDescription>
			</div>
			<Badge variant="secondary">{data.user.role}</Badge>
		</div>
	</Card>

	<Card>
		<CardHeader><CardTitle>Account details</CardTitle></CardHeader>
		<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				Email <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.email}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				Role <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.role}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				Status <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.status}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				Created <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.createdAt}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				Last login <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.lastLogin}</strong>
			</div>
		</CardContent>
	</Card>

	<div class="mt-4">
		<Button variant="outline" href="/users">Back to users</Button>
	</div>
</AppShell>