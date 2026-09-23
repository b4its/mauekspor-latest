import { apiFetch } from '$lib/api/client';
import type { ChatConversation } from '$lib/data/trade';

export function listChatConversations() { return apiFetch<ChatConversation[]>('/chat/'); }
export function sendChatMessage(id: string, text: string) { return apiFetch<ChatConversation>(`/chat/${id}/messages/`, { method: 'POST', body: JSON.stringify({ text }) }); }
