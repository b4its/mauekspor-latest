<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Pagination from '$lib/components/Pagination.svelte';
	import {
		listAdminTables,
		listAdminRecords,
		createAdminRecord,
		updateAdminRecord,
		deleteAdminRecord,
		type AdminTable,
		type AdminRecord
	} from '$lib/api/admin';
	import { t } from '$lib/i18n.svelte';
	import { getStatus, getUser } from '$lib/stores/session.svelte';

	import SearchIcon from '@lucide/svelte/icons/search';
	import DatabaseIcon from '@lucide/svelte/icons/database';
	import PencilIcon from '@lucide/svelte/icons/pencil';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import PlusIcon from '@lucide/svelte/icons/plus';
	import ShieldAlertIcon from '@lucide/svelte/icons/shield-alert';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';
	import XIcon from '@lucide/svelte/icons/x';

	let tables = $state<AdminTable[]>([]);
	let tablesLoading = $state(true);
	let activeTable = $state('');
	let records = $state<AdminRecord[]>([]);
	let recordsLoading = $state(false);
	let total = $state(0);
	let search = $state('');
	let error = $state('');
	let page = $state(1);
	let pageSize = $state(20);

	// Edit/create modal
	let editOpen = $state(false);
	let editRecord = $state<AdminRecord | null>(null);
	let editJson = $state('');
	let editError = $state('');
	let isNew = $state(false);

	// Delete modal
	let deleteOpen = $state(false);
	let deleteTarget = $state<AdminRecord | null>(null);

	let totalPages = $derived(Math.max(1, Math.ceil(total / pageSize)));
	let isAdmin = $derived(getStatus() === 'authenticated' && getUser()?.role === 'Admin');

	async function loadTables() {
		tablesLoading = true;
		try {
			const res = await listAdminTables();
			tables = res.data;
			if (!activeTable && tables.length) activeTable = tables[0].name;
		} catch {
			error = t('Gagal memuat daftar tabel.');
		} finally {
			tablesLoading = false;
		}
	}

	async function loadRecords() {
		if (!activeTable) return;
		recordsLoading = true;
		try {
			const res = await listAdminRecords(activeTable, {
				search: search || undefined,
				limit: pageSize,
				offset: (page - 1) * pageSize
			});
			records = res.data;
			total = Number(res.meta?.total ?? res.data.length);
		} catch {
			error = t('Gagal memuat data tabel.');
			records = [];
		} finally {
			recordsLoading = false;
		}
	}

	$effect(() => {
		loadTables();
	});

	$effect(() => {
		if (activeTable) loadRecords();
	});

	function selectTable(name: string) {
		activeTable = name;
		search = '';
		page = 1;
	}

	function openEdit(record: AdminRecord) {
		isNew = false;
		editRecord = record;
		editJson = JSON.stringify(record, null, 2);
		editError = '';
		editOpen = true;
	}

	function openCreate() {
		isNew = true;
		editRecord = null;
		editJson = '{\n  \n}';
		editError = '';
		editOpen = true;
	}

	async function saveEdit() {
		editError = '';
		let payload: Record<string, unknown>;
		try {
			payload = JSON.parse(editJson);
		} catch {
			editError = t('JSON tidak valid.');
			return;
		}
		try {
			if (isNew) {
				await createAdminRecord(activeTable, payload);
			} else if (editRecord?.id) {
				await updateAdminRecord(activeTable, editRecord.id, payload);
			}
			editOpen = false;
			loadRecords();
			loadTables();
		} catch (e) {
			editError = e instanceof Error ? e.message : t('Gagal menyimpan.');
		}
	}

	function openDelete(record: AdminRecord) {
		deleteTarget = record;
		deleteOpen = true;
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		try {
			await deleteAdminRecord(activeTable, deleteTarget.id);
			deleteOpen = false;
			deleteTarget = null;
			loadRecords();
			loadTables();
		} catch {
			error = t('Gagal menghapus record.');
		}
	}

	// Keys of first record for column display
	let columns = $derived(records[0] ? Object.keys(records[0]).slice(0, 6) : []);

	function cellPreview(record: AdminRecord, key: string) {
		const v = record[key];
		if (v === null || v === undefined) return '—';
		if (typeof v === 'object') {
			try {
				const s = JSON.stringify(v);
				return s.length > 40 ? s.slice(0, 40) + '…' : s;
			} catch {
				return '[obj]';
			}
		}
		const s = String(v);
		return s.length > 40 ? s.slice(0, 40) + '…' : s;
	}
</script>

<svelte:head>
	<title>{t('Admin Panel')} | MauEkspor</title>
</svelte:head>

<AppShell title="Admin Panel" eyebrow={t('Manajemen data seluruh workspace')}>
	{#if !isAdmin}
		<div class="grid place-items-center gap-4 rounded-xl border border-destructive/30 bg-destructive/5 p-12 text-center">
			<ShieldAlertIcon class="size-12 text-destructive/60" />
			<div>
				<h2 class="text-xl font-bold">{t('Akses Ditolak')}</h2>
				<p class="mt-1 text-sm text-muted-foreground">{t('Halaman ini khusus Admin.')}</p>
			</div>
			<Button href="/dashboard" variant="outline">{t('Kembali ke Dashboard')}</Button>
		</div>
	{:else}
		<div class="grid gap-4 lg:grid-cols-[280px_1fr]">
			<!-- Table list -->
			<Card class="h-fit">
				<CardHeader class="p-4">
					<CardTitle class="flex items-center gap-2 text-base">
						<DatabaseIcon class="size-4" />
						{t('Tabel')} ({tables.length})
					</CardTitle>
				</CardHeader>
				<CardContent class="max-h-[70vh] overflow-y-auto p-2">
					{#if tablesLoading}
						<div class="space-y-1 p-2">
							{#each [1,2,3,4,5] as _}
								<div class="h-9 animate-pulse rounded-md bg-muted/50"></div>
							{/each}
						</div>
					{:else}
						{#each tables as table}
							<button
								onclick={() => selectTable(table.name)}
								class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent {activeTable === table.name ? 'bg-accent font-semibold' : ''}"
							>
								<span class="truncate">{table.name}</span>
								<Badge variant="outline" class="shrink-0">{table.count}</Badge>
							</button>
						{/each}
					{/if}
				</CardContent>
			</Card>

			<!-- Records -->
			<Card>
				<CardHeader class="flex-row flex-wrap items-center justify-between gap-3 p-4">
					<div>
						<CardTitle class="text-base">{activeTable || '—'}</CardTitle>
						<CardDescription>{total} {t('record')}</CardDescription>
					</div>
					<div class="flex flex-wrap items-center gap-2">
						<div class="flex items-center gap-2 rounded-md border bg-muted/30 px-2 py-1.5">
							<SearchIcon class="size-4 text-muted-foreground" />
							<input
								type="text"
								placeholder={t('Cari...')}
								bind:value={search}
								oninput={() => (page = 1)}
								class="w-32 bg-transparent text-sm outline-none sm:w-48"
							/>
							{#if search}
								<button onclick={() => { search = ''; page = 1; }} class="text-muted-foreground hover:text-foreground"><XIcon class="size-3.5" /></button>
							{/if}
						</div>
						<Button size="sm" onclick={openCreate}><PlusIcon class="size-4" /><span class="ms-1">{t('Buat')}</span></Button>
						<Button size="sm" variant="outline" onclick={loadRecords}><RefreshCwIcon class="size-4" /></Button>
					</div>
				</CardHeader>

				<CardContent class="p-4 pt-0">
					{#if error}
						<p class="mb-3 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}

					{#if recordsLoading}
						<div class="space-y-2">
							{#each [1,2,3,4,5] as _}
								<div class="h-12 animate-pulse rounded-lg bg-muted/40"></div>
							{/each}
						</div>
					{:else if records.length === 0}
						<p class="py-10 text-center text-sm text-muted-foreground">{t('Tidak ada record.')}</p>
					{:else}
						<!-- Table view -->
						<div class="overflow-x-auto">
							<table class="w-full text-sm">
								<thead>
									<tr class="border-b text-left text-xs uppercase tracking-wide text-muted-foreground">
										{#each columns as col}
											<th class="px-3 py-2 font-semibold">{col}</th>
										{/each}
										<th class="px-3 py-2 text-right font-semibold">{t('Aksi')}</th>
									</tr>
								</thead>
								<tbody>
									{#each records as record (record.id)}
										<tr class="border-b transition-colors hover:bg-accent/40">
											{#each columns as col}
												<td class="max-w-[180px] truncate px-3 py-2">{cellPreview(record, col)}</td>
											{/each}
											<td class="px-3 py-2">
												<div class="flex justify-end gap-1">
													<button onclick={() => openEdit(record)} class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground" title={t('Edit')}><PencilIcon class="size-3.5" /></button>
													<button onclick={() => openDelete(record)} class="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive" title={t('Hapus')}><Trash2Icon class="size-3.5" /></button>
												</div>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="mt-3">
							<Pagination bind:page={page} bind:pageSize={pageSize} totalPages={totalPages} totalItems={total} />
						</div>
					{/if}
				</CardContent>
			</Card>
		</div>
	{/if}
</AppShell>

<!-- Edit/Create Dialog -->
{#if editOpen}
	<Dialog.Root bind:open={editOpen}>
		<Dialog.Content class="max-h-[85vh] sm:max-w-2xl">
			<Dialog.Header>
				<Dialog.Title>{isNew ? t('Buat Record') : t('Edit Record')} — {activeTable}</Dialog.Title>
				<Dialog.Description>{isNew ? t('Isi data sebagai JSON.') : t('Edit data record sebagai JSON.')}</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-3 py-3">
				{#if editError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{editError}</p>
				{/if}
				<Textarea bind:value={editJson} rows={14} class="font-mono text-xs" spellcheck="false" />
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (editOpen = false)}>{t('Batal')}</Button>
				<Button onclick={saveEdit}>{t('Simpan')}</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Delete Dialog -->
{#if deleteOpen}
	<Dialog.Root bind:open={deleteOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Hapus record')}</Dialog.Title>
				<Dialog.Description>
					{t('Yakin hapus record')} <code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">{deleteTarget?.id}</code> {t('dari')} <strong>{activeTable}</strong>?
				</Dialog.Description>
			</Dialog.Header>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (deleteOpen = false)}>{t('Batal')}</Button>
				<Button variant="destructive" onclick={confirmDelete}>{t('Hapus')}</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}