import { apiFetch } from '$lib/api/client';
import type { AnalyticsMetric } from '$lib/data/trade';

export interface AnalyticsLane {
	label: string;
	readiness: number;
	risk: string;
	href: string;
	stage?: string;
}

export function getAnalyticsOverview() {
	return apiFetch<AnalyticsMetric[]>('/analytics/overview/');
}

export function getAnalyticsLanes() {
	return apiFetch<AnalyticsLane[]>('/analytics/lanes/');
}

export function refreshAnalytics() {
	return apiFetch<AnalyticsMetric[]>('/analytics/refresh/', { method: 'POST' });
}
