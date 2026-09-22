import { apiFetch } from '$lib/api/client';
import type { KnowledgeArticle } from '$lib/data/trade';

export type KnowledgePayload = {
	title: string;
	category?: string;
	summary?: string;
	steps?: string[];
	readTime?: string;
	status?: string;
};

export function listKnowledgeArticles() {
	return apiFetch<KnowledgeArticle[]>('/knowledge/');
}

export function getKnowledgeArticle(id: string) {
	return apiFetch<KnowledgeArticle>(`/knowledge/${id}/`);
}

export function createKnowledgeArticle(payload: KnowledgePayload) {
	return apiFetch<KnowledgeArticle>('/knowledge/', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateKnowledgeArticle(id: string, payload: Partial<KnowledgePayload>) {
	return apiFetch<KnowledgeArticle>(`/knowledge/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteKnowledgeArticle(id: string) {
	return apiFetch<{ status: string; id: string }>(`/knowledge/${id}/`, { method: 'DELETE' });
}

export function publishKnowledgeArticle(id: string) {
	return apiFetch<KnowledgeArticle>(`/knowledge/${id}/publish/`, { method: 'POST' });
}
