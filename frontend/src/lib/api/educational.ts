import { apiFetch } from '$lib/api/client';
import type { EducationalModule } from '$lib/data/trade';

export function listEducationalModules() { return apiFetch<EducationalModule[]>('/educational/'); }
export function publishEducationalModule(id: string) { return apiFetch<EducationalModule>(`/educational/${id}/publish/`, { method: 'POST' }); }
