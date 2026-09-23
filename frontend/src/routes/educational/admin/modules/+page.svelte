<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalModules, publishEducationalModule, createEducationalModule, deleteEducationalModule } from '$lib/api/educational';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	let modules = createRemoteList(listEducationalModules, seedModules);
	let publishing = $state('');
	let deleting = $state('');
	let error = $state('');
	let newTitle = $state('');
	let creating = $state(false);

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

	async function createModule() {
		error = '';
		if (newTitle.trim().length < 3) {
			error = 'Judul modul minimal 3 karakter.';
			return;
		}
		creating = true;
		try {
			const created = (await createEducationalModule({ title: newTitle, description: '', order_index: modules.items.length + 1 })).data;
			modules.items.unshift(created);
			newTitle = '';
		} catch {
			error = 'Gagal membuat modul.';
		} finally {
			creating = false;
		}
	}

	async function removeModule(id: string) {
		if (!confirm('Hapus modul ini beserta artikelnya?')) return;
		error = '';
		deleting = id;
		try {
			await deleteEducationalModule(id);
			const idx = modules.items.findIndex((m) => m.id === id);
			if (idx >= 0) modules.items.splice(idx, 1);
		} catch {
			error = 'Gagal menghapus modul.';
		} finally {
			deleting = '';
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
		<CardContent class="grid gap-3">
			<form class="flex gap-2" onsubmit={(event) => { event.preventDefault(); createModule(); }}>
				<Input placeholder="Judul modul baru..." bind:value={newTitle} class="flex-1" />
				<Button type="submit" disabled={creating}>{creating ? 'Membuat...' : 'Buat modul'}</Button>
			</form>
			{#each modules.items as module}
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<div>
						<strong class="block text-sm font-bold">{module.title}</strong>
						<span class="mt-1 block text-xs font-semibold text-muted-foreground">{module.level} - {module.lessons} lessons - {module.completion}% complete</span>
					</div>
					<div class="grid justify-items-end gap-2">
						<Badge variant={toneVariant(statusTone(module.status))}>{module.status}</Badge>
						<div class="flex gap-2">
							<Button size="sm" variant="outline" href={`/educational/modules/${module.id}`}>Detail</Button>
							<Button size="sm" variant={module.status === 'Published' ? 'outline' : 'default'} disabled={module.status === 'Published' || publishing === module.id} onclick={() => publishModule(module.id)}>{publishing === module.id ? 'Publishing...' : 'Publish'}</Button>
							<Button size="sm" variant="destructive" disabled={deleting === module.id} onclick={() => removeModule(module.id)}>{deleting === module.id ? '...' : 'Hapus'}</Button>
						</div>
					</div>
				</div>
			{/each}
		</CardContent>
	</Card>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
</AppShell>