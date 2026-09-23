import { apiFetch } from '$lib/api/client';
import type { AnalyticsMetric } from '$lib/data/trade';

export function getAnalyticsOverview() {
	return apiFetch<AnalyticsMetric[]>('/analytics/overview/');
}

export function refreshAnalytics() {
	return apiFetch<AnalyticsMetric[]>('/analytics/refresh/', { method: 'POST' });
}
