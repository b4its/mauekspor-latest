<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { teamMembers as seedMembers } from '$lib/data/trade';
	import type { TeamMember } from '$lib/data/trade';
	import { listTeamMembers, inviteTeamMember, updateTeamMemberRole } from '$lib/api/team';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Admin', 'Operations', 'Compliance', 'Finance', 'Sales'];
	let activeFilter = $state('All');
	let query = $state('');
	let invited = $state(false);
	let error = $state('');
	let inviting = $state(false);

	let teamMembers = createRemoteList(listTeamMembers, seedMembers);
	$effect(() => {
		teamMembers.load();
	});

	let filteredMembers = $derived(
		teamMembers.items.filter(
			(member) =>
				(activeFilter === 'All' || member.role === activeFilter) &&
				[member.name, member.email, member.role, member.status, ...member.permissions].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let activeCount = $derived(teamMembers.items.filter((member) => member.status === 'Active').length);
	let avgWorkload = $derived(Math.round(teamMembers.items.reduce((sum, member) => sum + member.workload, 0) / (teamMembers.items.length || 1)));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleInvite() {
		error = '';
		inviting = true;
		try {
			await inviteTeamMember(`team+${Date.now()}@mauekspor.example`, 'Operations');
			invited = true;
		} catch {
			error = t('Gagal mengirim undangan.');
		} finally {
			inviting = false;
		}
	}

	let updatingRole = $state('');
	async function handleUpdateRole(member: TeamMember) {
		error = '';
		updatingRole = member.id;
		try {
			await updateTeamMemberRole(member.id, 'Compliance');
			invited = true;
		} catch {
			error = t('Gagal memperbarui peran.');
		} finally {
			updatingRole = '';
		}
	}
</script>

<svelte:head>
	<title>{t('Team')} | MauEkspor</title>
</svelte:head>

<AppShell title="Team" eyebrow={t('Roles and workspace access')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Access control')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Coordinate export operations with clear roles, permissions, and workload.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Manage team members across operations, compliance, finance, and sales while keeping access scoped to each trade workflow.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleInvite} disabled={inviting}>{invited ? t('Invite sent') : inviting ? t('Inviting...') : t('Invite member')}</Button>
			<Badge>{t('Active')} {activeCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if teamMembers.error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{teamMembers.error}</p>
	{/if}

	{#if invited}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Team invitation sent.')}</strong>
			<span class="block text-sm text-muted-foreground">
				{t('Undangan terkirim melalui backend.')}</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Search member, role, permission...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Members')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{teamMembers.items.length}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Active')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{activeCount}</strong>
			</CardContent>
		</Card>
		<Card>
			<CardContent class="p-5">
				<span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Avg workload')}</span>
				<strong class="mt-2 block text-3xl font-bold tracking-tight">{avgWorkload}%</strong>
			</CardContent>
		</Card>
	</div>

	{#if teamMembers.loading}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<Card class="grid gap-4">
					<CardContent class="grid gap-4 p-5">
						<div class="flex items-center justify-between gap-3">
							<Skeleton class="h-5 w-20" />
							<Skeleton class="h-5 w-16 rounded-full" />
						</div>
						<Skeleton class="h-7 w-3/4" />
						<Skeleton class="h-4 w-1/2" />
						<div class="grid grid-cols-2 gap-2">
							<Skeleton class="h-14 w-full rounded-lg" />
							<Skeleton class="h-14 w-full rounded-lg" />
						</div>
						<div class="flex flex-wrap gap-2">
							<Skeleton class="h-5 w-16 rounded-full" />
							<Skeleton class="h-5 w-20 rounded-full" />
							<Skeleton class="h-5 w-14 rounded-full" />
						</div>
						<Skeleton class="h-9 w-full" />
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each filteredMembers as member}
				<Card class="grid gap-4">
					<CardContent class="grid gap-4 p-5">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(member.status))}>{member.status}</Badge>
							<strong class="text-sm font-bold text-muted-foreground">{member.role}</strong>
						</div>
						<h3 class="text-xl font-bold tracking-tight">{member.name}</h3>
						<p class="text-sm text-muted-foreground">{member.email}</p>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Last active')} <strong class="mt-1 block text-sm font-bold text-foreground">{member.lastActive}</strong>
							</div>
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Workload')} <strong class="mt-1 block text-sm font-bold text-foreground">{member.workload}%</strong>
							</div>
						</div>
						<div class="flex flex-wrap gap-2">
							{#each member.permissions as permission}
								<span class="rounded-full border bg-muted/40 px-2.5 py-0.5 text-xs font-semibold text-muted-foreground">{permission}</span>
							{/each}
						</div>
						<Button variant="outline" onclick={() => handleUpdateRole(member)} disabled={updatingRole === member.id}>{updatingRole === member.id ? t('Updating...') : t('Update role')}</Button>
					</CardContent>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
					{t('No team member matched your search.')}
				</div>
			{/each}
		</div>
	{/if}
</AppShell>