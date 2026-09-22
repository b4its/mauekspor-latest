import { apiFetch } from '$lib/api/client';
import type { TradeReport } from '$lib/data/trade';

export function listReports() {
	return apiFetch<TradeReport[]>('/reports/');
}

export function createReport(payload: { title: string; type?: string; period?: string; owner?: string }) {
	return apiFetch<TradeReport>('/reports/', { method: 'POST', body: JSON.stringify(payload) });
}

export function getReport(id: string) {
	return apiFetch<TradeReport>(`/reports/${id}/`);
}

export function generateReport(id: string) {
	return apiFetch<TradeReport>(`/reports/${id}/generate/`, { method: 'POST' });
}

export function scheduleReport(id: string) {
	return apiFetch<TradeReport>(`/reports/${id}/schedule/`, { method: 'POST' });
}

export function updateReport(id: string, payload: Partial<TradeReport>) {
	return apiFetch<TradeReport>(`/reports/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteReport(id: string) {
	return apiFetch<{ status: string; id: string }>(`/reports/${id}/`, { method: 'DELETE' });
}
