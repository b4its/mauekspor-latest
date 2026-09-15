import { apiFetch } from '$lib/api/client';
import {
	createMarketIntelligence,
	createProductPricing,
	getMarketIntelligence,
	getProductPricing
} from '$lib/api/products';
import type { MarketIntelligence, ProductPricing } from '$lib/api/products';

export type {
	MarketIntelligence,
	ProductPricing
};

/**
 * Marketing Center — Market Intelligence & Pricing Calculator.
 * Berbasis endpoint AI per produk (`/products/{id}/ai/*`).
 */

// ---------- Market Intelligence ----------
export async function getOrCreateMarketIntelligence(productId: string): Promise<MarketIntelligence> {
	try {
		return (await getMarketIntelligence(productId)).data;
	} catch {
		return (await createMarketIntelligence(productId)).data;
	}
}

// ---------- Pricing ----------
export async function getOrCreateProductPricing(
	productId: string,
	payload: { cogs_per_unit_idr: number; target_margin_percent: number; target_country_code: string }
): Promise<ProductPricing> {
	try {
		return (await getProductPricing(productId)).data;
	} catch {
		return (await createProductPricing(productId, payload)).data;
	}
}
