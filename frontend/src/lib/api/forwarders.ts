import { apiFetch } from '$lib/api/client';
import type { Forwarder } from '$lib/data/trade';

export type ForwarderProfile = {
	id?: string;
	companyName: string;
	contactInfo?: Record<string, string>;
	specializationRoutes?: string[];
	serviceTypes?: string[];
	averageRating?: number;
	totalReviews?: number;
};

export type ForwarderReview = {
	id?: string;
	forwarderId?: string;
	rating: number;
	reviewText?: string;
	reviewerName?: string;
	createdAt?: string;
};

export type ForwarderStatistics = {
	totalReviews: number;
	averageRating: number;
	ratingDistribution: Record<string, number>;
	uniquePartnerships: number;
	recentReviews?: ForwarderReview[];
	trend30Days?: { label: string; count: number }[];
};

export function listForwarders() {
	return apiFetch<Forwarder[]>('/forwarders/');
}

export function getForwarder(id: string) {
	return apiFetch<Forwarder>(`/forwarders/${id}/`);
}

export function requestForwarderQuote(id: string) {
	return apiFetch<Forwarder>(`/forwarders/${id}/request-quote/`, { method: 'POST' });
}

// ---------- Forwarder profiles ----------
export function createForwarderProfile(payload: Partial<ForwarderProfile>) {
	return apiFetch<ForwarderProfile>('/forwarders/profile/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function getMyForwarderProfile() {
	return apiFetch<ForwarderProfile>('/forwarders/profile/me/');
}

export function updateForwarderProfile(id: string, payload: Partial<ForwarderProfile>) {
	return apiFetch<ForwarderProfile>(`/forwarders/profile/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

// ---------- Reviews & recommendations ----------
export function getForwarderRecommendations(destinationCountry: string) {
	return apiFetch<Forwarder[]>(`/forwarders/recommendations/?destination_country=${encodeURIComponent(destinationCountry)}`);
}

export function createForwarderReview(forwarderId: string, payload: { rating: number; review_text?: string }) {
	return apiFetch<ForwarderReview>(`/forwarders/${forwarderId}/reviews/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateForwarderReview(
	forwarderId: string,
	reviewId: string,
	payload: { rating: number; review_text?: string }
) {
	return apiFetch<ForwarderReview>(`/forwarders/${forwarderId}/reviews/${reviewId}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteForwarderReview(forwarderId: string, reviewId: string) {
	return apiFetch<{ status: string }>(`/forwarders/${forwarderId}/reviews/${reviewId}/delete/`, { method: 'DELETE' });
}

export function getForwarderStatistics(id: string) {
	return apiFetch<ForwarderStatistics>(`/forwarders/${id}/statistics/`);
}
