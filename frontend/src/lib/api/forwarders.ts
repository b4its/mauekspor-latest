import { apiFetch } from '$lib/api/client';
import type { Forwarder } from '$lib/data/trade';

export function listForwarders() { return apiFetch<Forwarder[]>('/forwarders/'); }
export function getForwarder(id: string) { return apiFetch<Forwarder>(`/forwarders/${id}/`); }
export function requestForwarderQuote(id: string) { return apiFetch<Forwarder>(`/forwarders/${id}/request-quote/`, { method: 'POST' }); }
