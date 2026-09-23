<script lang="ts">
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
		getChatSuggestions
	} from '$lib/api/chat';
	import type { ChatSession } from '$lib/api/chat';
	import { t } from '$lib/i18n.svelte';

	let sessions = $state<ChatSession[]>([]);
	let activeId = $state('');
	let input = $state('');
	let sending = $state(false);
	let loading = $state(true);
	let error = $state('');
	let suggestions = $state<{ question: string; context?: string }[]>([]);

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

	let active = $derived(sessions.find((s) => s.id === activeId) ?? null);

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
	<Card class="grid overflow-hidden md:grid-cols-[300px_1fr]">
		<aside class="grid content-start gap-2 border-b bg-muted/30 p-5 md:border-b-0 md:border-r">
			<div class="flex items-center justify-between gap-2">
				<h3 class="text-lg font-bold tracking-tight">{t('Sesi')}</h3>
				<Button variant="outline" size="sm" onclick={newSession}>{t('+ Baru')}</Button>
			</div>
			{#if loading}
				<p class="text-xs font-semibold text-muted-foreground">{t('Memuat sesi...')}</p>
			{/if}
			{#each sessions as session}
				<div class={`grid gap-1 rounded-lg border p-3 transition-colors ${session.id === activeId ? 'border-ring bg-primary/10' : ''}`}>
					<button class="text-left" onclick={() => (activeId = session.id)}>
						<strong class="block text-sm font-bold">{session.title}</strong>
						<small class="text-xs text-muted-foreground">{session.messageCount ?? session.messages.length} {t('pesan')}</small>
					</button>
					<button class="w-fit text-xs font-bold text-muted-foreground hover:text-destructive" onclick={() => removeSession(session.id)}>
						{t('Hapus')}
					</button>
				</div>
			{/each}
			{#if !loading && sessions.length === 0}
				<p class="text-xs font-semibold text-muted-foreground">{t('Belum ada sesi. Buat sesi baru untuk mulai.')}</p>
			{/if}
		</aside>

		<div class="grid min-h-[600px] grid-rows-[auto_1fr_auto]">
			<div class="flex items-start justify-between gap-3 border-b p-5">
				<div>
					<h3 class="text-lg font-bold tracking-tight">{active?.title ?? 'Copilot'}</h3>
					<small class="block text-sm text-muted-foreground">{t('Asisten AI ekspor-impor')}</small>
				</div>
				<Badge variant="secondary">{t('Asisten AI')}</Badge>
			</div>

			<div class="grid content-start gap-3 overflow-y-auto p-5">
				{#if !active}
					<div class="mx-auto grid max-w-md gap-3 text-center">
						<h4 class="text-lg font-bold">{t('Mulai percakapan dengan Copilot')}</h4>
						{#each suggestions as suggestion}
							<button
								class="rounded-lg border bg-muted/30 p-3 text-left text-sm transition-colors hover:bg-muted/60"
								onclick={() => {
									newSession().then(() => setTimeout(() => send(suggestion.question), 100));
								}}
							>
								{suggestion.question}
							</button>
						{/each}
					</div>
				{/if}

				{#each active?.messages ?? [] as message}
					<div class="grid max-w-[75%] gap-1" class:ml-auto={isUser(message.role)}>
						<span class="text-xs font-bold text-muted-foreground">{roleLabel(message.role)}</span>
						<p
							class={`rounded-xl border p-3 text-sm leading-relaxed ${isUser(message.role) ? 'bg-primary text-primary-foreground' : 'bg-muted/40'}`}
						>
							{message.text}
						</p>
					</div>
				{/each}
			</div>

			{#if error}
				<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
			{/if}
			<form class="flex gap-2 border-t p-5" onsubmit={(event) => { event.preventDefault(); send(); }}>
				<Input bind:value={input} placeholder={t('Tanya tentang kepatuhan, freight, pricing...')} class="flex-1" disabled={!active} />
				<Button type="submit" disabled={sending || !active}>{sending ? t('Mengirim...') : t('Kirim')}</Button>
			</form>
		</div>
	</Card>
</AppShell>
