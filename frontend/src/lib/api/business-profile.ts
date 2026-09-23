import { apiFetch } from '$lib/api/client';
import type { BusinessProfile } from '$lib/data/trade';

export function listBusinessProfiles() { return apiFetch<BusinessProfile[]>('/business-profiles/'); }
export function getBusinessProfile(id: string) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/`); }
export function createBusinessProfile(payload: Partial<BusinessProfile>) { return apiFetch<BusinessProfile>('/business-profiles/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateBusinessProfile(id: string, payload: Partial<BusinessProfile>) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function updateCertifications(id: string, certifications: string[]) { return apiFetch<BusinessProfile>(`/business-profiles/${id}/certifications/`, { method: 'POST', body: JSON.stringify({ certifications }) }); }
