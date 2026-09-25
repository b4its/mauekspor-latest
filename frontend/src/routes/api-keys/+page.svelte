<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { apiKeys as seedApiKeys } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { listApiKeys, createApiKey, revokeApiKey, deleteApiKey } from '$lib/api/api-keys';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';

	import KeyIcon from '@lucide/svelte/icons/key';
	import PlusIcon from '@lucide/svelte/icons/plus';
	import CopyIcon from '@lucide/svelte/icons/copy';
	import CheckIcon from '@lucide/svelte/icons/check';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import BanIcon from '@lucide/svelte/icons/ban';
	import XIcon from '@lucide/svelte/icons/x';

	const filters = ['All', 'Active', 'Expiring Soon', 'Revoked'];
	const availableScopes = [
		{ id: 'catalogs:read', label: 'catalogs:read' },
		{ id: 'quotations:read', label: 'quotations:read' },
		{ id: 'orders:read', label: 'orders:read' },
		{ id: 'orders:write', label: 'orders:write' },
		{ id: 'shipments:read', label: 'shipments:read' },
		{ id: 'analytics:read', label: 'analytics:read' }
	];

	let activeFilter = $state('All');
	let query = $state('');
	let showCreateModal = $state(false);
	let newKeyName = $state('');
	let selectedScopes = $state<string[]>(['catalogs:read', 'quotations:read']);
	let creating = $state(false);
	let revokingId = $state('');
	let deletingId = $state('');
	let copiedId = $state('');
	let message = $state('');
	let error = $state('');

	let keys = createRemoteList(listApiKeys, seedApiKeys);
	let filteredKeys = $derived(
		keys.items.filter(
			(key) =>
				(activeFilter === 'All' || key.status === activeFilter) &&
				[key.name, key.prefix, key.status, key.owner, ...(key.scopes ?? [])].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let activeCount = $derived(keys.items.filter((key) => key.status === 'Active').length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		keys.load();
	});

	function toggleScope(scope: string) {
		if (selectedScopes.includes(scope)) {
			selectedScopes = selectedScopes.filter((s) => s !== scope);
		} else {
			selectedScopes = [...selectedScopes, scope];
		}
	}

	function openCreateModal() {
		newKeyName = `API Key ${keys.items.length + 1}`;
		selectedScopes = ['catalogs:read', 'quotations:read'];
		error = '';
		showCreateModal = true;
	}

	async function handleCreate() {
		error = '';
		if (!newKeyName.trim()) {
			error = t('Nama API key wajib diisi.');
			return;
		}
		if (selectedScopes.length === 0) {
			error = t('Pilih minimal satu lingkup akses (scope).');
			return;
		}
		creating = true;
		try {
			const res = await createApiKey(newKeyName.trim(), selectedScopes);
			if (res.data) {
				keys.upsert(res.data);
			} else {
				await keys.load();
			}
			message = `${t('API key created.')} (Prefix: ${res.data?.prefix || 'mek_live_'})`;
			showCreateModal = false;
		} catch {
			error = t('Gagal membuat API key.');
		} finally {
			creating = false;
		}
	}

	async function handleRevoke(id: string) {
		error = '';
		revokingId = id;
		try {
			const res = await revokeApiKey(id);
			if (res.data) {
				keys.upsert(res.data);
			} else {
				const target = keys.items.find((k) => k.id === id);
				if (target) keys.upsert({ ...target, status: 'Revoked' });
			}
			message = t('Kunci API berhasil dicabut (Revoked).');
		} catch {
			error = t('Gagal mencabut API key.');
		} finally {
			revokingId = '';
		}
	}

	async function handleDelete(id: string) {
		if (!confirm(t('Hapus Kunci API ini?'))) return;
		error = '';
		deletingId = id;
		try {
			await deleteApiKey(id);
			keys.remove(id);
			message = t('Kunci API dihapus.');
		} catch {
			error = t('Gagal menghapus API key.');
		} finally {
			deletingId = '';
		}
	}

	async function copyToClipboard(id: string, text: string) {
		try {
			await navigator.clipboard.writeText(text);
			copiedId = id;
			setTimeout(() => {
				if (copiedId === id) copiedId = '';
			}, 2000);
		} catch {
			// Fallback silent
		}
	}

	let paginationPage = $state(1);
	let paginationPageSize = $state(6);
	let pagedItems = $derived(paginate(filteredKeys ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredKeys?.length ?? 0, paginationPageSize));
</script>

<svelte:head>
	<title>{t('Kunci API')} | MauEkspor</title>
</svelte:head>

<AppShell title="API Keys" eyebrow={t('Developer access controls')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline" class="gap-1 border-primary/30 bg-primary/10 text-primary">
				<KeyIcon class="size-3.5" />
				{t('Akses developer')}
			</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Manage API credentials for logistics, finance, and reporting integrations.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Create scoped API keys, monitor usage, and revoke old credentials before they become integration or security risks.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={openCreateModal} class="gap-1.5 shadow-md">
				<PlusIcon class="size-4" />
				{t('Create API key')}
			</Button>
			<Badge variant="secondary" class="px-3 py-1 text-sm font-semibold">
				{t('Active')} ({activeCount})
			</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if message}
		<div class="flex items-center justify-between rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
			<span>{message}</span>
			<button onclick={() => (message = '')} class="text-muted-foreground hover:text-foreground">
				<XIcon class="size-4" />
			</button>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search key, scope, owner...')} class="w-[min(390px,100%)]" />
	</div>

	{#if keys.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="p-5">
					<div class="flex items-center justify-between gap-3">
						<Skeleton class="h-5 w-20" />
						<Skeleton class="h-5 w-24 font-mono" />
					</div>
					<Skeleton class="mt-4 h-6 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<div class="mt-4 grid grid-cols-2 gap-2">
						<Skeleton class="h-14 w-full rounded-lg" />
						<Skeleton class="h-14 w-full rounded-lg" />
					</div>
					<div class="mt-3 flex flex-wrap gap-2">
						<Skeleton class="h-5 w-16 rounded-full" />
						<Skeleton class="h-5 w-20 rounded-full" />
					</div>
					<Skeleton class="mt-4 h-9 w-full rounded-lg" />
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each pagedItems as key (key.id)}
				<Card class="flex flex-col justify-between gap-4 p-5 transition-shadow hover:shadow-md">
					<div>
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(key.status))}>{key.status}</Badge>
							<div class="flex items-center gap-1.5">
								<code class="rounded bg-muted px-2 py-0.5 font-mono text-xs font-semibold text-muted-foreground">{key.prefix}...</code>
								<Button
									size="icon"
									variant="ghost"
									class="size-7"
									title={t('Salin')}
									onclick={() => copyToClipboard(key.id, `${key.prefix}live_secret_token`)}
								>
									{#if copiedId === key.id}
										<CheckIcon class="size-3.5 text-emerald-600" />
									{:else}
										<CopyIcon class="size-3.5 text-muted-foreground" />
									{/if}
								</Button>
							</div>
						</div>

						<CardHeader class="p-0 mt-3">
							<CardTitle class="text-xl font-bold tracking-tight text-foreground">{key.name}</CardTitle>
							<CardDescription>{key.owner} · {t('Last used')} {key.lastUsed}</CardDescription>
						</CardHeader>

						<CardContent class="grid gap-3 p-0 mt-3">
							<div class="grid grid-cols-2 gap-2">
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Created')} <strong class="mt-1 block text-sm font-bold text-foreground">{key.createdAt}</strong>
								</div>
								<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
									{t('Scopes')} <strong class="mt-1 block text-sm font-bold text-foreground">{key.scopes?.length ?? 0}</strong>
								</div>
							</div>
							<div class="flex flex-wrap gap-1.5 pt-1">
								{#each key.scopes ?? [] as scope}
									<span class="rounded-md border border-primary/20 bg-primary/5 px-2 py-0.5 text-xs font-medium text-primary">{scope}</span>
								{/each}
							</div>
						</CardContent>
					</div>

					<div class="flex items-center justify-end gap-2 border-t pt-3">
						{#if key.status === 'Active'}
							<Button
								variant="outline"
								size="sm"
								class="gap-1 border-destructive/30 text-destructive hover:bg-destructive/10"
								onclick={() => handleRevoke(key.id)}
								disabled={revokingId === key.id}
							>
								<BanIcon class="size-3.5" />
								{revokingId === key.id ? t('Revoking...') : t('Revoke')}
							</Button>
						{:else}
							<Button
								variant="ghost"
								size="sm"
								class="gap-1 text-destructive hover:bg-destructive/10"
								onclick={() => handleDelete(key.id)}
								disabled={deletingId === key.id}
							>
								<Trash2Icon class="size-3.5" />
								{deletingId === key.id ? t('Menghapus...') : t('Hapus Kunci')}
							</Button>
						{/if}
					</div>
				</Card>
			{:else}
				<div class="col-span-full rounded-xl border border-dashed p-8 text-center font-semibold text-muted-foreground">
					{t('No API key matched your search.')}
				</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredKeys?.length ?? 0} />

	<!-- Create API Key Modal Dialog -->
	{#if showCreateModal}
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
			<div class="w-full max-w-lg rounded-2xl border bg-card p-6 shadow-2xl space-y-5">
				<div class="flex items-center justify-between border-b pb-3">
					<div class="flex items-center gap-2">
						<KeyIcon class="size-5 text-primary" />
						<h3 class="text-xl font-bold">{t('Kunci API Baru')}</h3>
					</div>
					<Button variant="ghost" size="icon" onclick={() => (showCreateModal = false)}>
						<XIcon class="size-4" />
					</Button>
				</div>

				<div class="space-y-4">
					<div class="space-y-1.5">
						<label for="new-key-name" class="text-sm font-semibold">{t('Nama Kunci API')}</label>
						<Input id="new-key-name" bind:value={newKeyName} placeholder="cth. Logistics Gateway Token" />
					</div>

					<div class="space-y-2">
						<span class="text-sm font-semibold block">{t('Pilih Lingkup Akses (Scopes)')}</span>
						<div class="grid grid-cols-2 gap-2">
							{#each availableScopes as sc}
								<label class="flex cursor-pointer items-center gap-2 rounded-lg border p-2.5 text-xs font-medium hover:bg-muted/50 {selectedScopes.includes(sc.id) ? 'border-primary bg-primary/5 text-primary font-bold' : ''}">
									<input
										type="checkbox"
										class="size-4 rounded"
										checked={selectedScopes.includes(sc.id)}
										onchange={() => toggleScope(sc.id)}
									/>
									{sc.label}
								</label>
							{/each}
						</div>
					</div>
				</div>

				<div class="flex justify-end gap-2 border-t pt-4">
					<Button variant="outline" onclick={() => (showCreateModal = false)}>{t('Batal')}</Button>
					<Button onclick={handleCreate} disabled={creating} class="gap-1.5">
						{creating ? t('Creating...') : t('Simpan & Buat')}
					</Button>
				</div>
			</div>
		</div>
	{/if}
</AppShell>