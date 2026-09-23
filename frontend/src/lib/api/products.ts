import { apiFetch } from '$lib/api/client';
import type { Product } from '$lib/data/trade';

export type CreateProductPayload = {
	name: string;
	category: string;
	origin: string;
	packaging?: string;
	netWeight?: string;
	grossWeight?: string;
	moq?: string;
	leadTime?: string;
};

export function listProducts() {
	return apiFetch<Product[]>('/products/');
}

export function getProduct(id: string) {
	return apiFetch<Product>(`/products/${id}/`);
}

export function createProduct(payload: CreateProductPayload) {
	return apiFetch<Product>('/products/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function enrichProduct(id: string) {
	return apiFetch<Product>(`/products/${id}/enrich/`, { method: 'POST' });
}
