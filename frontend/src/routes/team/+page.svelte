<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { teamMembers as seedMembers } from '$lib/data/trade';
	import type { TeamMember } from '$lib/data/trade';
	import { listTeamMembers, inviteTeamMember, updateTeamMemberRole, updateTeamMember, removeTeamMember } from '$lib/api/team';
	import { downloadFile } from '$lib/api/client';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';
import Pagination from '$lib/components/Pagination.svelte';
import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
import SortSelect from '$lib/components/SortSelect.svelte';
import { paginate, calcTotalPages } from '$lib/utils/pagination';
import { sortBy, type SortDir } from '$lib/utils/sort';
import { formatRelative } from '$lib/utils/date';
import { syncFiltersToUrl } from '$lib/utils/urlFilters';
import { page } from '$app/state';

	const filters = ['All', 'Admin', 'Operations', 'Compliance', 'Finance', 'Sales'];
	const roles: TeamMember['role'][] = ['Admin', 'Operations', 'Compliance', 'Finance', 'Sales'];
	let activeFilter = $state(page.url.searchParams.get('status') ?? 'All');
	let query = $state(page.url.searchParams.get('query') ?? '');
	let sortKey = $state(page.url.searchParams.get('sort') ?? '');
	let sortDir = $state<SortDir>((page.url.searchParams.get('dir') as SortDir) ?? 'asc');
	const sortOptions = [
		{ value: 'name', label: t('Nama') },
		{ value: 'role', label: t('Peran') },
		{ value: 'workload', label: t('Beban kerja') },
		{ value: 'status', label: t('Status') },
		{ value: 'lastActive', label: t('Terakhir aktif') }
	];
	let invited = $state(false);
	let error = $state('');
	let message = $state('');
	let inviting = $state(false);
	let showInvite = $state(false);
	let inviteEmail = $state('');
	let inviteRole = $state<TeamMember['role']>('Operations');
	let busyId = $state('');
	// Tautan aktivasi undangan terakhir agar admin bisa meneruskannya.
	let inviteLink = $state('');
	let copiedInvite = $state(false);

	// Konfirmasi terpusat untuk hapus anggota tim (pengganti window.confirm).
	const confirm = createConfirmController();

	// Simpan filter & pencarian ke URL agar tahan refresh/back/dibagikan.
	let syncTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const state = { query, status: activeFilter === 'All' ? '' : activeFilter, sort: sortKey, dir: sortKey ? sortDir : '' };
		clearTimeout(syncTimer);
		syncTimer = setTimeout(() => syncFiltersToUrl(page.url, state, { query: '', status: '', sort: '', dir: '' }, ['query', 'status', 'sort', 'dir']), 250);
		return () => clearTimeout(syncTimer);
	});

	let teamMembers = createRemoteList(listTeamMembers, seedMembers);
	$effect(() => {
		teamMembers.load();
	});

	let filteredMembers = $derived(
		sortBy(
			teamMembers.items.filter(
				(member) =>
					(activeFilter === 'All' || member.role === activeFilter) &&
					[member.name, member.email, member.role, member.status, ...(member.permissions ?? [])].join(' ').toLowerCase().includes(query.trim().toLowerCase())
			),
			sortKey,
			sortDir
		)
	);
	let activeCount = $derived(teamMembers.items.filter((member) => member.status === 'Active').length);
	let avgWorkload = $derived(Math.round(teamMembers.items.reduce((sum, member) => sum + member.workload, 0) / (teamMembers.items.length || 1)));


	async function handleInvite() {
		error = '';
		if (!inviteEmail.trim()) {
			error = t('Email wajib diisi.');
			return;
		}
		inviting = true;
		try {
			const res = await inviteTeamMember(inviteEmail.trim(), inviteRole);
			invited = true;
			const path = res.meta?.activation_path as string | undefined;
			inviteLink = path ? `${window.location.origin}${path}` : '';
			copiedInvite = false;
			message = t('Undangan dibuat. Teruskan tautan aktivasi ke anggota baru.');
			if (res.data) teamMembers.upsert(res.data);
			else await teamMembers.load();
			showInvite = false;
			inviteEmail = '';
		} catch (err) {
			error = err instanceof Error ? err.message : t('Gagal mengirim undangan.');
		} finally {
			inviting = false;
		}
	}

	async function copyInviteLink() {
		if (!inviteLink) return;
		try {
			await navigator.clipboard.writeText(inviteLink);
			copiedInvite = true;
			setTimeout(() => (copiedInvite = false), 2500);
		} catch {
			error = t('Gagal menyalin tautan aktivasi.');
		}
	}

	let updatingRole = $state('');
	async function handleUpdateRole(member: TeamMember, role: TeamMember['role']) {
		error = '';
		updatingRole = member.id;
		try {
			const res = await updateTeamMemberRole(member.id, role);
			if (res.data) teamMembers.upsert(res.data);
			message = `Peran ${member.name} diubah ke ${role}.`;
		} catch {
			error = t('Gagal memperbarui peran.');
		} finally {
			updatingRole = '';
		}
	}

	async function handleToggleStatus(member: TeamMember) {
		error = '';
		busyId = member.id;
		try {
			const next = member.status === 'Active' ? 'Suspended' : 'Active';
			const res = await updateTeamMember(member.id, { status: next });
			if (res.data) teamMembers.upsert(res.data);
			message = `${member.name} kini ${next}.`;
		} catch {
			error = t('Gagal memperbarui status.');
		} finally {
			busyId = '';
		}
	}

	async function handleRemove(member: TeamMember) {
		error = '';
		busyId = member.id;
		try {
			await removeTeamMember(member.id);
			teamMembers.remove(member.id);
			message = `${member.name} dihapus dari tim.`;
		} catch {
			error = t('Gagal menghapus anggota.');
		} finally {
			busyId = '';
		}
	}
	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredMembers ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredMembers?.length ?? 0, paginationPageSize));

	// Reset ke halaman pertama saat filter/pencarian/pengurutan berubah.
	$effect(() => {
		activeFilter;
		query;
		sortKey;
		sortDir;
		paginationPage = 1;
	});

</script>

<svelte:head>
	<title>{t('Team')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Team')} eyebrow={t('Roles and workspace access')}>
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
			<Button onclick={() => (showInvite ? (showInvite = false) : (showInvite = true))}>{showInvite ? t('Batal') : t('Invite member')}</Button>
			<Button variant="outline" onclick={() => downloadFile('/team-members/export.csv', 'team-members.csv')}>{t('Export CSV')}</Button>
			<Button variant="outline" onclick={() => downloadFile('/team-members/export.xlsx', 'team-members.xlsx')}>{t('Excel (.xlsx)')}</Button>
			<Badge>{t('Active')} {activeCount}</Badge>
		</CardContent>
		{#if showInvite}
			<CardContent class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Email')}
						<Input bind:value={inviteEmail} placeholder="nama@perusahaan.example" />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Peran')}
						<select bind:value={inviteRole} aria-label={t('Peran undangan')} class="h-10 rounded-md border bg-background px-3 text-sm">
							{#each roles as role}
								<option value={role}>{role}</option>
							{/each}
						</select>
					</label>
				</div>
				<Button class="w-fit" disabled={inviting} onclick={handleInvite}>{inviting ? t('Inviting...') : t('Kirim undangan')}</Button>
			</CardContent>
		{/if}
	</Card>

	{#if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}
	{#if message}
		<p role="status" class="rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
	{/if}

	{#if teamMembers.error}
		<p role="alert" class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{teamMembers.error}</p>
	{/if}

	{#if invited}
		<div role="status" class="grid gap-3 rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<div>
				<strong class="block">{t('Undangan dibuat. Teruskan tautan aktivasi ke anggota baru.')}</strong>
			</div>
			{#if inviteLink}
				<div class="flex flex-wrap items-center gap-2">
					<code class="min-w-0 flex-1 truncate rounded bg-background/80 px-2 py-1.5 font-mono text-xs">{inviteLink}</code>
					<Button size="sm" variant="outline" onclick={copyInviteLink}>
						{copiedInvite ? t('Tautan aktivasi tersalin.') : t('Salin tautan aktivasi')}
					</Button>
				</div>
			{/if}
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{filter === 'All' ? t('Semua') : label(filter)}</Button>
			{/each}
		</div>
		<div class="flex flex-wrap items-center gap-2">
			<Input bind:value={query} type="search"
				aria-label={t('Search member, role, permission...')} placeholder={t('Search member, role, permission...')} class="w-[min(390px,100%)]" />
			<SortSelect bind:key={sortKey} bind:dir={sortDir} options={sortOptions} placeholder={t('Urutkan')} />
		</div>
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
			{#each pagedItems as member}
				<Card class="grid gap-4">
					<CardContent class="grid gap-4 p-5">
						<div class="flex items-center justify-between gap-3">
							<Badge variant={toneVariant(statusTone(member.status))}>{label(member.status)}</Badge>
							<strong class="text-sm font-bold text-muted-foreground">{label(member.role)}</strong>
						</div>
						<h3 class="text-xl font-bold tracking-tight">{member.name}</h3>
						<p class="text-sm text-muted-foreground">{member.email}</p>
						<div class="grid grid-cols-2 gap-2">
							<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
								{t('Last active')} <strong class="mt-1 block text-sm font-bold text-foreground">{formatRelative(member.lastActive)}</strong>
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
						<select
							class="h-10 rounded-md border bg-background px-3 text-sm"
							aria-label={t('Ubah peran anggota')}
							disabled={updatingRole === member.id}
							value={label(member.role)}
							onchange={(e) => handleUpdateRole(member, (e.currentTarget as HTMLSelectElement).value as TeamMember['role'])}
						>
							{#each roles as role}
								<option value={role}>{role}</option>
							{/each}
						</select>
						<div class="grid grid-cols-2 gap-2">
							<Button variant="outline" disabled={busyId === member.id} onclick={() => handleToggleStatus(member)}>
								{member.status === 'Active' ? t('Suspend') : t('Aktifkan')}
							</Button>
							<Button variant="outline" class="text-destructive" disabled={busyId === member.id} onclick={() =>
								confirm.ask({
									title: t('Hapus anggota tim'),
									description: t('Anggota ini akan dihapus permanen dari workspace.'),
									detail: member.name,
									action: () => handleRemove(member)
								})}>{t('Hapus')}</Button>
						</div>
					</CardContent>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
					{t('No team member matched your search.')}
				</div>
			{/each}
		</div>
	{/if}
	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredMembers?.length ?? 0} />

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