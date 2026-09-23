<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { userAccounts as seedUsers } from '$lib/data/trade';
	import { listUsers, deleteUser } from '$lib/api/users';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';

	const roleFilters = ['All', 'Admin', 'UMKM', 'Buyer', 'Forwarder'];
	let roleFilter = $state('All');
	let query = $state('');
	let deleting = $state('');
	let error = $state('');

	let users = createRemoteList(listUsers, seedUsers);
	$effect(() => {
		users.load();
	});

	let filteredUsers = $derived(
		users.items.filter((user) => {
			const matchesRole = roleFilter === 'All' || user.role === roleFilter;
			const matchesQuery = [user.email, user.fullName, user.role, user.status]
				.join(' ')
				.toLowerCase()
				.includes(query.trim().toLowerCase());
			return matchesRole && matchesQuery;
		})
	);

	async function removeUser(id: string, name: string) {
		if (!confirm(`Hapus akun "${name}" beserta data terkaitnya?`)) return;
		error = '';
		deleting = id;
		try {
			await deleteUser(id);
			const idx = users.items.findIndex((u) => u.id === id);
			if (idx >= 0) users.items.splice(idx, 1);
		} catch {
			error = 'Gagal menghapus akun.';
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

<AppShell title="Users" eyebrow="Account management">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant="secondary">Admin only</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					Manage the accounts in your export workspace.
				</CardTitle>
				<CardDescription class="mt-2 max-w-xl leading-relaxed">
					Filter by role, search by email or full name, and open a user to inspect account detail.
				</CardDescription>
			</div>
			<Card>
				<CardContent class="p-5">
					<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Total users</span>
					<strong class="mt-2 block text-3xl font-bold tracking-tight">{users.items.length}</strong>
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
					onclick={() => (roleFilter = filter)}
				>
					{filter}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder="Search email or name..." class="max-w-xs" />
	</div>

	<Card class="p-2">
		<div class="grid grid-cols-2 gap-1 p-3 text-xs font-bold text-muted-foreground md:grid-cols-4 lg:grid-cols-5">
			<span>User</span><span>Role</span><span>Status</span><span>Created</span><span class="hidden lg:block"></span>
		</div>
		{#each filteredUsers as user}
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
						{deleting === user.id ? '...' : 'Hapus'}
					</Button>
				</span>
			</div>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">No user matched your filter.</div>
		{/each}
		{#if error}
			<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}
	</Card>
</AppShell>