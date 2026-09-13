import { apiFetch } from '$lib/api/client';
import type { BusinessProfile } from '$lib/data/trade';

export type DashboardSummary = {
	role: string;
	has_business_profile: boolean;
	business_profile?: BusinessProfile | null;
	counts: {
		products: number;
		products_without_catalog: number;
		catalogs: number;
		catalogs_published: number;
		catalogs_draft: number;
		buyer_requests: number;
		buyer_requests_pending: number;
		business_profiles: number;
		users: number;
		users_by_role: Record<string, number>;
		educational_modules: number;
		educational_articles: number;
	};
};

export function listBusinessProfiles() { return apiFetch<BusinessProfile[]>('/business-profiles/'); }
export function getBusinessProfile(id: string) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/`); }
export function createBusinessProfile(payload: Partial<BusinessProfile>) { return apiFetch<BusinessProfile>('/business-profiles/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateBusinessProfile(id: string, payload: Partial<BusinessProfile>) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function updateCertifications(id: string, certifications: string[]) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/certifications/`, { method: 'POST', body: JSON.stringify({ certifications }) }); }
export function getDashboardSummary() { return apiFetch<DashboardSummary>('/business-profiles/dashboard/summary/'); }
