<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { NativeSelect, NativeSelectOption } from '$lib/components/ui/native-select/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { messageThreads } from '$lib/data/trade';
	import { statusTone } from '$lib/utils/format';
	import {
		listMessages,
		sendMessage,
		resolveMessageThread,
		updateMessageThread,
		createMessageThread,
		deleteMessageThread
	} from '$lib/api/messages';
	import type { MessageThread } from '$lib/data/trade';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';

	import PlusIcon from '@lucide/svelte/icons/plus';
	import MessageSquareIcon from '@lucide/svelte/icons/message-square';
	import ReplyIcon from '@lucide/svelte/icons/reply';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';
	import AlertCircleIcon from '@lucide/svelte/icons/alert-circle';
	import XIcon from '@lucide/svelte/icons/x';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';

	const filters = ['All', 'Email', 'WhatsApp', 'Portal', 'Internal'];

	function trStatus(s: string) {
		return t(s === 'All' ? 'Semua' : s === 'Open' ? 'Terbuka' : s === 'Waiting Reply' ? 'Menunggu balasan' : s === 'Escalated' ? 'Eskalasi' : 'Selesai');
	}

	function trFilter(f: string) {
		return t(f === 'All' ? 'Semua' : f);
	}

	let activeFilter = $state('All');
	let query = $state('');
	let error = $state('');
	let successMessage = $state('');
	let actionLoading = $state(false);

	// Compose dialog state
	let composeOpen = $state(false);
	let composeSubject = $state('');
	let composeParty = $state('');
	let composeChannel = $state<'Email' | 'WhatsApp' | 'Portal' | 'Internal'>('Email');
	let composeLinkedTo = $state('');
	let composeBody = $state('');

	// Reply dialog state
	let replyOpen = $state(false);
	let replyTarget = $state<MessageThread | null>(null);
	let replyBody = $state('');

	// Delete confirmation dialog
	let deleteOpen = $state(false);
	let deleteTarget = $state<MessageThread | null>(null);

	let threads = createRemoteList(listMessages, messageThreads);
	$effect(() => {
		threads.load();
	});

	let filteredThreads = $derived(
		threads.items.filter(
			(thread) =>
				(activeFilter === 'All' || thread.channel === activeFilter) &&
				[thread.subject, thread.party, thread.channel, thread.status, thread.lastMessage, thread.linkedTo, ...(thread.participants ?? [])].join(' ').toLowerCase().includes(query.trim().toLowerCase())
		)
	);

	let openCount = $derived(threads.items.filter((thread) => ['Open', 'Waiting Reply', 'Escalated'].includes(thread.status)).length);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	function openCompose() {
		composeSubject = '';
		composeParty = '';
		composeChannel = 'Email';
		composeLinkedTo = '';
		composeBody = '';
		error = '';
		composeOpen = true;
	}

	async function handleCreateThread() {
		if (!composeSubject.trim() || !composeParty.trim() || !composeBody.trim()) {
			error = t('Subjek, pihak lawan bicara, dan pesan wajib diisi.');
			return;
		}
		error = '';
		actionLoading = true;
		try {
			const res = await createMessageThread({
				subject: composeSubject.trim(),
				party: composeParty.trim(),
				channel: composeChannel,
				linkedTo: composeLinkedTo.trim() || undefined,
				lastMessage: composeBody.trim(),
				participants: [composeParty.trim(), 'MauEkspor Team'],
				status: 'Open',
				time: 'now'
			});
			if (res.data) {
				threads.upsert(res.data);
			} else {
				await threads.load();
			}
			composeOpen = false;
			successMessage = t('Thread berhasil dibuat.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
		} catch {
			error = t('Gagal membuat thread.');
		} finally {
			actionLoading = false;
		}
	}

	function openReply(thread: MessageThread) {
		replyTarget = thread;
		replyBody = '';
		error = '';
		replyOpen = true;
	}

	async function handleSendReply() {
		if (!replyTarget || !replyBody.trim()) {
			error = t('Isi balasan tidak boleh kosong.');
			return;
		}
		error = '';
		actionLoading = true;
		try {
			const res = await sendMessage(replyTarget.id, replyBody.trim());
			if (res.data) {
				threads.upsert(res.data);
			} else {
				await threads.load();
			}
			replyOpen = false;
			replyTarget = null;
			successMessage = t('Pesan berhasil dikirim.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
		} catch {
			error = t('Gagal mengirim pesan.');
		} finally {
			actionLoading = false;
		}
	}

	async function handleToggleResolve(thread: MessageThread) {
		error = '';
		try {
			const res =
				thread.status === 'Resolved'
					? await updateMessageThread(thread.id, { status: 'Open' })
					: await resolveMessageThread(thread.id);
			if (res.data) {
				threads.upsert(res.data);
			} else {
				await threads.load();
			}
		} catch {
			error = t('Gagal memperbarui status thread.');
		}
	}

	function openDelete(thread: MessageThread) {
		deleteTarget = thread;
		deleteOpen = true;
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		actionLoading = true;
		error = '';
		try {
			await deleteMessageThread(deleteTarget.id);
			threads.remove(deleteTarget.id);
			deleteOpen = false;
			deleteTarget = null;
			successMessage = t('Thread berhasil dihapus.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
		} catch {
			error = t('Gagal menghapus thread.');
		} finally {
			actionLoading = false;
		}
	}

	let paginationPage = $state(1);
	let paginationPageSize = $state(5);
	let pagedItems = $derived(paginate(filteredThreads ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredThreads?.length ?? 0, paginationPageSize));
</script>

<svelte:head>
	<title>{t('Pesan')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Pesan')} eyebrow={t('Komunikasi buyer, supplier, dan internal')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<div class="flex items-center gap-2">
				<Badge>{t('Pusat komunikasi')}</Badge>
				<Badge variant="outline">{t('Open')} {openCount}</Badge>
			</div>
			<CardTitle class="mt-3 font-display text-3xl font-black tracking-tight text-[#0b1d3a] md:text-4xl dark:text-white">
				{t('Jaga percakapan dagang tetap terhubung dengan catatan ekspor.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Lacak balasan buyer, penolakan bukti supplier, eskalasi internal, dan tindak lanjut order tanpa kehilangan konteks proyek.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={openCompose}>
				<PlusIcon class="size-4" />
				<span class="ms-1.5">{t('Tulis Pesan Baru')}</span>
			</Button>
			<Button variant="outline" onclick={() => threads.load()}>
				<RefreshCwIcon class="size-4" />
				<span class="ms-1.5">{t('Segarkan')}</span>
			</Button>
		</CardContent>
	</Card>

	{#if error}
		<div class="flex items-center justify-between rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-semibold text-destructive">
			<div class="flex items-center gap-2">
				<AlertCircleIcon class="size-4" />
				<span>{error}</span>
			</div>
			<button onclick={() => (error = '')}><XIcon class="size-4" /></button>
		</div>
	{/if}

	{#if successMessage}
		<div class="flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
			<div class="flex items-center gap-2">
				<CheckCircle2Icon class="size-4" />
				<span>{successMessage}</span>
			</div>
			<button onclick={() => (successMessage = '')}><XIcon class="size-4" /></button>
		</div>
	{/if}

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap gap-2">
			{#each filters as filter}
				<Button variant={activeFilter === filter ? 'default' : 'outline'} size="sm" onclick={() => (activeFilter = filter)}>
					{trFilter(filter)}
				</Button>
			{/each}
		</div>
		<Input bind:value={query} type="search" placeholder={t('Cari thread, pihak, partisipan...')} class="w-[min(390px,100%)]" />
	</div>

	{#if threads.loading}
		<div class="grid gap-4">
			{#each Array(5) as _}
				<Card>
					<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
						<div class="min-w-0 flex-1">
							<Skeleton class="h-5 w-24" />
							<Skeleton class="mt-2 h-6 w-3/4" />
							<Skeleton class="mt-1 h-4 w-full" />
							<Skeleton class="mt-1 h-4 w-1/3" />
						</div>
						<aside class="grid justify-items-end gap-2 whitespace-nowrap">
							<Skeleton class="h-5 w-20" />
							<Skeleton class="h-4 w-28" />
							<Skeleton class="h-9 w-24" />
						</aside>
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else}
		<div class="grid gap-4">
			{#each pagedItems as thread (thread.id)}
				<Card class="transition-shadow hover:shadow-md">
					<CardContent class="flex flex-wrap items-start justify-between gap-4 p-5">
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<Badge variant={toneVariant(statusTone(thread.status))}>
									{trStatus(thread.status)}
								</Badge>
								<Badge variant="outline" class="text-xs">{thread.channel}</Badge>
							</div>
							<h3 class="mt-2 text-lg font-bold tracking-tight text-foreground">{thread.subject}</h3>
							<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{thread.lastMessage}</p>
							<small class="mt-2 block text-xs text-muted-foreground">
								<strong>{thread.party}</strong> · {thread.time || 'now'}
							</small>
						</div>
						<aside class="flex flex-col items-end gap-2 whitespace-nowrap">
							{#if thread.linkedTo}
								<strong class="text-xs font-semibold text-muted-foreground">{thread.linkedTo}</strong>
							{/if}
							<span class="block text-xs text-muted-foreground">{(thread.participants ?? []).join(', ')}</span>

							<div class="mt-2 flex flex-wrap items-center gap-1.5">
								<Button size="sm" variant="outline" onclick={() => openReply(thread)}>
									<ReplyIcon class="size-3.5" />
									<span class="ms-1">{t('Balas')}</span>
								</Button>
								<Button size="sm" variant={thread.status === 'Resolved' ? 'secondary' : 'default'} onclick={() => handleToggleResolve(thread)}>
									{thread.status === 'Resolved' ? t('Buka Kembali') : t('Selesai')}
								</Button>
								<button
									onclick={() => openDelete(thread)}
									class="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
									title={t('Hapus Thread')}
								>
									<Trash2Icon class="size-3.5" />
								</button>
							</div>
						</aside>
					</CardContent>
				</Card>
			{:else}
				<div class="rounded-xl border border-dashed p-10 text-center font-semibold text-muted-foreground">
					{t('Tidak ada thread pesan yang cocok dengan pencarian.')}
				</div>
			{/each}
		</div>
	{/if}

	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredThreads?.length ?? 0} />
</AppShell>

<!-- COMPOSE NEW THREAD DIALOG -->
{#if composeOpen}
	<Dialog.Root bind:open={composeOpen}>
		<Dialog.Content class="sm:max-w-lg">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base font-bold">
					<MessageSquareIcon class="size-5 text-primary" />
					<span>{t('Buat Thread Baru')}</span>
				</Dialog.Title>
				<Dialog.Description class="text-xs">
					{t('Mulai percakapan atau catatan korespondensi baru dengan buyer, supplier, atau tim internal.')}
				</Dialog.Description>
			</Dialog.Header>

			<div class="grid gap-3 py-2 text-xs">
				<div>
					<label for="compose-subject" class="mb-1 block font-semibold text-foreground">{t('Subjek')}</label>
					<Input id="compose-subject" bind:value={composeSubject} placeholder="Contoh: Negosiasi Harga Kopi Arabika Batch 2" class="text-xs" />
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="compose-party" class="mb-1 block font-semibold text-foreground">{t('Pihak Lawan Bicara')}</label>
						<Input id="compose-party" bind:value={composeParty} placeholder="Hikari Foods Co. / PT Supplier" class="text-xs" />
					</div>
					<div>
						<label for="compose-channel" class="mb-1 block font-semibold text-foreground">{t('Saluran Komunikasi')}</label>
						<NativeSelect id="compose-channel" bind:value={composeChannel} class="h-8 text-xs">
							<NativeSelectOption value="Email">Email</NativeSelectOption>
							<NativeSelectOption value="WhatsApp">WhatsApp</NativeSelectOption>
							<NativeSelectOption value="Portal">Portal</NativeSelectOption>
							<NativeSelectOption value="Internal">Internal</NativeSelectOption>
						</NativeSelect>
					</div>
				</div>

				<div>
					<label for="compose-linked" class="mb-1 block font-semibold text-foreground">{t('Terkait Proyek / Dokumen')}</label>
					<Input id="compose-linked" bind:value={composeLinkedTo} placeholder="EXP-2408-017 / ORD-001" class="text-xs" />
				</div>

				<div>
					<label for="compose-body" class="mb-1 block font-semibold text-foreground">{t('Pesan Awal')}</label>
					<Textarea id="compose-body" bind:value={composeBody} rows={4} placeholder="Tuliskan isi pesan atau ringkasan percakapan..." class="text-xs" />
				</div>
			</div>

			<Dialog.Footer>
				<Button variant="outline" onclick={() => (composeOpen = false)} disabled={actionLoading}>
					{t('Batal')}
				</Button>
				<Button onclick={handleCreateThread} disabled={actionLoading}>
					{#if actionLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menyimpan...')}</span>
					{:else}
						{t('Kirim Pesan Baru')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- REPLY DIALOG -->
{#if replyOpen && replyTarget}
	<Dialog.Root bind:open={replyOpen}>
		<Dialog.Content class="sm:max-w-lg">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base font-bold">
					<ReplyIcon class="size-5 text-primary" />
					<span>{t('Balas Pesan')} — {replyTarget.party}</span>
				</Dialog.Title>
				<Dialog.Description class="text-xs">
					{replyTarget.subject}
				</Dialog.Description>
			</Dialog.Header>

			<div class="space-y-3 py-2 text-xs">
				<div class="rounded-lg border bg-muted/20 p-3">
					<span class="text-[11px] font-semibold text-muted-foreground">{t('Riwayat Terakhir')}:</span>
					<p class="mt-1 text-xs text-foreground italic">"{replyTarget.lastMessage}"</p>
				</div>

				<div>
					<label for="reply-body" class="mb-1 block font-semibold text-foreground">{t('Isi balasan Anda...')}</label>
					<Textarea id="reply-body" bind:value={replyBody} rows={4} placeholder={t('Isi balasan Anda...')} class="text-xs" />
				</div>
			</div>

			<Dialog.Footer>
				<Button variant="outline" onclick={() => (replyOpen = false)} disabled={actionLoading}>
					{t('Batal')}
				</Button>
				<Button onclick={handleSendReply} disabled={actionLoading}>
					{#if actionLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menyimpan...')}</span>
					{:else}
						{t('Kirim Balasan')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- DELETE THREAD DIALOG -->
{#if deleteOpen && deleteTarget}
	<Dialog.Root bind:open={deleteOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base text-destructive">
					<Trash2Icon class="size-4" />
					<span>{t('Hapus Thread')}</span>
				</Dialog.Title>
				<Dialog.Description class="text-xs">
					{t('Apakah Anda yakin ingin menghapus thread percakapan ini?')}
					<div class="my-2 rounded bg-muted p-2 font-mono text-xs">
						{deleteTarget.subject} ({deleteTarget.party})
					</div>
					<span class="text-destructive font-semibold">{t('Tindakan ini tidak dapat dibatalkan.')}</span>
				</Dialog.Description>
			</Dialog.Header>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (deleteOpen = false)} disabled={actionLoading}>
					{t('Batal')}
				</Button>
				<Button variant="destructive" onclick={confirmDelete} disabled={actionLoading}>
					{#if actionLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menghapus...')}</span>
					{:else}
						{t('Hapus')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}