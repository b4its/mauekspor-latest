<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { deleteUser } from '$lib/api/users';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let error = $state('');
	let deleting = $state(false);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus pengguna ini secara permanen?'))) return;
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

<AppShell title={data.user.id} eyebrow={t('User detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.user.status))}>{data.user.status}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.user.fullName}
				</CardTitle>
				<CardDescription class="mt-2">{data.user.email}</CardDescription>
			</div>
			<Badge variant="secondary">{data.user.role}</Badge>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if error}
			<p class="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
		{/if}
	</Card>

	<Card>
		<CardHeader><CardTitle>{t('Detail akun')}</CardTitle></CardHeader>
		<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Email')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.email}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Role')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.role}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Status')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.status}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Created')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.createdAt}</strong>
			</div>
			<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
				{t('Login terakhir')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.user.lastLogin}</strong>
			</div>
		</CardContent>
	</Card>

	<div class="mt-4">
		<Button variant="outline" href="/users">{t('Kembali ke pengguna')}</Button>
	</div>
</AppShell>