import { apiFetch } from '$lib/api/client';
import type { BusinessProfile } from '$lib/data/trade';

export type DashboardSummary = {
	role: string;
	has_business_profile: boolean;
	business_profile?: BusinessProfile | null;
	counts: {
		products: number;
		catalogs: number;
		buyer_requests: number;
		business_profiles: number;
		users: number;
		users_by_role: Record<string, number>;
	};
};

export function listBusinessProfiles() { return apiFetch<BusinessProfile[]>('/business-profiles/'); }
export function getBusinessProfile(id: string) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/`); }
export function createBusinessProfile(payload: Partial<BusinessProfile>) { return apiFetch<BusinessProfile>('/business-profiles/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateBusinessProfile(id: string, payload: Partial<BusinessProfile>) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function updateCertifications(id: string, certifications: string[]) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/certifications/`, { method: 'POST', body: JSON.stringify({ certifications }) }); }
export function getDashboardSummary() { return apiFetch<DashboardSummary>('/business-profiles/dashboard/summary/'); }
