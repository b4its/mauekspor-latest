<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { messageThreads } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import { listMessages, sendMessage, resolveMessageThread } from '$lib/api/messages';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { t } from '$lib/i18n.svelte';

	const filters = ['All', 'Email', 'WhatsApp', 'Portal', 'Internal'];

	function trStatus(s: string) {
		return t(s === 'All' ? 'Semua' : s === 'Open' ? 'Terbuka' : s === 'Waiting Reply' ? 'Menunggu balasan' : s === 'Escalated' ? 'Eskalasi' : 'Selesai');
	}

	function trFilter(f: string) {
		return t(f === 'All' ? 'Semua' : f);
	}
	let activeFilter = $state('All');
	let query = $state('');
	let sent = $state(false);
	let sending = $state(false);
	let resolved = $state(false);
	let error = $state('');
	let resolvedId = $state('');

	let threads = createRemoteList(listMessages, messageThreads);
	$effect(() => {
		threads.load();
	});

	let filteredThreads = $derived(
		threads.items.filter(
			(thread) =>
				(activeFilter === 'All' || thread.channel === activeFilter) &&
				[thread.subject, thread.party, thread.channel, thread.status, thread.lastMessage, ...thread.participants].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);
	let openCount = $derived(threads.items.filter((thread) => ['Open', 'Waiting Reply', 'Escalated'].includes(thread.status)).length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleSend() {
		error = '';
		sending = true;
		try {
			await sendMessage(threads.items[0]?.id ?? 'msg-001', t('Menindaklanjuti order ekspor terbaru.'));
			sent = true;
		} catch {
			error = t('Gagal mengirim pesan.');
		} finally {
			sending = false;
		}
	}

	async function handleResolve(threadId: string) {
		error = '';
		try {
			await resolveMessageThread(threadId);
			resolvedId = threadId;
		} catch {
			error = t('Gagal menyelesaikan thread.');
		}
	}
</script>

<svelte:head>
	<title>Messages | MauEkspor</title>
</svelte:head>

<AppShell title="Messages" eyebrow={t('Komunikasi buyer, supplier, dan internal')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge>{t('Pusat komunikasi')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
				{t('Jaga percakapan dagang tetap terhubung dengan catatan ekspor.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Lacak balasan buyer, penolakan bukti supplier, eskalasi internal, dan tindak lanjut order tanpa kehilangan konteks proyek.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={handleSend} disabled={sending}>{sent ? t('Pesan terkirim') : sending ? t('Mengirim...') : t('Kirim pesan')}</Button>
			<Badge variant="outline">{t('Open')} {openCount}</Badge>
		</CardContent>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if sent}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Pesan terkirim.')}</strong>
			<span class="block text-sm text-muted-foreground">
				{t('Pesan terkirim melalui backend.')}
			</span>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>{trFilter(filter)}</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari thread, pihak, partisipan...')} class="w-[min(390px,100%)]" />
	</div>

	<div class="grid gap-4">
		{#each filteredThreads as thread}
			<Card>
				<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
					<div class="min-w-0 flex-1">
						<Badge variant={toneVariant(statusTone(resolved || resolvedId === thread.id ? 'Resolved' : thread.status))}>{t(resolved || resolvedId === thread.id ? 'Selesai' : trStatus(thread.status))}</Badge>
						<h3 class="mt-2 text-lg font-bold tracking-tight">{thread.subject}</h3>
						<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{thread.lastMessage}</p>
						<small class="block text-xs text-muted-foreground">{thread.party} · {thread.channel} · {thread.time}</small>
					</div>
					<aside class="grid justify-items-end gap-2 whitespace-nowrap">
						<strong class="text-sm font-bold">{thread.linkedTo}</strong>
						<span class="block text-sm text-muted-foreground">{thread.participants.join(', ')}</span>
						<Button variant="outline" size="sm" onclick={() => handleResolve(thread.id)}>{resolvedId === thread.id ? t('Selesai') : t('Selesaikan')}</Button>
					</aside>
				</CardContent>
			</Card>
		{:else}
			<div class="rounded-xl border border-dashed p-6 text-center font-semibold text-muted-foreground">
				{t('Tidak ada thread pesan yang cocok dengan pencarian.')}
			</div>
		{/each}
	</div>
</AppShell>