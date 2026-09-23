import { apiFetch } from '$lib/api/client';
import type { ChatConversation } from '$lib/data/trade';

export type ChatSession = {
	id: string;
	title: string;
	messages: { role: string; text: string }[];
	messageCount?: number;
	createdAt?: string;
	updatedAt?: string;
};

export function listChatConversations() {
	return apiFetch<ChatConversation[]>('/chat/');
}

export function sendChatMessage(id: string, text: string) {
	return apiFetch<ChatConversation>(`/chat/${id}/messages/`, {
		method: 'POST',
		body: JSON.stringify({ text })
	});
}

// ---------- Chat sessions (AI Copilot) ----------
export function listChatSessions() {
	return apiFetch<ChatSession[]>('/chat/sessions/');
}

export function getChatSession(id: string) {
	return apiFetch<ChatSession>(`/chat/sessions/${id}/`);
}

export function createChatSession(title = '') {
	return apiFetch<ChatSession>('/chat/sessions/', {
		method: 'POST',
		body: JSON.stringify({ title })
	});
}

export function deleteChatSession(id: string) {
	return apiFetch<{ status: string }>(`/chat/sessions/${id}/`, { method: 'DELETE' });
}

export function sendSessionMessage(id: string, text: string) {
	return apiFetch<ChatSession>(`/chat/sessions/${id}/messages/`, {
		method: 'POST',
		body: JSON.stringify({ text })
	});
}

export function getChatSuggestions() {
	return apiFetch<{ question: string; context?: string }[]>('/chat/suggestions/');
}
