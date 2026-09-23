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
	description?: string;
	material_composition?: string;
	quality_specs?: Record<string, unknown>;
};

export type UpdateProductPayload = Partial<CreateProductPayload> & {
	hs?: string;
	hs_code?: string;
	sku?: string;
	name_english_b2b?: string;
	description_english_b2b?: string;
	marketing_highlights?: string[];
	production_technique?: string;
	finishing_type?: string;
	certificates?: string[];
};

export type MiForwarder = {
	id?: string;
	name?: string;
	averageRating?: number;
	serviceTypes?: string[];
	contactInfo?: { phone?: string; email?: string };
};

export type MarketIntelligence = {
	productId?: string;
	recommendedCountries: {
		country: string;
		code: string;
		score: number;
		reason?: string;
		market_size?: string;
		competition_level?: string;
		price_range?: string;
		entry_strategy?: string;
		forwarders?: MiForwarder[];
	}[];
	countriesToAvoid?: { country: string; code: string; reason?: string }[];
	marketTrends?: string[];
	competitiveLandscape?: string;
	growthOpportunities?: string[];
	risksAndChallenges?: string[];
	overallRecommendation?: string;
	generatedAt?: string;
};

export type ProductPricing = {
	productId?: string;
	cogsPerUnitIdr: number;
	targetMarginPercent: number;
	targetCountryCode: string;
	exchangeRateUsed: number;
	exwPriceUsd: number;
	fobPriceUsd: number;
	cifPriceUsd?: number;
	pricingInsight?: string;
	pricingBreakdown?: Record<string, unknown>;
	generatedAt?: string;
};

export type CatalogDescription = {
	export_description: string;
	technical_specs: { label: string; value: string }[];
	safety_info: { label: string; value: string }[];
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

export function updateProduct(id: string, payload: UpdateProductPayload) {
	return apiFetch<Product>(`/products/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(payload)
	});
}

export function deleteProduct(id: string) {
	return apiFetch<{ status: string; id: string }>(`/products/${id}/`, { method: 'DELETE' });
}

export function enrichProduct(id: string) {
	return apiFetch<Product>(`/products/${id}/enrich/`, { method: 'POST' });
}

export type BatchEnrichResult = {
	enriched: string[];
	enrichedCount: number;
	skippedCount: number;
	targetCount: number;
};

export function batchEnrichProducts(ids: string[] = []) {
	return apiFetch<BatchEnrichResult>('/products/batch/enrich/', {
		method: 'POST',
		body: JSON.stringify({ ids })
	});
}

export function batchDeleteProducts(ids: string[]) {
	return apiFetch<{ deleted: string[]; deletedCount: number }>('/products/batch/delete/', {
		method: 'POST',
		body: JSON.stringify({ ids })
	});
}

// ---------- AI: Market Intelligence ----------
export function getMarketIntelligence(productId: string) {
	return apiFetch<MarketIntelligence>(`/products/${productId}/ai/market-intelligence/`);
}

export function createMarketIntelligence(productId: string) {
	return apiFetch<MarketIntelligence>(`/products/${productId}/ai/market-intelligence/`, { method: 'POST' });
}

// ---------- AI: Pricing ----------
export function getProductPricing(productId: string) {
	return apiFetch<ProductPricing>(`/products/${productId}/ai/pricing/`);
}

export function createProductPricing(
	productId: string,
	payload: {
		cogs_per_unit_idr: number;
		target_margin_percent: number;
		target_country_code: string;
	}
) {
	return apiFetch<ProductPricing>(`/products/${productId}/ai/pricing/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

// ---------- AI: Catalog description ----------
export function generateCatalogDescription(productId: string) {
	return apiFetch<CatalogDescription>(`/products/${productId}/ai/catalog-description/`, {
		method: 'POST',
		body: JSON.stringify({})
	});
}
