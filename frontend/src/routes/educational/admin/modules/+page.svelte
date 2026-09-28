<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { educationalModules as seedModules } from '$lib/data/trade';
	import { listEducationalModules, publishEducationalModule, createEducationalModule, deleteEducationalModule, updateEducationalModule } from '$lib/api/educational';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import Pagination from '$lib/components/Pagination.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';
	import { page } from '$app/state';
	import { syncFiltersToUrl } from '$lib/utils/urlFilters';

	let modules = createRemoteList(listEducationalModules, seedModules);
	let publishing = $state('');
	let deleting = $state('');
	let error = $state('');
	let newTitle = $state('');
	let creating = $state(false);
	let query = $state(page.url.searchParams.get('query') ?? '');
	let statusFilter = $state(page.url.searchParams.get('status') ?? 'All');
	const statusFilters = ['All', 'Published', 'Draft'];
	const confirm = createConfirmController();

	let filteredModules = $derived(
		modules.items.filter(
			(module) =>
				(statusFilter === 'All' || module.status === statusFilter) &&
				[module.title, module.level, module.summary].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);

	// Simpan pencarian & filter ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: statusFilter === 'All' ? '' : statusFilter };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '' }, ['query', 'status']), 250);
		return () => clearTimeout(syncTimer);
	});

	$effect(() => {
		modules.load();
	});

	async function publishModule(id: string) {
		error = '';
		publishing = id;
		try {
			const res = await publishEducationalModule(id);
			if (res.data) {
				modules.upsert(res.data);
			} else {
				const module = modules.items.find((item) => item.id === id);
				if (module) modules.upsert({ ...module, status: 'Published' });
			}
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
			const res = await createEducationalModule({ title: newTitle, description: '', order_index: modules.items.length + 1 });
			if (res.data) {
				modules.upsert(res.data);
			} else {
				await modules.load();
			}
			newTitle = '';
		} catch {
			error = t('Gagal membuat modul.');
		} finally {
			creating = false;
		}
	}

	async function removeModule(id: string) {
		error = '';
		deleting = id;
		try {
			await deleteEducationalModule(id);
			modules.remove(id);
		} catch {
			error = t('Gagal menghapus modul.');
		} finally {
			deleting = '';
		}
	}

	async function moveModule(id: string, dir: -1 | 1) {
		// Cari indeks pada daftar sumber (bukan daftar terfilter) agar urutan tetap benar.
		const index = modules.items.findIndex((m) => m.id === id);
		if (index < 0) return;
		const target = index + dir;
		if (target < 0 || target >= modules.items.length) return;
		const a = modules.items[index];
		const b = modules.items[target];
		const aOrder = a.orderIndex ?? index;
		const bOrder = b.orderIndex ?? target;
		try {
			const resA = await updateEducationalModule(a.id, { title: a.title, description: a.description ?? '', order_index: bOrder });
			const resB = await updateEducationalModule(b.id, { title: b.title, description: b.description ?? '', order_index: aOrder });
			if (resA.data) modules.upsert(resA.data);
			if (resB.data) modules.upsert(resB.data);
			if (!resA.data || !resB.data) {
				await modules.load();
			}
		} catch {
			error = t('Gagal mengubah urutan modul.');
		}
	}

	let paginationPage_modules = $state(1);
	let paginationPageSize_modules = $state(5);
	let pagedItems_modules = $derived(paginate(filteredModules ?? [], paginationPage_modules, paginationPageSize_modules));
	let paginationTotalPages_modules = $derived(calcTotalPages(filteredModules?.length ?? 0, paginationPageSize_modules));

	// Reset ke halaman pertama saat pencarian/filter berubah.
	$effect(() => {
		query;
		statusFilter;
		paginationPage_modules = 1;
	});

</script>

<svelte:head>
	<title>{t('Modul Admin')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Educational Admin')} eyebrow={t('Manage modules')}>
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
			<Badge variant="secondary">{filteredModules.length} {t('total')}</Badge>
		</CardHeader>
		<CardContent class="flex flex-wrap items-center justify-between gap-3">
			<form class="flex flex-1 gap-2" onsubmit={(event) => { event.preventDefault(); createModule(); }}>
				<Input placeholder={t('Judul modul baru...')} aria-label={t('Judul modul baru')} bind:value={newTitle} class="flex-1" />
				<Button type="submit" disabled={creating}>{creating ? t('Membuat...') : t('Buat modul')}</Button>
			</form>
		</CardContent>
		<CardContent class="flex flex-wrap items-center justify-between gap-3">
			<div class="flex flex-wrap gap-2">
				{#each statusFilters as filter}
					<Button variant={statusFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (statusFilter = filter)}>{filter === 'All' ? t('Semua') : label(filter)}</Button>
				{/each}
			</div>
			<Input bind:value={query} type="search" aria-label={t('Cari modul...')} placeholder={t('Cari modul...')} class="w-[min(300px,100%)]" />
		</CardContent>
		<CardContent class="grid gap-3">
			{#if modules.loading}
				{#each Array(4) as _}
					<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<div class="grid gap-2">
							<Skeleton class="h-4 w-48" />
							<Skeleton class="h-3 w-40" />
						</div>
						<Skeleton class="h-8 w-24" />
					</div>
				{/each}
			{:else}
			{#each pagedItems_modules as module (module.id)}
				{@const srcIndex = modules.items.findIndex((m) => m.id === module.id)}
				<div class="flex items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
					<div class="min-w-0">
						<strong class="block text-sm font-bold">{module.title}</strong>
						<span class="mt-1 block text-xs font-semibold text-muted-foreground">{module.level} - {module.lessons} {t('pelajaran')} - {module.completion}% {t('selesai')} · {t('urutan')} {srcIndex + 1}</span>
					</div>
					<div class="grid justify-items-end gap-2">
						<Badge variant={toneVariant(statusTone(module.status))}>{label(module.status)}</Badge>
						<div class="flex flex-wrap justify-end gap-2">
							<Button size="sm" variant="outline" disabled={srcIndex <= 0} aria-label={t('Naikkan urutan')} onclick={() => moveModule(module.id, -1)}>↑</Button>
							<Button size="sm" variant="outline" disabled={srcIndex < 0 || srcIndex >= modules.items.length - 1} aria-label={t('Turunkan urutan')} onclick={() => moveModule(module.id, 1)}>↓</Button>
							<Button size="sm" variant="outline" href={`/educational/modules/${module.id}`}>{t('Detail')}</Button>
							<Button size="sm" variant={module.status === 'Published' ? 'outline' : 'default'} disabled={module.status === 'Published' || publishing === module.id} onclick={() => publishModule(module.id)}>{publishing === module.id ? t('Mempublikasikan...') : t('Publikasikan')}</Button>
							<Button
								size="sm"
								variant="destructive"
								disabled={deleting === module.id}
								onclick={() =>
									confirm.ask({
										title: t('Hapus modul'),
										description: t('Modul ini akan dihapus permanen dari workspace.'),
										detail: module.title,
										action: () => removeModule(module.id)
									})}
							>
								{deleting === module.id ? '...' : t('Hapus')}
							</Button>
						</div>
					</div>
				</div>
			{:else}
				<p class="text-sm text-muted-foreground">{t('Belum ada data.')}</p>
			{/each}
			{/if}
		</CardContent>
	</Card>
{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{error}</p>{/if}
	<Pagination bind:page={paginationPage_modules} bind:pageSize={paginationPageSize_modules} totalPages={paginationTotalPages_modules} totalItems={filteredModules?.length ?? 0} />

	<ConfirmDialog
		bind:open={confirm.open}
		title={confirm.title}
		description={confirm.description}
		detail={confirm.detail}
		confirmLabel={confirm.label}
		loading={confirm.loading}
		onconfirm={confirm.run}
	/>
</AppShell>