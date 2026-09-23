<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card } from '$lib/components/ui/card/index.js';
	import { chatConversations as seedConversations } from '$lib/data/trade';
	import type { ChatConversation } from '$lib/data/trade';
	import { listChatConversations, sendChatMessage } from '$lib/api/chat';
	import { createRemoteList } from '$lib/api/remote-list.svelte';

	let activeId = $state(seedConversations[0].id);
	let input = $state('');
	let conversations = createRemoteList(listChatConversations, seedConversations);
	let sending = $state(false);
	let error = $state('');

	$effect(() => {
		conversations.load();
	});

	let active = $derived(conversations.items.find((c) => c.id === activeId) ?? conversations.items[0]);

	async function send() {
		const text = input.trim();
		if (!text || sending) return;
		error = '';
		sending = true;
		try {
			const thread = await sendChatMessage(active.id, text);
			active.messages = [...(thread.data.messages ?? active.messages)];
			if (thread.data.updatedAt) active.updatedAt = thread.data.updatedAt;
		} catch {
			error = 'Gagal mengirim pesan.';
		} finally {
			sending = false;
		}
		input = '';
	}
</script>

<svelte:head>
	<title>Chat | MauEkspor</title>
</svelte:head>

<AppShell title="Chat" eyebrow="Trade assistant">
	<Card class="grid overflow-hidden md:grid-cols-[300px_1fr]">
		<aside class="grid content-start gap-2 border-b bg-muted/30 p-5 md:border-b-0 md:border-r">
			<h3 class="text-lg font-bold tracking-tight">Conversations</h3>
			{#each conversations.items as conversation}
				<button
					class={`grid gap-1 rounded-lg border p-3 text-left transition-colors ${conversation.id === activeId ? 'border-ring bg-primary/10' : ''}`}
					onclick={() => (activeId = conversation.id)}
				>
					<strong class="text-sm font-bold">{conversation.title}</strong>
					<small class="text-xs text-muted-foreground">{conversation.updatedAt}</small>
				</button>
			{/each}
		</aside>

		<div class="grid min-h-[600px] grid-rows-[auto_1fr_auto]">
			<div class="flex items-start justify-between gap-3 border-b p-5">
				<div>
					<h3 class="text-lg font-bold tracking-tight">{active.title}</h3>
					<small class="block text-sm text-muted-foreground">{active.status} conversation</small>
				</div>
				<Badge variant="secondary">AI assistant</Badge>
			</div>

			<div class="grid content-start gap-3 overflow-y-auto p-5">
				{#each active.messages as message}
					<div class="grid max-w-[75%] gap-1" class:ml-auto={message.role === 'User'}>
						<span class="text-xs font-bold text-muted-foreground">{message.role === 'User' ? 'You' : 'Assistant'}</span>
						<p
							class={`rounded-xl border p-3 text-sm leading-relaxed ${message.role === 'User' ? 'bg-primary text-primary-foreground' : 'bg-muted/40'}`}
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
				<Input bind:value={input} placeholder="Ask about compliance, freight, pricing..." class="flex-1" />
				<Button type="submit" disabled={sending}>{sending ? 'Sending...' : 'Send'}</Button>
			</form>
		</div>
	</Card>
</AppShell>