<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { apiKeys as seedApiKeys } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { listApiKeys } from '$lib/api/api-keys';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
	import { createApiKey, revokeApiKey } from '$lib/api/api-keys';

	const filters = ['All', 'Active', 'Expiring Soon', 'Revoked'];
	let activeFilter = $state('All');
	let query = $state('');
	let created = $state(false);
	let creating = $state(false);
	let revokingId = $state('');
	let revoked = $state(false);
	let keys = createRemoteList(listApiKeys, seedApiKeys);
	let error = $state('');
	let filteredKeys = $derived(
		keys.items.filter(
			(key) =>
				(activeFilter === 'All' || key.status === activeFilter) &&
				[key.name, key.prefix, key.status, key.owner, ...key.scopes].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let activeCount = $derived(keys.items.filter((key) => key.status === 'Active').length + (created ? 1 : 0));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	$effect(() => {
		keys.load();
	});

	async function handleCreate() {
		error = '';
		creating = true;
		try {
			await createApiKey(`Export API Key ${keys.items.length + 1}`, ['catalogs:read', 'quotations:read']);
			created = true;
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
			await revokeApiKey(id);
			revoked = true;
		} catch {
			error = t('Gagal mencabut API key.');
		} finally {
			revokingId = '';
		}
	}
</script>

<svelte:head>
	<title>{t('Kunci API')} | MauEkspor</title>
</svelte:head>

<AppShell title="API Keys" eyebrow={t('Developer access controls')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Akses developer')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Manage API credentials for logistics, finance, and reporting integrations.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Create scoped API keys, monitor usage, and revoke old credentials before they become integration or security risks.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleCreate} disabled={creating}>{created ? t('Key created') : creating ? t('Creating...') : t('Create API key')}</Button>
			<Badge variant="secondary">{t('Active')} {activeCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if created}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('API key created.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Key tersimpan di backend; simpan nilai rahasia di tempat aman.')}</span>
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

	<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredKeys as key}
			<Card class="gap-4">
				<div class="flex items-center justify-between gap-3">
					<Badge variant={toneVariant(statusTone(revoked ? 'Revoked' : key.status))}>{revoked ? 'Revoked' : key.status}</Badge>
					<strong class="font-mono text-sm font-bold text-muted-foreground">{key.prefix}...</strong>
				</div>
				<CardHeader class="p-0">
					<CardTitle class="text-xl font-bold tracking-tight">{key.name}</CardTitle>
					<CardDescription>{key.owner} · {t('Last used')} {revoked ? 'Never' : key.lastUsed}</CardDescription>
				</CardHeader>
				<CardContent class="grid gap-3 p-0">
					<div class="grid grid-cols-2 gap-2">
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Created')} <strong class="mt-1 block text-sm font-bold text-foreground">{key.createdAt}</strong>
						</div>
						<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
							{t('Scopes')} <strong class="mt-1 block text-sm font-bold text-foreground">{key.scopes.length}</strong>
						</div>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each key.scopes as scope}
							<span class="rounded-full border bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">{scope}</span>
						{/each}
					</div>
				</CardContent>
				<Button variant="outline" onclick={() => handleRevoke(key.id)} disabled={revokingId === key.id}>{revokingId === key.id ? t('Revoking...') : t('Revoke')}</Button>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">{t('No API key matched your search.')}</div>
		{/each}
	</div>
</AppShell>