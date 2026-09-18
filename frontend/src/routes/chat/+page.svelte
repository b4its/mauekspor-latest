<script lang="ts">
	import { tick } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { MarkdownRenderer } from '$lib/components/MarkdownRenderer';
	import ThinkingIndicator from '$lib/components/ThinkingIndicator.svelte';
	import TypewriterText from '$lib/components/TypewriterText.svelte';
	import {
		listChatSessions,
		createChatSession,
		deleteChatSession,
		renameChatSession,
		sendSessionMessage,
		getChatSuggestions,
		getChatSession,
		type ChatSession
	} from '$lib/api/chat';
	import { t } from '$lib/i18n.svelte';

	import PanelRightOpenIcon from '@lucide/svelte/icons/panel-right-open';
	import PanelRightCloseIcon from '@lucide/svelte/icons/panel-right-close';
	import MessageSquarePlusIcon from '@lucide/svelte/icons/message-square-plus';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import SendHorizonalIcon from '@lucide/svelte/icons/send-horizonal';
	import BotIcon from '@lucide/svelte/icons/bot';
	import UserIcon from '@lucide/svelte/icons/user';
	import SearchIcon from '@lucide/svelte/icons/search';
	import PencilIcon from '@lucide/svelte/icons/pencil';
	import CopyIcon from '@lucide/svelte/icons/copy';
	import CheckIcon from '@lucide/svelte/icons/check';
	import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
	import XIcon from '@lucide/svelte/icons/x';

	let sessions = $state<ChatSession[]>([]);
	let activeId = $state('');
	let input = $state('');
	let sending = $state(false);
	let loading = $state(true);
	let error = $state('');
	let suggestions = $state<{ question: string; context?: string }[]>([]);
	let sidebarOpen = $state(true);
	let messagesEl = $state<HTMLDivElement | null>(null);
	let searchQuery = $state('');
	// Track which AI message is currently animating (the latest one)
	let typingMessageId = $state<string | null>(null);

	// Rename modal
	let renameDialogOpen = $state(false);
	let renameTarget = $state<ChatSession | null>(null);
	let renameTitle = $state('');

	// Delete modal
	let deleteDialogOpen = $state(false);
	let deleteTarget = $state<ChatSession | null>(null);

	let filteredSessions = $derived(
		searchQuery.trim()
			? sessions.filter((s) => s.title.toLowerCase().includes(searchQuery.toLowerCase()))
			: sessions
	);

	// ── Pagination & grouping sesi ──
	let sessionPage = $state(1);
	const SESSION_PAGE_SIZE = 30;
	let sessionTotalPages = $derived(Math.max(1, Math.ceil(filteredSessions.length / SESSION_PAGE_SIZE)));
	let pagedSessions = $derived(
		filteredSessions.slice((sessionPage - 1) * SESSION_PAGE_SIZE, sessionPage * SESSION_PAGE_SIZE)
	);
	// Kelompokkan sesi yang punya pesan vs kosong
	let groupedSessions = $derived({
		active: pagedSessions.filter((s) => (s.messageCount ?? s.messages.length) > 0),
		empty: pagedSessions.filter((s) => (s.messageCount ?? s.messages.length) === 0)
	});
	$effect(() => {
		if (sessionPage > sessionTotalPages) sessionPage = sessionTotalPages;
	});

	async function loadSessions() {
		try {
			sessions = (await listChatSessions()).data;
			if (!activeId && sessions.length > 0) activeId = sessions[0].id;
		} catch {
			error = t('Tidak dapat memuat sesi chat dari server.');
		} finally { loading = false; }
	}

	async function loadSuggestions() {
		try { suggestions = (await getChatSuggestions()).data; }
		catch { suggestions = []; }
	}

	$effect(() => { loadSessions(); loadSuggestions(); });

	$effect(() => {
		const msgs = active?.messages ?? [];
		if (msgs.length && messagesEl) {
			tick().then(() => { if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight; });
		}
	});

	let active = $derived(sessions.find((s) => s.id === activeId) ?? null);

	async function switchSession(id: string) {
		if (id === activeId) return;
		activeId = id;
		error = '';
		try {
			const fresh = (await getChatSession(id)).data;
			const idx = sessions.findIndex((s) => s.id === id);
			if (idx >= 0) sessions[idx] = fresh;
		} catch { error = t('Tidak dapat memuat sesi.'); }
	}

	function isUser(role: string) { return role.toLowerCase() === 'user'; }

	async function newSession() {
		error = '';
		try {
			const session = (await createChatSession('')).data;
			sessions = [session, ...sessions];
			activeId = session.id;
		} catch { error = t('Gagal membuat sesi baru.'); }
	}

	async function removeSession(id: string) {
		try {
			await deleteChatSession(id);
			sessions = sessions.filter((s) => s.id !== id);
			if (activeId === id) activeId = sessions[0]?.id ?? '';
		} catch { error = t('Gagal menghapus sesi.'); }
	}

	function openRename(session: ChatSession) {
		renameTarget = session; renameTitle = session.title; renameDialogOpen = true;
	}

	async function confirmRename() {
		if (!renameTarget || !renameTitle.trim()) return;
		const target = renameTarget;
		try {
			const updated = (await renameChatSession(target.id, renameTitle.trim())).data;
			const idx = sessions.findIndex((s) => s.id === target.id);
			if (idx >= 0) sessions[idx] = updated;
			renameDialogOpen = false; renameTarget = null;
		} catch { error = t('Gagal mengganti nama sesi.'); }
	}

	function openDelete(session: ChatSession) { deleteTarget = session; deleteDialogOpen = true; }

	async function confirmDelete() {
		if (!deleteTarget) return;
		await removeSession(deleteTarget.id);
		deleteDialogOpen = false; deleteTarget = null;
	}

	// ── Copy to clipboard ──
	let copiedId = $state<string | null>(null);

	async function copyText(text: string, msgIdx: number) {
		try {
			await navigator.clipboard.writeText(text);
			copiedId = `copy-${msgIdx}`;
			setTimeout(() => { copiedId = null; }, 2000);
		} catch { /* fallback */ }
	}

	// ── Optimistic send ──
	async function send(textOverride?: string) {
		const text = (textOverride ?? input).trim();
		if (!text || sending || !active) return;
		error = '';
		input = '';

		// Optimistic: tampilkan pesan user langsung
		const userMsg = { role: 'user', text };
		const localMsgs = [...(active?.messages ?? []), userMsg];
		active!.messages = localMsgs; // trigger reactivity

		sending = true;
		try {
			const updated = (await sendSessionMessage(active!.id, text)).data;
			const idx = sessions.findIndex((s) => s.id === active!.id);
			if (idx >= 0) sessions[idx] = updated;
			activeId = updated.id;
			// Set typing effect untuk pesan AI terbaru
			const aiMsgCount = updated.messages.filter((m: { role: string }) => m.role === 'ai').length;
			typingMessageId = `ai-${aiMsgCount - 1}`;
		} catch {
			error = t('Gagal mengirim pesan.');
		} finally { sending = false; }
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
	}
</script>

<svelte:head>
	<title>{t('Chat')} | MauEkspor</title>
</svelte:head>

<AppShell title="Chat" eyebrow={t('Asisten dagang AI')}>
	<div class="relative flex h-[calc(100dvh-11rem)] min-h-[450px] overflow-hidden rounded-xl border bg-card shadow-sm lg:h-[calc(100dvh-10rem)]">
		<!-- Backdrop untuk mobile & tablet -->
		{#if sidebarOpen}
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div class="fixed inset-0 z-30 bg-black/30 lg:hidden" role="presentation" onclick={() => (sidebarOpen = false)}></div>
		{/if}

		<!-- Sidebar -->
		<aside
			class="absolute inset-y-0 left-0 z-40 flex flex-col border-r bg-card transition-all duration-200 lg:relative {sidebarOpen ? 'w-72' : 'w-0 overflow-hidden'}">
			<div class="flex shrink-0 items-center justify-between gap-2 border-b px-3 py-2.5">
				<h3 class="truncate text-sm font-bold">{t('Riwayat Sesi')}</h3>
				<div class="flex items-center gap-0.5 shrink-0">
					<Button variant="ghost" size="sm" onclick={newSession} title={t('Sesi baru')} class="h-8 w-8 p-0">
						<MessageSquarePlusIcon class="size-4" />
					</Button>
					<Button variant="ghost" size="sm" onclick={() => (sidebarOpen = false)} class="h-8 w-8 p-0" title={t('Tutup')}>
						<ChevronLeftIcon class="size-4" />
					</Button>
				</div>
			</div>

			<div class="flex w-72 flex-1 flex-col overflow-hidden">
				<div class="border-b px-3 py-2">
					<div class="flex items-center gap-2 rounded-md border bg-muted/30 px-2 py-1.5 text-sm">
						<SearchIcon class="size-3.5 shrink-0 text-muted-foreground" />
						<input type="text" placeholder={t('Cari sesi...')} bind:value={searchQuery}
							class="w-full bg-transparent outline-none placeholder:text-muted-foreground" />
						{#if searchQuery}
							<button onclick={() => (searchQuery = '')} class="shrink-0 text-muted-foreground hover:text-foreground"><XIcon class="size-3" /></button>
						{/if}
					</div>
				</div>

				<!-- List -->
				<div class="flex-1 overflow-y-auto p-2">
					{#if loading}
						<div class="space-y-2 p-2">{#each [1, 2, 3, 4, 5] as _}<div class="h-16 animate-pulse rounded-lg bg-muted/50"></div>{/each}</div>
					{:else if filteredSessions.length === 0}
						<p class="p-4 text-center text-xs text-muted-foreground">{searchQuery ? t('Tidak ada sesi ditemukan.') : t('Belum ada sesi. Buat sesi baru untuk mulai.')}</p>
					{:else}
						{#if groupedSessions.active.length > 0}
							<div class="px-2 pb-1 pt-2 text-[10px] font-bold uppercase tracking-wide text-muted-foreground/60">{t('Percakapan')}</div>
							{#each groupedSessions.active as session (session.id)}
								<div
									class="group mb-1 flex items-start gap-1 rounded-lg border p-2.5 text-left text-xs transition-colors {session.id === activeId ? 'border-ring bg-accent' : 'border-transparent hover:border-border hover:bg-accent/40'}"
								>
									<button class="min-w-0 flex-1 text-left" onclick={() => switchSession(session.id)}>
										<strong class="block truncate text-sm font-bold">{session.title || t('Percakapan baru')}</strong>
										<small class="text-muted-foreground">{session.messageCount ?? session.messages.length} {t('pesan')}</small>
									</button>
									<div class="flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
										<button class="rounded p-1 text-muted-foreground/50 hover:bg-accent hover:text-foreground" onclick={() => openRename(session)} title={t('Ganti nama')}><PencilIcon class="size-3" /></button>
										<button class="rounded p-1 text-muted-foreground/50 hover:bg-destructive/10 hover:text-destructive" onclick={() => openDelete(session)} title={t('Hapus')}><Trash2Icon class="size-3" /></button>
									</div>
								</div>
							{/each}
						{/if}
						{#if groupedSessions.empty.length > 0}
							<div class="px-2 pb-1 pt-2 text-[10px] font-bold uppercase tracking-wide text-muted-foreground/60">{t('Baru / Kosong')}</div>
							{#each groupedSessions.empty as session (session.id)}
								<div
									class="group mb-1 flex items-start gap-1 rounded-lg border p-2.5 text-left text-xs transition-colors {session.id === activeId ? 'border-ring bg-accent' : 'border-transparent hover:border-border hover:bg-accent/40'}"
								>
									<button class="min-w-0 flex-1 text-left" onclick={() => switchSession(session.id)}>
										<strong class="block truncate text-sm font-bold">{session.title || t('Percakapan baru')}</strong>
										<small class="text-muted-foreground">{session.messageCount ?? session.messages.length} {t('pesan')}</small>
									</button>
									<div class="flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
										<button class="rounded p-1 text-muted-foreground/50 hover:bg-accent hover:text-foreground" onclick={() => openRename(session)} title={t('Ganti nama')}><PencilIcon class="size-3" /></button>
										<button class="rounded p-1 text-muted-foreground/50 hover:bg-destructive/10 hover:text-destructive" onclick={() => openDelete(session)} title={t('Hapus')}><Trash2Icon class="size-3" /></button>
									</div>
								</div>
							{/each}
						{/if}
						{#if sessionTotalPages > 1}
							<div class="flex items-center justify-between gap-2 border-t px-1 pt-2">
								<button
									class="rounded-md px-2 py-1 text-xs font-bold text-muted-foreground hover:bg-accent disabled:opacity-40"
									disabled={sessionPage <= 1}
									onclick={() => (sessionPage--)}
								>
									{t('Sebelumnya')}
								</button>
								<span class="text-[11px] text-muted-foreground">{sessionPage} / {sessionTotalPages}</span>
								<button
									class="rounded-md px-2 py-1 text-xs font-bold text-muted-foreground hover:bg-accent disabled:opacity-40"
									disabled={sessionPage >= sessionTotalPages}
									onclick={() => (sessionPage++)}
								>
									{t('Selanjutnya')}
								</button>
							</div>
						{/if}
					{/if}
				</div>
			</div>
		</aside>

		<!-- Collapse toggle (desktop) -->
		<button
			class="hidden lg:flex absolute left-0 top-1/2 z-20 -translate-y-1/2 items-center justify-center rounded-r-md border border-l-0 bg-card p-1 text-muted-foreground shadow-sm hover:bg-accent hover:text-foreground transition-all"
			style="left: {sidebarOpen ? '288px' : '0'}"
			onclick={() => (sidebarOpen = !sidebarOpen)}
			title={sidebarOpen ? t('Tutup sidebar') : t('Buka sidebar')}
		>
			<ChevronLeftIcon class="size-4 transition-transform {sidebarOpen ? '' : 'rotate-180'}" />
		</button>

		<!-- Main chat area -->
		<div class="flex flex-1 flex-col overflow-hidden">
			<!-- Header -->
			<div class="flex items-center justify-between gap-3 border-b px-3 py-2.5 md:px-4">
				<div class="flex items-center gap-2 min-w-0">
					<Button variant="ghost" size="sm" onclick={() => (sidebarOpen = true)} class="-ml-1.5 h-8 w-8 shrink-0 p-0 lg:hidden" title={t('Buka sesi')}>
						<PanelRightOpenIcon class="size-4" />
					</Button>
					<div class="min-w-0">
						<h3 class="truncate text-base font-bold">{active?.title ?? 'Copilot'}</h3>
						<small class="hidden text-xs text-muted-foreground sm:block">{t('Asisten AI ekspor-impor')}</small>
					</div>
				</div>
				<div class="flex items-center gap-2 shrink-0">
					<Badge variant="secondary" class="hidden sm:inline-flex"><BotIcon class="mr-1 size-3" />{t('AI')}</Badge>
					<Button variant="ghost" size="sm" onclick={newSession} class="h-8 w-8 p-0" title={t('Sesi baru')}><MessageSquarePlusIcon class="size-4" /></Button>
				</div>
			</div>

			<!-- Messages -->
			<div bind:this={messagesEl} class="flex-1 space-y-4 overflow-y-auto overscroll-contain px-3 py-4 md:px-4">
				{#if !active}
					<div class="mx-auto mt-12 grid max-w-md gap-3 text-center">
						<BotIcon class="mx-auto size-12 text-muted-foreground/30" />
						<h4 class="text-lg font-bold">{t('Mulai percakapan dengan Copilot')}</h4>
						<p class="text-sm text-muted-foreground">{t('Pilih sesi atau buat sesi baru untuk memulai.')}</p>
						{#each suggestions as suggestion}
							<button class="rounded-lg border bg-muted/30 p-3 text-left text-sm transition-colors hover:bg-muted/60"
								onclick={() => { newSession().then(() => setTimeout(() => send(suggestion.question), 300)); }}>
								{suggestion.question}
							</button>
						{/each}
					</div>
				{:else}
					{#each active.messages as message, msgIdx (msgIdx)}
						<div class="flex items-start gap-2 {isUser(message.role) ? 'flex-row-reverse' : ''}">
							<div class="shrink-0 rounded-full border bg-muted p-1.5 {isUser(message.role) ? 'bg-primary text-primary-foreground border-primary' : ''}">
								{#if isUser(message.role)}<UserIcon class="size-4" />{:else}<BotIcon class="size-4" />{/if}
							</div>
							<div class="max-w-[92%] space-y-1 md:max-w-[75%]">
								<div class="flex items-center gap-2">
									<span class="text-xs font-bold text-muted-foreground">{isUser(message.role) ? t('Anda') : t('Asisten')}</span>
									{#if !isUser(message.role)}
										<button onclick={() => copyText(message.text, msgIdx)} class="text-muted-foreground/50 hover:text-foreground transition-colors" title={t('Salin')}>
											{#if copiedId === `copy-${msgIdx}`}
												<CheckIcon class="size-3 text-emerald-500" />
											{:else}
												<CopyIcon class="size-3" />
											{/if}
										</button>
									{/if}
								</div>
								<div class="rounded-xl border px-4 py-2.5 {isUser(message.role) ? 'bg-primary text-primary-foreground' : 'bg-muted/40'}">
									{#if isUser(message.role)}
										<p class="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
									{:else}
										{#if typingMessageId === `ai-${msgIdx}`}
											<TypewriterText text={message.text} speed={20} />
										{:else}
											<MarkdownRenderer text={message.text} />
										{/if}
									{/if}
								</div>
							</div>
						</div>
					{/each}
				{/if}

				{#if sending}
					<ThinkingIndicator />
				{/if}
			</div>

			<!-- Error -->
			{#if error}
				<div class="mx-3 mb-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm font-bold text-destructive md:mx-4">{error}</div>
			{/if}

			<!-- Input -->
			<form class="flex items-end gap-2 border-t bg-card px-3 py-3 md:px-4" onsubmit={(e) => { e.preventDefault(); send(); }}>
				<Input bind:value={input} placeholder={t('Tanya tentang kepatuhan, freight, pricing...')}
					class="min-h-[44px] flex-1 resize-none text-sm" disabled={!active} onkeydown={handleKeydown} />
				<Button type="submit" disabled={sending || !active || !input.trim()} class="h-[44px] w-[44px] shrink-0 p-0" title={t('Kirim')}>
					{#if sending}
						<span class="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
					{:else}
						<SendHorizonalIcon class="size-5" />
					{/if}
				</Button>
			</form>
		</div>
	</div>
</AppShell>

<!-- Rename Dialog -->
{#if renameDialogOpen}
	<Dialog.Root bind:open={renameDialogOpen} onOpenChange={(o) => { if (!o) { renameDialogOpen = false; renameTarget = null; } }}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Ganti nama sesi')}</Dialog.Title>
				<Dialog.Description>{t('Masukkan nama baru untuk sesi chat ini.')}</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-4 py-4">
				<Input bind:value={renameTitle} placeholder={t('Nama sesi...')} onkeydown={(e) => { if (e.key === 'Enter') confirmRename(); }} />
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => { renameDialogOpen = false; renameTarget = null; }}>{t('Batal')}</Button>
				<Button disabled={!renameTitle.trim()} onclick={confirmRename}>{t('Simpan')}</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Delete Dialog -->
{#if deleteDialogOpen}
	<Dialog.Root bind:open={deleteDialogOpen} onOpenChange={(o) => { if (!o) { deleteDialogOpen = false; deleteTarget = null; } }}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Hapus sesi')}</Dialog.Title>
				<Dialog.Description>{t('Apakah Anda yakin ingin menghapus sesi "')}{deleteTarget?.title ?? ''}{t('"? Semua pesan akan hilang.')}</Dialog.Description>
			</Dialog.Header>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => { deleteDialogOpen = false; deleteTarget = null; }}>{t('Batal')}</Button>
				<Button variant="destructive" onclick={confirmDelete}>{t('Hapus')}</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}
