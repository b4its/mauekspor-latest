<script lang="ts">
	import { tick } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card } from '$lib/components/ui/card/index.js';
	import {
		listChatSessions,
		createChatSession,
		deleteChatSession,
		sendSessionMessage,
		getChatSuggestions,
		getChatSession
	} from '$lib/api/chat';
	import type { ChatSession } from '$lib/api/chat';
	import { t } from '$lib/i18n.svelte';

	import PanelRightOpenIcon from '@lucide/svelte/icons/panel-right-open';
	import PanelRightCloseIcon from '@lucide/svelte/icons/panel-right-close';
	import MessageSquarePlusIcon from '@lucide/svelte/icons/message-square-plus';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import SendHorizonalIcon from '@lucide/svelte/icons/send-horizonal';
	import BotIcon from '@lucide/svelte/icons/bot';
	import UserIcon from '@lucide/svelte/icons/user';

	let sessions = $state<ChatSession[]>([]);
	let activeId = $state('');
	let input = $state('');
	let sending = $state(false);
	let loading = $state(true);
	let error = $state('');
	let suggestions = $state<{ question: string; context?: string }[]>([]);
	let sidebarOpen = $state(true);
	let messagesEl = $state<HTMLDivElement | null>(null);

	async function loadSessions() {
		try {
			sessions = (await listChatSessions()).data;
			if (!activeId && sessions.length > 0) activeId = sessions[0].id;
		} catch {
			error = t('Tidak dapat memuat sesi chat dari server.');
		} finally {
			loading = false;
		}
	}

	async function loadSuggestions() {
		try {
			suggestions = (await getChatSuggestions()).data;
		} catch {
			suggestions = [];
		}
	}

	$effect(() => {
		loadSessions();
		loadSuggestions();
	});

	// Auto-scroll ke bawah saat messages berubah
	$effect(() => {
		const msgs = active?.messages ?? [];
		if (msgs.length && messagesEl) {
			tick().then(() => {
				if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
			});
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
			// Tutup sidebar di mobile setelah pilih sesi
			sidebarOpen = false;
		} catch {
			error = t('Tidak dapat memuat sesi.');
		}
	}

	function roleLabel(role: string) {
		const r = role.toLowerCase();
		return r === 'user' ? t('Anda') : t('Asisten');
	}

	function isUser(role: string) {
		return role.toLowerCase() === 'user';
	}

	async function newSession() {
		error = '';
		try {
			const session = (await createChatSession('')).data;
			sessions = [session, ...sessions];
			activeId = session.id;
			sidebarOpen = false; // buka chat baru di mobile
		} catch {
			error = t('Gagal membuat sesi baru.');
		}
	}

	async function removeSession(id: string) {
		if (!confirm(t('Hapus sesi ini?'))) return;
		try {
			await deleteChatSession(id);
			sessions = sessions.filter((s) => s.id !== id);
			if (activeId === id) activeId = sessions[0]?.id ?? '';
		} catch {
			error = t('Gagal menghapus sesi.');
		}
	}

	async function send(textOverride?: string) {
		const text = (textOverride ?? input).trim();
		if (!text || sending || !active) return;
		error = '';
		sending = true;
		try {
			const updated = (await sendSessionMessage(active.id, text)).data;
			const idx = sessions.findIndex((s) => s.id === active.id);
			if (idx >= 0) sessions[idx] = updated;
			activeId = updated.id;
		} catch {
			error = t('Gagal mengirim pesan.');
		} finally {
			sending = false;
			input = '';
		}
	}
</script>

<svelte:head>
	<title>{t('Chat')} | MauEkspor</title>
</svelte:head>

<AppShell title="Chat" eyebrow={t('Asisten dagang AI')}>
	<div class="relative flex h-[calc(100dvh-9rem)] min-h-[400px] overflow-hidden rounded-xl border bg-card shadow-sm md:h-[calc(100dvh-10rem)]">
		<!-- Sidebar overlay (mobile) -->
		{#if sidebarOpen}
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div class="fixed inset-0 z-40 bg-black/30 md:hidden" role="presentation" onclick={() => (sidebarOpen = false)}></div>
		{/if}

		<!-- Sidebar -->
		<aside
			class="absolute inset-y-0 left-0 z-50 flex w-72 flex-col border-r bg-muted/30 transition-transform duration-200 md:relative md:w-72 md:translate-x-0 {sidebarOpen ? 'translate-x-0' : '-translate-x-full'}">
			<div class="flex items-center justify-between gap-2 border-b p-3">
				<h3 class="text-sm font-bold tracking-tight">{t('Riwayat Sesi')}</h3>
				<div class="flex items-center gap-1">
					<Button variant="ghost" size="sm" onclick={newSession} title={t('Sesi baru')}>
						<MessageSquarePlusIcon class="size-4" />
					</Button>
					<Button variant="ghost" size="sm" onclick={() => (sidebarOpen = false)} class="md:hidden" title={t('Tutup')}>
						<PanelRightCloseIcon class="size-4" />
					</Button>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto p-2">
				{#if loading}
					<p class="p-3 text-xs font-semibold text-muted-foreground">{t('Memuat sesi...')}</p>
				{/if}
				{#each sessions as session}
					<div class="group mb-1 flex items-start gap-1 rounded-lg border p-2.5 text-left text-xs transition-colors hover:border-border hover:bg-accent/50 {session.id === activeId ? 'border-ring bg-accent' : 'border-transparent'}"
					>
						<button
							class="flex-1 text-left"
							onclick={() => switchSession(session.id)}
						>
							<strong class="block truncate text-sm font-bold">{session.title}</strong>
							<small class="text-muted-foreground">{session.messageCount ?? session.messages.length} {t('pesan')}</small>
						</button>
						<button
							class="shrink-0 rounded p-1 opacity-0 text-muted-foreground/50 transition-opacity hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100 focus-visible:opacity-100"
							onclick={() => removeSession(session.id)}
							title={t('Hapus')}
						>
							<Trash2Icon class="size-3" />
						</button>
					</div>
				{/each}
				{#if !loading && sessions.length === 0}
					<p class="p-3 text-xs font-semibold text-muted-foreground">{t('Belum ada sesi. Buat sesi baru untuk mulai.')}</p>
				{/if}
			</div>
		</aside>

		<!-- Main chat area -->
		<div class="flex flex-1 flex-col overflow-hidden">
			<!-- Header -->
			<div class="flex items-center justify-between gap-3 border-b px-4 py-3">
				<div class="flex items-center gap-2 min-w-0">
					<Button variant="ghost" size="sm" onclick={() => (sidebarOpen = true)} class="-ml-1 shrink-0 md:hidden" title={t('Buka sesi')}>
						<PanelRightOpenIcon class="size-4" />
					</Button>
					<div class="min-w-0">
						<h3 class="truncate text-base font-bold">{active?.title ?? 'Copilot'}</h3>
						<small class="hidden text-xs text-muted-foreground md:block">{t('Asisten AI ekspor-impor')}</small>
					</div>
				</div>
				<div class="flex items-center gap-2 shrink-0">
					<Badge variant="secondary" class="hidden md:inline-flex">
						<BotIcon class="mr-1 size-3" />
						{t('AI')}
					</Badge>
					<Button variant="ghost" size="sm" onclick={newSession} title={t('Sesi baru')} class="hidden md:inline-flex">
						<MessageSquarePlusIcon class="size-4" />
					</Button>
				</div>
			</div>

			<!-- Messages area -->
			<div
				bind:this={messagesEl}
				class="flex-1 space-y-3 overflow-y-auto px-4 py-4"
			>
				{#if !active}
					<div class="mx-auto mt-12 grid max-w-md gap-3 text-center">
						<BotIcon class="mx-auto size-12 text-muted-foreground/30" />
						<h4 class="text-lg font-bold">{t('Mulai percakapan dengan Copilot')}</h4>
						<p class="text-sm text-muted-foreground">{t('Pilih sesi atau buat sesi baru untuk memulai.')}</p>
						{#each suggestions as suggestion}
							<button
								class="rounded-lg border bg-muted/30 p-3 text-left text-sm transition-colors hover:bg-muted/60"
								onclick={() => {
									newSession().then(() => setTimeout(() => send(suggestion.question), 300));
								}}
							>
								{suggestion.question}
							</button>
						{/each}
					</div>
				{:else}
					{#each active.messages as message}
						<div class="flex items-start gap-2 {isUser(message.role) ? 'flex-row-reverse' : ''}">
							<div class="shrink-0 rounded-full border bg-muted p-1.5 {isUser(message.role) ? 'bg-primary text-primary-foreground' : ''}">
								{#if isUser(message.role)}
									<UserIcon class="size-4" />
								{:else}
									<BotIcon class="size-4" />
								{/if}
							</div>
							<div class="max-w-[85%] space-y-1 md:max-w-[70%]">
								<span class="text-xs font-bold text-muted-foreground">{roleLabel(message.role)}</span>
								<p
									class="rounded-xl border px-4 py-2.5 text-sm leading-relaxed {isUser(message.role) ? 'bg-primary text-primary-foreground' : 'bg-muted/50'}"
								>
									{message.text}
								</p>
							</div>
						</div>
					{/each}
				{/if}

				{#if sending}
					<div class="flex items-start gap-2">
						<div class="shrink-0 rounded-full border bg-muted p-1.5">
							<BotIcon class="size-4" />
						</div>
						<div class="max-w-[70%] space-y-1">
							<span class="text-xs font-bold text-muted-foreground">{t('Asisten')}</span>
							<div class="rounded-xl border bg-muted/50 px-4 py-3">
								<span class="inline-flex gap-1">
									<span class="size-1.5 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:0ms]"></span>
									<span class="size-1.5 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:150ms]"></span>
									<span class="size-1.5 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:300ms]"></span>
								</span>
							</div>
						</div>
					</div>
				{/if}
			</div>

			<!-- Error toast -->
			{#if error}
				<div class="mx-4 mb-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm font-bold text-destructive">
					{error}
				</div>
			{/if}

			<!-- Input form (sticky bottom) -->
			<form
				class="flex items-end gap-2 border-t bg-card px-4 py-3"
				onsubmit={(event) => { event.preventDefault(); send(); }}
			>
				<Input
					bind:value={input}
					placeholder={t('Tanya tentang kepatuhan, freight, pricing...')}
					class="min-h-[44px] flex-1 resize-none"
					disabled={!active}
				/>
				<Button
					type="submit"
					disabled={sending || !active || !input.trim()}
					class="h-[44px] w-[44px] shrink-0 p-0"
					title={t('Kirim')}
				>
					{#if sending}
						<span class="loading-spinner size-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
					{:else}
						<SendHorizonalIcon class="size-5" />
					{/if}
				</Button>
			</form>
		</div>
	</div>
</AppShell>
