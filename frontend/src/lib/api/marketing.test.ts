import { afterEach, describe, expect, it, vi } from 'vitest';
import { getOrCreateMarketIntelligence, hasMarketIntelligence, getOrCreateProductPricing, hasProductPricing } from './marketing';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data
	} as unknown as Response;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('marketing getOrCreate fallback', () => {
	it('getOrCreateMarketIntelligence: GET sukses -> data GET, tanpa POST', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValueOnce(jsonResponse(200, { data: { productId: 'P-1', recommendedCountries: [] } }))
			.mockResolvedValueOnce(jsonResponse(200, { data: {} }));
		vi.stubGlobal('fetch', fetchMock);

		const result = await getOrCreateMarketIntelligence('P-1');
		expect(result.productId).toBe('P-1');
		expect(fetchMock).toHaveBeenCalledTimes(1);
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/products\/P-1\/ai\/market-intelligence\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method ?? 'GET').toBe('GET');
	});

	it('getOrCreateMarketIntelligence: GET gagal (404) -> fallback POST create', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValueOnce(jsonResponse(404, { message: 'not found' }))
			.mockResolvedValueOnce(jsonResponse(200, { data: { productId: 'P-1', recommendedCountries: [] } }));
		vi.stubGlobal('fetch', fetchMock);

		const result = await getOrCreateMarketIntelligence('P-1');
		expect(result.productId).toBe('P-1');
		expect(fetchMock).toHaveBeenCalledTimes(2);
		expect((fetchMock.mock.calls[1][1] as RequestInit).method).toBe('POST');
	});

	it('getOrCreateProductPricing: GET gagal -> fallback POST dengan payload', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValueOnce(jsonResponse(404, { message: 'not found' }))
			.mockResolvedValueOnce(jsonResponse(200, { data: { exwPriceUsd: 100, cogsPerUnitIdr: 50, targetMarginPercent: 20, targetCountryCode: 'JP', exchangeRateUsed: 15800 } }));
		vi.stubGlobal('fetch', fetchMock);

		const result = await getOrCreateProductPricing('P-1', { cogs_per_unit_idr: 5000, target_margin_percent: 20, target_country_code: 'JP' });
		expect(result.exwPriceUsd).toBe(100);
		expect(fetchMock).toHaveBeenCalledTimes(2);
		const postInit = fetchMock.mock.calls[1][1] as RequestInit;
		expect(JSON.parse(String(postInit.body)).target_country_code).toBe('JP');
	});

	it('getOrCreateProductPricing: GET sukses -> tidak memanggil POST', async () => {
		const fetchMock = vi.fn().mockResolvedValueOnce(jsonResponse(200, { data: { exwPriceUsd: 200, cogsPerUnitIdr: 50, targetMarginPercent: 20, targetCountryCode: 'JP', exchangeRateUsed: 15800 } }));
		vi.stubGlobal('fetch', fetchMock);

		const result = await getOrCreateProductPricing('P-1', { cogs_per_unit_idr: 5000, target_margin_percent: 20, target_country_code: 'JP' });
		expect(result.exwPriceUsd).toBe(200);
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});

	it('hasMarketIntelligence & hasProductPricing meneruskan ke getter', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data: {} }));
		vi.stubGlobal('fetch', fetchMock);
		await hasMarketIntelligence('P-1');
		await hasProductPricing('P-1');
		expect(fetchMock).toHaveBeenCalledTimes(2);
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/market-intelligence/);
		expect(String(fetchMock.mock.calls[1][0])).toMatch(/pricing/);
	});
});
