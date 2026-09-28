<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone, toneVariant } from '$lib/utils/format';
	import { deleteUser } from '$lib/api/users';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';
	import { formatDateTime } from '$lib/utils/date';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
	import { createConfirmController } from '$lib/utils/confirm.svelte';
	import { label } from '$lib/utils/labels';

	let { data } = $props();
	let error = $state('');
	let deleting = $state(false);
	const confirm = createConfirmController();


	async function handleDelete() {
		error = '';
		deleting = true;
		try {
			await deleteUser(data.user.id);
			goto('/users');
		} catch {
			error = t('Gagal menghapus pengguna.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.user.fullName} | MauEkspor</title>
</svelte:head>

<AppShell back="/users" title={data.user.fullName || data.user.id} eyebrow={`${t('User')} · ${data.user.id}`}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.user.status))}>{label(data.user.status)}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.user.fullName}
				</CardTitle>
				<CardDescription class="mt-2">{data.user.email}</CardDescription>
			</div>
			<Badge variant="secondary">{label(data.user.role)}</Badge>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button
				variant="outline"
				class="text-destructive"
				disabled={deleting}
				onclick={() =>
					confirm.ask({
						title: t('Hapus pengguna'),
						description: t('Pengguna ini akan dihapus permanen dari workspace.'),
						detail: data.user.fullName,
						action: handleDelete
					})}
			>
				{deleting ? t('Menghapus...') : t('Hapus')}
			</Button>
		</div>
		{#if error}
			<p class="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive" role="alert">{error}</p>
		{/if}
	</Card>

	<Card>
		<CardHeader><CardTitle>{t('Detail akun')}</CardTitle></CardHeader>
		<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Email')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.email}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Role')} <strong class="mt-1 block text-sm font-bold text-foreground">{label(data.user.role)}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Status')} <strong class="mt-1 block text-sm font-bold text-foreground">{label(data.user.status)}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Created')} <strong class="mt-1 block text-sm font-bold text-foreground">{formatDateTime(data.user.createdAt)}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Login terakhir')} <strong class="mt-1 block text-sm font-bold text-foreground">{formatDateTime(data.user.lastLogin)}</strong>
			</div>
		</CardContent>
	</Card>

	<div class="mt-4">
		<Button variant="outline" href="/users">{t('Kembali ke pengguna')}</Button>
	</div>

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