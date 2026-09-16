<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalModules, publishEducationalModule, createEducationalModule, deleteEducationalModule, updateEducationalModule } from '$lib/api/educational';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

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
			error = t('Gagal mempublikasikan modul.');
		} finally {
			publishing = '';
		}
	}

	async function createModule() {
		error = '';
		if (newTitle.trim().length < 3) {
			error = t('Judul modul minimal 3 karakter.');
			return;
		}
		creating = true;
		try {
			const created = (await createEducationalModule({ title: newTitle, description: '', order_index: modules.items.length + 1 })).data;
			modules.items.unshift(created);
			newTitle = '';
		} catch {
			error = t('Gagal membuat modul.');
		} finally {
			creating = false;
		}
	}

	async function removeModule(id: string) {
		if (!confirm(t('Hapus modul ini beserta artikelnya?'))) return;
		error = '';
		deleting = id;
		try {
			await deleteEducationalModule(id);
			const idx = modules.items.findIndex((m) => m.id === id);
			if (idx >= 0) modules.items.splice(idx, 1);
		} catch {
			error = t('Gagal menghapus modul.');
		} finally {
			deleting = '';
		}
	}

	async function moveModule(index: number, dir: -1 | 1) {
		const target = index + dir;
		if (target < 0 || target >= modules.items.length) return;
		const a = modules.items[index];
		const b = modules.items[target];
		const aOrder = a.orderIndex ?? index;
		const bOrder = b.orderIndex ?? target;
		try {
			await updateEducationalModule(a.id, { title: a.title, description: a.description ?? '', order_index: bOrder });
			await updateEducationalModule(b.id, { title: b.title, description: b.description ?? '', order_index: aOrder });
			// Tukar posisi dalam array secara in-place (items adalah getter read-only)
			const arr = modules.items;
			[arr[index], arr[target]] = [arr[target], arr[index]];
			arr[index].orderIndex = bOrder;
			arr[target].orderIndex = aOrder;
		} catch {
			error = t('Gagal mengubah urutan modul.');
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
	<title>{t('Modul Admin')} | MauEkspor</title>
</svelte:head>

<AppShell title="Educational Admin" eyebrow={t('Manage modules')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="outline">{t('Admin')}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{t('Review and publish learning modules.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-2xl">
					{t('Setiap modul memetakan alur kerja di workspace dan dipublikasikan setelah tinjauan konten.')}
				</CardDescription>
			</div>
			<Button variant="outline" href="/educational/admin">{t('Beranda admin')}</Button>
		</div>
	</Card>

	<Card class="mt-4">
		<CardHeader class="flex-row items-center justify-between gap-3">
			<CardTitle>{t('Modul')}</CardTitle>
			<Badge variant="secondary">{modules.items.length} {t('total')}</Badge>
		</CardHeader>
		<CardContent class="grid gap-3">
			<form class="flex gap-2" onsubmit={(event) => { event.preventDefault(); createModule(); }}>
				<Input placeholder={t('Judul modul baru...')} bind:value={newTitle} class="flex-1" />
				<Button type="submit" disabled={creating}>{creating ? t('Membuat...') : t('Buat modul')}</Button>
			</form>
			{#each modules.items as module, index (module.id)}
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<div class="min-w-0">
						<strong class="block text-sm font-bold">{module.title}</strong>
						<span class="mt-1 block text-xs font-semibold text-muted-foreground">{module.level} - {module.lessons} {t('pelajaran')} - {module.completion}% {t('selesai')} · {t('urutan')} {index + 1}</span>
					</div>
					<div class="grid justify-items-end gap-2">
						<Badge variant={toneVariant(statusTone(module.status))}>{module.status}</Badge>
						<div class="flex flex-wrap justify-end gap-2">
							<Button size="sm" variant="outline" disabled={index === 0} onclick={() => moveModule(index, -1)}>↑</Button>
							<Button size="sm" variant="outline" disabled={index === modules.items.length - 1} onclick={() => moveModule(index, 1)}>↓</Button>
							<Button size="sm" variant="outline" href={`/educational/modules/${module.id}`}>{t('Detail')}</Button>
							<Button size="sm" variant={module.status === 'Published' ? 'outline' : 'default'} disabled={module.status === 'Published' || publishing === module.id} onclick={() => publishModule(module.id)}>{publishing === module.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
							<Button size="sm" variant="destructive" disabled={deleting === module.id} onclick={() => removeModule(module.id)}>{deleting === module.id ? '...' : t('Hapus')}</Button>
						</div>
					</div>
				</div>
			{/each}
		</CardContent>
	</Card>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
</AppShell>