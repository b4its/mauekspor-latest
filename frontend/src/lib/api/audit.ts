import { apiFetch } from '$lib/api/client';
import type { AuditEvent } from '$lib/data/trade';

export function listAuditEvents() {
	return apiFetch<AuditEvent[]>('/audit/');
}

export function exportAuditTrail() {
	return apiFetch<AuditEvent[]>('/audit/export/', { method: 'POST' });
}
