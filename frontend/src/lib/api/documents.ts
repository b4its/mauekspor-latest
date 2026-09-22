import { apiFetch } from '$lib/api/client';
import type { TradeDocument } from '$lib/data/trade';

export type GenerateDocumentPayload = {
	projectId: string;
	type: TradeDocument['type'];
};

export function listTradeDocuments() {
	return apiFetch<TradeDocument[]>('/documents/');
}

export function getTradeDocument(id: string) {
	return apiFetch<TradeDocument>(`/documents/${id}/`);
}

export function generateTradeDocument(payload: GenerateDocumentPayload) {
	return apiFetch<TradeDocument>('/documents/generate/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function approveTradeDocument(id: string) {
	return apiFetch<TradeDocument>(`/documents/${id}/approve/`, { method: 'POST' });
}

export function updateTradeDocument(id: string, payload: Partial<TradeDocument>) {
	return apiFetch<TradeDocument>(`/documents/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteTradeDocument(id: string) {
	return apiFetch<{ status: string; id: string }>(`/documents/${id}/`, { method: 'DELETE' });
}
