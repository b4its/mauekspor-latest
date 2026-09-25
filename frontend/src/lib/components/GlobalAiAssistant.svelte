<script lang="ts">
	import { tick } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { MarkdownRenderer } from '$lib/components/MarkdownRenderer';
	import ThinkingIndicator from '$lib/components/ThinkingIndicator.svelte';
	import { t } from '$lib/i18n.svelte';
	import { getUser, getStatus } from '$lib/stores/session.svelte';
	import {
		isAiAssistantOpen,
		closeAiAssistant,
		toggleAiAssistant,
		openAiAssistant,
		consumePendingPrompt,
		getPromptsForPath
	} from '$lib/stores/aiAssistant.svelte';
	import {
		listChatSessions,
		createChatSession,
		getChatSession,
		sendSessionMessage,
		getAiStatus,
		type ChatSession,
		type AiStatus
	} from '$lib/api/chat';

	import BotIcon from '@lucide/svelte/icons/bot';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import SendHorizonalIcon from '@lucide/svelte/icons/send-horizonal';
	import XIcon from '@lucide/svelte/icons/x';
	import MessageSquarePlusIcon from '@lucide/svelte/icons/message-square-plus';
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
	import CopyIcon from '@lucide/svelte/icons/copy';
	import CheckIcon from '@lucide/svelte/icons/check';
	import UserIcon from '@lucide/svelte/icons/user';
	import CompassIcon from '@lucide/svelte/icons/compass';

	let open = $derived(isAiAssistantOpen());
	let pathname = $derived(page.url.pathname);
	let promptContext = $derived(getPromptsForPath(pathname));

	let sessions = $state<ChatSession[]>([]);
	let activeSession = $state<ChatSession | null>(null);
	let input = $state('');
	let sending = $state(false);
	let loading = $state(false);
	let error = $state('');
	let copiedIdx = $state<number | null>(null);
	let aiStatus = $state<AiStatus | null>(null);
	let messagesContainer = $state<HTMLDivElement | null>(null);

	// Load AI status on mount
	$effect(() => {
		getAiStatus()
			.then((res) => {
				aiStatus = res.data;
			})
			.catch(() => {
				aiStatus = null;
			});
	});

	// Auto scroll to bottom of chat
	$effect(() => {
		const msgs = activeSession?.messages ?? [];
		if (msgs.length && messagesContainer) {
			tick().then(() => {
				if (messagesContainer) {
					messagesContainer.scrollTop = messagesContainer.scrollHeight;
				}
			});
		}
	});

	// Watch when open becomes true: ensure we have an active session
	$effect(() => {
		if (open) {
			const pending = consumePendingPrompt();
			if (!activeSession) {
				initSession().then(() => {
					if (pending) send(pending);
				});
			} else if (pending) {
				send(pending);
			}
		}
	});

	async function initSession() {
		loading = true;
		error = '';
		try {
			const res = await listChatSessions();
			sessions = res.data;
			if (sessions.length > 0) {
				activeSession = (await getChatSession(sessions[0].id)).data;
			} else {
				const created = await createChatSession('Konsultasi Cepat AI');
				activeSession = created.data;
				sessions = [created.data];
			}
		} catch (err: any) {
			// If unauthenticated or failure, create in-memory temporary session
			activeSession = {
				id: 'local-session',
				title: 'Asisten Ekspor',
				messages: []
			};
		} finally {
			loading = false;
		}
	}

	async function handleNewSession() {
		error = '';
		loading = true;
		try {
			const created = await createChatSession('Sesi Baru');
			activeSession = created.data;
			sessions = [created.data, ...sessions];
		} catch {
			activeSession = {
				id: `local-${Date.now()}`,
				title: 'Sesi Baru',
				messages: []
			};
		} finally {
			loading = false;
		}
	}

	async function send(textOverride?: string) {
		const text = (textOverride ?? input).trim();
		if (!text || sending) return;
		input = '';
		error = '';

		// If no active session yet, init one
		if (!activeSession) {
			await initSession();
		}

		// Optimistic user message
		const userMsg = { role: 'user', text };
		if (activeSession) {
			activeSession.messages = [...(activeSession.messages ?? []), userMsg];
		}

		sending = true;
		try {
			if (activeSession && activeSession.id && !activeSession.id.startsWith('local-')) {
				const updated = await sendSessionMessage(activeSession.id, text, pathname);
				activeSession = updated.data;
			} else {
				// Fallback if local session without DB ID: create real session first then send
				const created = await createChatSession(text.slice(0, 35));
				activeSession = created.data;
				sessions = [created.data, ...sessions];
				activeSession.messages = [userMsg];
				const updated = await sendSessionMessage(created.data.id, text, pathname);
				activeSession = updated.data;
			}
		} catch (err: any) {
			error = t('Gagal mengirim pesan ke asisten AI. Periksa koneksi backend.');
		} finally {
			sending = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			send();
		} else if (e.key === 'Escape' && open) {
			closeAiAssistant();
		}
	}

	async function copyMessage(text: string, idx: number) {
		try {
			await navigator.clipboard.writeText(text);
			copiedIdx = idx;
			setTimeout(() => {
				copiedIdx = null;
			}, 2000);
		} catch {
			/* ignore */
		}
	}

	function openFullChat() {
		closeAiAssistant();
		goto('/chat');
	}
</script>

<svelte:window onkeydown={(e) => {
	// Ctrl + / or Cmd + / to toggle AI assistant
	if ((e.metaKey || e.ctrlKey) && e.key === '/') {
		e.preventDefault();
		toggleAiAssistant();
	}
}} />

<!-- ─── Floating Trigger Button (Bottom-Right) ────────────────────────── -->
{#if !open}
	<div aria-label="Asisten AI">
		<button
			type="button"
			onclick={() => toggleAiAssistant()}
			class="group fixed bottom-5 right-5 z-40 flex items-center gap-2 rounded-full border border-primary/30 bg-gradient-to-r from-[#0b3d91] via-[#1552b7] to-[#1e63d6] px-4 py-3 text-white shadow-xl backdrop-blur-md transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/50 cursor-pointer sm:bottom-6 sm:right-6"
			title={t('Tanya Asisten AI (Ctrl + /)')}
			aria-label={t('Buka Asisten AI MauEkspor')}
		>
			<span class="relative flex size-3">
				<span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
				<span class="relative inline-flex size-3 rounded-full bg-emerald-500"></span>
			</span>
			<SparklesIcon class="size-4 animate-pulse text-amber-300" />
			<span class="font-display text-sm font-bold tracking-wide">
				{t('Tanya AI')}
			</span>
			<kbd class="hidden rounded bg-white/20 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-white/90 sm:inline-block">
				⌘/
			</kbd>
		</button>
	</div>
{/if}

<!-- ─── Slide-over Drawer / Sheet Panel ───────────────────────────────── -->
{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs transition-opacity"
		onclick={closeAiAssistant}
		role="presentation"
	></div>

	<!-- Drawer Container -->
	<div
		class="fixed inset-y-0 right-0 z-50 flex w-full max-w-[440px] flex-col border-l border-border bg-background shadow-2xl transition-transform duration-300 sm:w-[440px]"
		role="dialog"
		aria-modal="true"
		aria-label={t('Asisten AI MauEkspor')}
	>
		<!-- Header -->
		<div class="flex items-center justify-between border-b border-border bg-card/60 px-4 py-3 backdrop-blur-md">
			<div class="flex items-center gap-2.5">
				<div class="flex size-9 items-center justify-center rounded-xl bg-gradient-to-tr from-[#0b3d91] to-[#1e63d6] text-white shadow-sm">
					<BotIcon class="size-5" />
				</div>
				<div>
					<div class="flex items-center gap-1.5">
						<h3 class="font-display text-sm font-black tracking-tight text-foreground">
							{t('MauEkspor AI')}
						</h3>
						<Badge variant="outline" class="h-4 border-emerald-500/30 bg-emerald-500/10 px-1 text-[10px] font-semibold text-emerald-600 dark:text-emerald-400">
							<span class="mr-1 inline-block size-1.5 rounded-full bg-emerald-500"></span>
							{aiStatus?.model ? 'DeepSeek' : 'Online'}
						</Badge>
					</div>
					<p class="text-[11px] text-muted-foreground">
						{t('Asisten Ekspor & Workspace Aktif')}
					</p>
				</div>
			</div>

			<div class="flex items-center gap-1">
				<Button
					variant="ghost"
					size="sm"
					class="size-8 p-0 text-muted-foreground hover:text-foreground"
					onclick={handleNewSession}
					title={t('Sesi Baru')}
				>
					<MessageSquarePlusIcon class="size-4" />
				</Button>
				<Button
					variant="ghost"
					size="sm"
					class="size-8 p-0 text-muted-foreground hover:text-foreground"
					onclick={openFullChat}
					title={t('Buka Layar Penuh')}
				>
					<ExternalLinkIcon class="size-4" />
				</Button>
				<Button
					variant="ghost"
					size="sm"
					class="size-8 p-0 text-muted-foreground hover:text-foreground"
					onclick={closeAiAssistant}
					title={t('Tutup (Esc)')}
				>
					<XIcon class="size-4" />
				</Button>
			</div>
		</div>

		<!-- Page Context Grounding Banner -->
		<div class="flex items-center justify-between border-b border-border/60 bg-muted/40 px-3.5 py-1.5 text-xs">
			<div class="flex items-center gap-1.5 truncate text-muted-foreground">
				<CompassIcon class="size-3.5 shrink-0 text-primary" />
				<span class="font-medium text-foreground">{promptContext.title}</span>
			</div>
			<span class="text-[10px] text-muted-foreground/75 truncate">
				{pathname}
			</span>
		</div>

		<!-- Messages Scroll Area -->
		<div bind:this={messagesContainer} class="flex-1 space-y-4 overflow-y-auto p-4">
			{#if loading && !activeSession}
				<div class="space-y-3 pt-6">
					<div class="h-14 animate-pulse rounded-lg bg-muted/60"></div>
					<div class="h-20 animate-pulse rounded-lg bg-muted/40"></div>
				</div>
			{:else if !activeSession || (activeSession.messages ?? []).length === 0}
				<!-- Empty state: welcome & contextual chips -->
				<div class="space-y-4 pt-2">
					<div class="rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/5 via-transparent to-primary/5 p-4 text-center">
						<div class="mx-auto mb-2.5 flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
							<SparklesIcon class="size-5" />
						</div>
						<h4 class="font-display text-base font-bold text-foreground">
							{t('Bagaimana saya bisa membantu?')}
						</h4>
						<p class="mt-1 text-xs text-muted-foreground leading-relaxed">
							{t('Saya terhubung langsung ke katalog produk, kepatuhan regulasi, dan proyek dagang workspace Anda.')}
						</p>
					</div>

					<div class="space-y-2">
						<span class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground/70">
							{t('Pertanyaan yang relevan:')}
						</span>
						<div class="flex flex-col gap-1.5">
							{#each promptContext.prompts as q}
								<button
									type="button"
									onclick={() => send(q)}
									class="rounded-xl border border-border bg-card/70 p-2.5 text-left text-xs font-medium text-foreground transition-all hover:border-primary/40 hover:bg-accent/60 cursor-pointer"
								>
									💡 {q}
								</button>
							{/each}
						</div>
					</div>
				</div>
			{:else}
				<!-- Message History -->
				{#each activeSession.messages as msg, idx (idx)}
					{@const isUser = msg.role.toLowerCase() === 'user'}
					<div class="flex items-start gap-2.5 {isUser ? 'flex-row-reverse' : ''}">
						<div class="shrink-0 rounded-full border p-1.5 {isUser ? 'border-primary bg-primary text-primary-foreground' : 'border-border bg-muted'}">
							{#if isUser}
								<UserIcon class="size-3.5" />
							{:else}
								<BotIcon class="size-3.5 text-primary" />
							{/if}
						</div>

						<div class="max-w-[85%] space-y-1">
							<div class="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground">
								<span>{isUser ? t('Anda') : 'MauEkspor AI'}</span>
								{#if !isUser}
									<button
										type="button"
										onclick={() => copyMessage(msg.text, idx)}
										class="p-0.5 text-muted-foreground/60 hover:text-foreground transition-colors cursor-pointer"
										title={t('Salin')}
									>
										{#if copiedIdx === idx}
											<CheckIcon class="size-3 text-emerald-500" />
										{:else}
											<CopyIcon class="size-3" />
										{/if}
									</button>
								{/if}
							</div>

							<div class="rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed {isUser ? 'rounded-tr-xs bg-primary text-primary-foreground' : 'rounded-tl-xs border border-border bg-card text-card-foreground shadow-xs'}">
								{#if isUser}
									<p class="whitespace-pre-wrap">{msg.text}</p>
								{:else}
									<MarkdownRenderer text={msg.text} />
								{/if}
							</div>
						</div>
					</div>
				{/each}

				{#if sending}
					<ThinkingIndicator />
				{/if}
			{/if}
		</div>

		<!-- Error Message if any -->
		{#if error}
			<div class="mx-3 mb-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-1.5 text-xs font-semibold text-destructive">
				{error}
			</div>
		{/if}

		<!-- Contextual Quick Chips Bar (shown when messages exist) -->
		{#if activeSession && (activeSession.messages ?? []).length > 0}
			<div class="flex gap-1.5 overflow-x-auto border-t border-border/50 bg-muted/20 px-3 py-2 no-scrollbar">
				{#each promptContext.prompts as q}
					<button
						type="button"
						onclick={() => send(q)}
						class="shrink-0 rounded-full border border-border bg-background px-2.5 py-1 text-[11px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground cursor-pointer"
					>
						{q}
					</button>
				{/each}
			</div>
		{/if}

		<!-- Input Footer -->
		<form
			class="border-t border-border bg-card p-3"
			onsubmit={(e) => {
				e.preventDefault();
				send();
			}}
		>
			<div class="relative flex items-center gap-1.5">
				<input
					type="text"
					bind:value={input}
					onkeydown={handleKeydown}
					placeholder={t('Tanya regulasi, HS code, costing, atau pasar...')}
					disabled={sending}
					class="h-10 flex-1 rounded-xl border border-input bg-background px-3.5 text-xs text-foreground placeholder:text-muted-foreground/70 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
				/>
				<Button
					type="submit"
					disabled={sending || !input.trim()}
					size="sm"
					class="h-10 w-10 shrink-0 rounded-xl p-0"
					title={t('Kirim (Enter)')}
				>
					{#if sending}
						<span class="size-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
					{:else}
						<SendHorizonalIcon class="size-4" />
					{/if}
				</Button>
			</div>
			<div class="mt-2 flex items-center justify-between px-1 text-[10px] text-muted-foreground/60">
				<span>{t('Didukung DeepSeek 4.1 Flash')}</span>
				<span>{t('Enter untuk kirim • Esc untuk tutup')}</span>
			</div>
		</form>
	</div>
{/if}

<style>
	/* Hide scrollbar for Chrome, Safari and Opera */
	.no-scrollbar::-webkit-scrollbar {
		display: none;
	}
	/* Hide scrollbar for IE, Edge and Firefox */
	.no-scrollbar {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
</style>
