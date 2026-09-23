import { apiFetch } from '$lib/api/client';
import type { Catalog } from '$lib/data/trade';

export type CreateCatalogPayload = {
	productId: string;
	projectId: string;
	title: string;
	targetMarket: string;
	moq: string;
	leadTime: string;
};

export function listCatalogs() {
	return apiFetch<Catalog[]>('/catalogs/');
}

export function getCatalog(id: string) {
	return apiFetch<Catalog>(`/catalogs/${id}/`);
}

export function createCatalog(payload: CreateCatalogPayload) {
	return apiFetch<Catalog>('/catalogs/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function publishCatalog(id: string) {
	return apiFetch<Catalog>(`/catalogs/${id}/publish/`, { method: 'POST' });
}

export function generateCatalogDescription(id: string) {
	return apiFetch<Catalog>(`/catalogs/${id}/generate-description/`, { method: 'POST' });
}
