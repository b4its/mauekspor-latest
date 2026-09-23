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

export function uploadComplianceEvidence(payload: EvidencePayload) {
	return apiFetch<ComplianceRequirement>(`/compliance/requirements/${payload.requirementId}/evidence/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}
