import { apiFetch } from '$lib/api/client';

export type ChatSession = {
	id: string;
	title: string;
	messages: { role: string; text: string }[];
	messageCount?: number;
	createdAt?: string;
	updatedAt?: string;
};

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

export function renameChatSession(id: string, title: string) {
	return apiFetch<ChatSession>(`/chat/sessions/${id}/`, {
		method: 'PUT',
		body: JSON.stringify({ title })
	});
}

export type AiStatus = {
	mode: string;
	configured: boolean;
	health: string;
	circuit_breaker?: string;
	consecutive_failures?: number;
	endpoint?: string;
	model?: string;
};

export function getAiStatus() {
	return apiFetch<AiStatus>('/ai/status/');
}

export function sendSessionMessage(id: string, text: string, page_context?: string) {
	return apiFetch<ChatSession>(`/chat/sessions/${id}/messages/`, {
		method: 'POST',
		body: JSON.stringify({ text, page_context })
	});
}

export function getChatSuggestions() {
	return apiFetch<{ question: string; context?: string }[]>('/chat/suggestions/');
}
