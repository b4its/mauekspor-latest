import { apiFetch } from '$lib/api/client';
import type { ExportAnalysis } from '$lib/data/trade';

export function listExportAnalyses() { return apiFetch<ExportAnalysis[]>('/export-analysis/'); }
export function getExportAnalysis(id: string) { return apiFetch<ExportAnalysis>(`/export-analysis/${id}/`); }
export function createExportAnalysis(payload: { productId: string; destination: string }) { return apiFetch<ExportAnalysis>('/export-analysis/', { method: 'POST', body: JSON.stringify(payload) }); }
export function runRegulationCheck(id: string) { return apiFetch<ExportAnalysis>(`/export-analysis/${id}/regulation-recommendations/`, { method: 'POST' }); }