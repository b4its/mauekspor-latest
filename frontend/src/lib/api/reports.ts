import { apiFetch } from '$lib/api/client';
import type { TradeReport } from '$lib/data/trade';

export function listReports() {
	return apiFetch<TradeReport[]>('/reports/');
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
