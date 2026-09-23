import { apiFetch } from '$lib/api/client';
import type { KnowledgeArticle } from '$lib/data/trade';

export function listKnowledgeArticles() {
	return apiFetch<KnowledgeArticle[]>('/knowledge/');
}

export function publishKnowledgeArticle(id: string) {
	return apiFetch<KnowledgeArticle>(`/knowledge/${id}/publish/`, { method: 'POST' });
}
