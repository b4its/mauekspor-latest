<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { userAccounts as seedUsers } from '$lib/data/trade';
	import { listUsers, deleteUser } from '$lib/api/users';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import type { UserAccount } from '$lib/data/trade';

	const roleFilters = ['All', 'Admin', 'UMKM', 'Buyer', 'Forwarder'];
	const PAGE_SIZE = 8;
	let roleFilter = $state('All');
	let query = $state('');
	let deleting = $state('');
	let error = $state('');
	let users = $state<UserAccount[]>(seedUsers);
	let loading = $state(true);
	let total = $state(seedUsers.length);
	let page = $state(1);

	async function loadUsers() {
		loading = true;
		try {
			const res = await listUsers({
				search: query || undefined,
				role: roleFilter === 'All' ? undefined : roleFilter,
				limit: PAGE_SIZE,
				offset: (page - 1) * PAGE_SIZE
			});
			users = res.data;
			total = Number(res.meta?.total ?? res.data.length);
		} catch {
			users = seedUsers;
			total = seedUsers.length;
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		loadUsers();
	});

	const totalPages = $derived(Math.max(1, Math.ceil(total / PAGE_SIZE)));

	async function removeUser(id: string, name: string) {
		if (!confirm(`${t('Hapus akun "')}${name}" ${t('beserta data terkaitnya?')}`)) return;
		error = '';
		deleting = id;
		try {
			await deleteUser(id);
			await loadUsers();
		} catch {
			error = t('Gagal menghapus akun.');
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
	<title>Users | MauEkspor</title>
</svelte:head>

<AppShell title="Users" eyebrow={t('Account management')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">{t('Admin only')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{t('Manage the accounts in your export workspace.')}
				</CardTitle>
				<CardDescription class="mt-2 max-w-xl leading-relaxed">
					{t('Filter by role, search by email or full name, and open a user to inspect account detail.')}
				</CardDescription>
			</div>
			<Card>
				<CardContent class="p-5">
				<div class="grid gap-2.5 md:min-w-[200px]">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Total users')}</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{total}</strong>
				</div>
				</CardContent>
			</Card>
		</div>
	</Card>

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each roleFilters as filter}
				<Button
					variant={roleFilter === filter ? 'default' : 'outline'}
					size="sm"
					onclick={() => {
						roleFilter = filter;
						page = 1;
					}}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input
			bind:value={query}
			type="search"
			placeholder={t('Search email or name...')}
			class="max-w-xs"
			oninput={() => (page = 1)}
		/>
	</div>

	<Card class="p-2">
		<div class="grid grid-cols-2 gap-1 p-3 text-xs font-bold text-muted-foreground md:grid-cols-4 lg:grid-cols-5">
			<span>{t('User')}</span><span>{t('Role')}</span><span>{t('Status')}</span><span>{t('Created')}</span><span class="hidden lg:block"></span>
		</div>
		{#if loading}
			<div class="p-6 text-center font-semibold text-muted-foreground">{t('Memuat...')}</div>
		{:else}
			{#each users as user}
				<div class="grid grid-cols-2 items-center gap-3 rounded-lg border-b p-3 text-sm transition-colors last:border-b-0 hover:bg-muted/40 md:grid-cols-4 lg:grid-cols-5">
					<a href={`/users/${user.id}`} class="grid min-w-0 gap-1">
						<strong class="block truncate">{user.fullName}</strong>
						<small class="block truncate text-xs text-muted-foreground">{user.email}</small>
					</a>
					<span><Badge variant="secondary">{user.role}</Badge></span>
					<span><Badge variant={toneVariant(statusTone(user.status))}>{user.status}</Badge></span>
					<span class="hidden text-muted-foreground md:block">{user.createdAt}</span>
					<span class="grid justify-end">
						<Button size="sm" variant="ghost" href={`/users/${user.id}`}>Open</Button>
						<Button size="sm" variant="destructive" disabled={deleting === user.id || user.role === 'Admin'} onclick={() => removeUser(user.id, user.fullName)}>
							{deleting === user.id ? '...' : t('Hapus')}
						</Button>
					</span>
				</div>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No user matched your filter.')}</div>
			{/each}
		{/if}
		{#if error}
			<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}
		{#if totalPages > 1}
			<div class="flex items-center justify-between gap-3 border-t p-3">
				<span class="text-xs font-semibold text-muted-foreground">Halaman {page} dari {totalPages} · {total} pengguna</span>
				<div class="flex gap-2">
					<Button size="sm" variant="outline" disabled={page <= 1} onclick={() => (page -= 1)}>{t('Sebelumnya')}</Button>
					<Button size="sm" variant="outline" disabled={page >= totalPages} onclick={() => (page += 1)}>{t('Berikutnya')}</Button>
				</div>
			</div>
		{/if}
	</Card>
</AppShell>