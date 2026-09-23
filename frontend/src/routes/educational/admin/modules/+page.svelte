<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalModules, publishEducationalModule } from '$lib/api/educational';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	let modules = createRemoteList(listEducationalModules, seedModules);
	let publishing = $state('');
	let error = $state('');

	$effect(() => {
		modules.load();
	});

	async function publishModule(id: string) {
		error = '';
		publishing = id;
		try {
			await publishEducationalModule(id);
			const module = modules.items.find((item) => item.id === id);
			if (module) module.status = 'Published';
		} catch {
			error = 'Gagal mempublikasikan modul.';
		} finally {
			publishing = '';
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>Admin Modules | MauEkspor</title>
</svelte:head>

<AppShell title="Educational Admin" eyebrow="Manage modules">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="outline">Admin</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Review and publish learning modules.
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					Each module maps to a workflow in the workspace and is published after content review.
				</CardDescription>
			</div>
			<Button variant="outline" href="/educational/admin">Admin home</Button>
		</div>
	</Card>

	<Card class="mt-4">
		<CardHeader class="flex-row items-center justify-between gap-3">
			<CardTitle>Modules</CardTitle>
			<Badge variant="secondary">{modules.items.length} total</Badge>
		</CardHeader>
		<CardContent class="grid gap-2">
			{#each modules.items as module}
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<div>
						<strong class="block text-sm font-bold">{module.title}</strong>
						<span class="mt-1 block text-xs font-semibold text-muted-foreground">{module.level} - {module.lessons} lessons - {module.completion}% complete</span>
					</div>
					<div class="grid justify-items-end gap-2">
						<Badge variant={toneVariant(statusTone(module.status))}>{module.status}</Badge>
						<Button size="sm" variant={module.status === 'Published' ? 'outline' : 'default'} disabled={module.status === 'Published' || publishing === module.id} onclick={() => publishModule(module.id)}>{publishing === module.id ? 'Publishing...' : 'Publish'}</Button>
					</div>
				</div>
			{/each}
		</CardContent>
	</Card>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
</AppShell>