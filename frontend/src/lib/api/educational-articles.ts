import { apiFetch } from '$lib/api/client';
import type { EducationalArticle } from '$lib/data/trade';

export function listEducationalArticles() { return apiFetch<EducationalArticle[]>('/educational/articles/'); }
export function publishEducationalArticle(id: string) { return apiFetch<EducationalArticle>(`/educational/articles/${id}/publish/`, { method: 'POST' }); }