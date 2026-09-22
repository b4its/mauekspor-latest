import { apiFetch } from '$lib/api/client';
import type { ComplianceRequirement } from '$lib/data/trade';

export type EvidencePayload = {
	requirementId: string;
	note: string;
	fileName?: string;
};

export function listComplianceRequirements() {
	return apiFetch<ComplianceRequirement[]>('/compliance/requirements/');
}

export function getComplianceRequirement(id: string) {
	return apiFetch<ComplianceRequirement>(`/compliance/requirements/${id}/`);
}

export type CreateCompliancePayload = {
	title: string;
	category?: string;
	severity?: string;
	owner?: string;
	source?: string;
	requiredEvidence?: string;
	projectId?: string;
};

export function createComplianceRequirement(payload: CreateCompliancePayload) {
	return apiFetch<ComplianceRequirement>('/compliance/requirements/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function uploadComplianceEvidence(payload: EvidencePayload) {
	return apiFetch<ComplianceRequirement>(`/compliance/requirements/${payload.requirementId}/evidence/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateComplianceRequirement(id: string, payload: Partial<ComplianceRequirement>) {
	return apiFetch<ComplianceRequirement>(`/compliance/requirements/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(payload)
	});
}

export function deleteComplianceRequirement(id: string) {
	return apiFetch<{ status: string; id: string }>(`/compliance/requirements/${id}/`, { method: 'DELETE' });
}
