import { apiFetch } from '$lib/api/client';
import type { BillingRecord } from '$lib/data/trade';

export function getBilling() {
	return apiFetch<BillingRecord[]>('/billing/');
}

export function changePlan(plan: BillingRecord['plan']) {
	return apiFetch<BillingRecord>('/billing/change-plan/', { method: 'POST', body: JSON.stringify({ plan }) });
}

export function downloadInvoice(id: string) {
	return apiFetch<BillingRecord>(`/billing/${id}/invoice/`, { method: 'POST' });
}
