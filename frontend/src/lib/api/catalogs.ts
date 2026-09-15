import { apiFetch } from '$lib/api/client';
import type { Catalog } from '$lib/data/trade';

export type CreateCatalogPayload = {
	productId: string;
	projectId: string;
	title: string;
	targetMarket: string;
	moq: string;
	leadTime: string;
	priceRange?: string;
	description?: string;
	highlights?: string[];
	specifications?: { label: string; value: string }[];
	tags?: string[];
};

export type UpdateCatalogPayload = Partial<CreateCatalogPayload> & {
	is_published?: boolean;
	export_description?: string;
	technical_specs?: { label: string; value: string }[];
	safety_info?: { label: string; value: string }[];
	base_price_exw?: number;
};

export type CatalogImage = {
	id: string;
	catalogId?: string;
	imageUrl?: string;
	altText?: string;
	sortOrder?: number;
	isPrimary?: boolean;
};

export type VariantType = {
	id: string;
	catalogId?: string;
	typeCode?: string;
	typeName: string;
	sortOrder?: number;
	options?: VariantOption[];
};

export type VariantOption = {
	id: string;
	variantTypeId?: string;
	optionName: string;
	sortOrder?: number;
	isAvailable?: boolean;
};

export type CatalogAIDescription = {
	export_description: string;
	technical_specs: { label: string; value: string }[];
	safety_info: { label: string; value: string }[];
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

export function updateCatalog(id: string, payload: UpdateCatalogPayload) {
	return apiFetch<Catalog>(`/catalogs/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteCatalog(id: string) {
	return apiFetch<{ status: string }>(`/catalogs/${id}/`, { method: 'DELETE' });
}

export function publishCatalog(id: string) {
	return apiFetch<Catalog>(`/catalogs/${id}/publish/`, { method: 'POST' });
}

export function unpublishCatalog(id: string) {
	return apiFetch<Catalog>(`/catalogs/${id}/unpublish/`, { method: 'POST' });
}

export function generateCatalogDescription(id: string) {
	return apiFetch<Catalog>(`/catalogs/${id}/generate-description/`, { method: 'POST' });
}

// ---------- Public / forwarder catalog ----------
export function listForwarderCatalogs() {
	return apiFetch<Catalog[]>('/catalogs/forwarder/');
}

// ---------- Catalog AI ----------
export function getCatalogMarketIntelligence(id: string) {
	return apiFetch(`/catalogs/${id}/ai/market-intelligence/`);
}

export function createCatalogMarketIntelligence(id: string) {
	return apiFetch(`/catalogs/${id}/ai/market-intelligence/`, { method: 'POST' });
}

export function getCatalogPricing(id: string) {
	return apiFetch(`/catalogs/${id}/ai/pricing/`);
}

export function createCatalogPricing(id: string, payload: Record<string, unknown>) {
	return apiFetch(`/catalogs/${id}/ai/pricing/`, { method: 'POST', body: JSON.stringify(payload) });
}

export function generateCatalogAiDescription(id: string, saveToCatalog = false) {
	return apiFetch<CatalogAIDescription>(`/catalogs/${id}/ai/description/`, {
		method: 'POST',
		body: JSON.stringify({ save_to_catalog: saveToCatalog })
	});
}

// ---------- Catalog images ----------
export function listCatalogImages(catalogId: string) {
	return apiFetch<CatalogImage[]>(`/catalogs/${catalogId}/images/`);
}

export function addCatalogImage(catalogId: string, payload: { image_url?: string; alt_text?: string; is_primary?: boolean }) {
	return apiFetch<CatalogImage>(`/catalogs/${catalogId}/images/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateCatalogImage(catalogId: string, imageId: string, payload: Record<string, unknown>) {
	return apiFetch<CatalogImage>(`/catalogs/${catalogId}/images/${imageId}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteCatalogImage(catalogId: string, imageId: string) {
	return apiFetch<{ status: string }>(`/catalogs/${catalogId}/images/${imageId}/`, { method: 'DELETE' });
}

// ---------- Catalog variants ----------
export function listVariantTypes(catalogId: string) {
	return apiFetch<{ data: VariantType[]; meta: { predefined_types: { type_code: string; type_name: string }[] } }>(
		`/catalogs/${catalogId}/variant-types/`
	);
}

export function addVariantType(catalogId: string, payload: { type_code?: string; type_name: string; options?: string[] }) {
	return apiFetch<VariantType>(`/catalogs/${catalogId}/variant-types/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateVariantType(catalogId: string, typeId: string, payload: Record<string, unknown>) {
	return apiFetch<VariantType>(`/catalogs/${catalogId}/variant-types/${typeId}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteVariantType(catalogId: string, typeId: string) {
	return apiFetch<{ status: string }>(`/catalogs/${catalogId}/variant-types/${typeId}/`, { method: 'DELETE' });
}

export function addVariantOption(catalogId: string, typeId: string, optionName: string) {
	return apiFetch<VariantOption>(`/catalogs/${catalogId}/variant-types/${typeId}/options/`, {
		method: 'POST',
		body: JSON.stringify({ option_name: optionName })
	});
}

export function updateVariantOption(catalogId: string, typeId: string, optionId: string, payload: Record<string, unknown>) {
	return apiFetch<VariantOption>(`/catalogs/${catalogId}/variant-types/${typeId}/options/${optionId}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteVariantOption(catalogId: string, typeId: string, optionId: string) {
	return apiFetch<{ status: string }>(`/catalogs/${catalogId}/variant-types/${typeId}/options/${optionId}/`, { method: 'DELETE' });
}
