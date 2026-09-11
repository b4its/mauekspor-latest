import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listProducts,
	getProduct,
	createProduct,
	updateProduct,
	deleteProduct,
	enrichProduct,
	batchEnrichProducts,
	batchDeleteProducts,
	getMarketIntelligence,
	createMarketIntelligence,
	getProductPricing,
	createProductPricing,
	generateCatalogDescription
} from './products';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data
	} as unknown as Response;
}

function mockApi() {
	const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data: {} }));
	vi.stubGlobal('fetch', fetchMock);
	return fetchMock;
}

function urlOf(fetchMock: ReturnType<typeof vi.fn>, call = 0): string {
	return String(fetchMock.mock.calls[call][0]);
}
function initOf(fetchMock: ReturnType<typeof vi.fn>, call = 0) {
	return fetchMock.mock.calls[call][1] as RequestInit;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('products API contract', () => {
	it('listProducts -> GET /products/', async () => {
		const fetchMock = mockApi();
		await listProducts();
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/$/);
		expect(initOf(fetchMock).method ?? 'GET').toBe('GET');
	});

	it('getProduct -> GET /products/{id}/', async () => {
		const fetchMock = mockApi();
		await getProduct('P-1');
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/P-1\/$/);
	});

	it('createProduct -> POST /products/ dengan body JSON', async () => {
		const fetchMock = mockApi();
		await createProduct({ name: 'Kopi', category: 'F&B', origin: 'Aceh' });
		expect(initOf(fetchMock).method).toBe('POST');
		expect(JSON.parse(String(initOf(fetchMock).body))).toEqual({ name: 'Kopi', category: 'F&B', origin: 'Aceh' });
	});

	it('updateProduct -> PATCH /products/{id}/', async () => {
		const fetchMock = mockApi();
		await updateProduct('P-1', { moq: '1000' });
		expect(initOf(fetchMock).method).toBe('PATCH');
		expect(JSON.parse(String(initOf(fetchMock).body))).toEqual({ moq: '1000' });
	});

	it('deleteProduct -> DELETE /products/{id}/', async () => {
		const fetchMock = mockApi();
		await deleteProduct('P-1');
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/P-1\/$/);
		expect(initOf(fetchMock).method).toBe('DELETE');
	});

	it('enrichProduct -> POST /products/{id}/enrich/', async () => {
		const fetchMock = mockApi();
		await enrichProduct('P-1');
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/P-1\/enrich\/$/);
		expect(initOf(fetchMock).method).toBe('POST');
	});

	it('batchEnrichProducts -> POST /products/batch/enrich/ dengan ids', async () => {
		const fetchMock = mockApi();
		await batchEnrichProducts(['P-1', 'P-2']);
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/batch\/enrich\/$/);
		expect(JSON.parse(String(initOf(fetchMock).body))).toEqual({ ids: ['P-1', 'P-2'] });
	});

	it('batchDeleteProducts -> POST /products/batch/delete/', async () => {
		const fetchMock = mockApi();
		await batchDeleteProducts(['P-1']);
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/batch\/delete\/$/);
	});

	it('getMarketIntelligence -> GET /products/{id}/ai/market-intelligence/', async () => {
		const fetchMock = mockApi();
		await getMarketIntelligence('P-1');
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/P-1\/ai\/market-intelligence\/$/);
	});

	it('createMarketIntelligence -> POST endpoint yang sama', async () => {
		const fetchMock = mockApi();
		await createMarketIntelligence('P-1');
		expect(initOf(fetchMock).method).toBe('POST');
	});

	it('getProductPricing -> GET /products/{id}/ai/pricing/', async () => {
		const fetchMock = mockApi();
		await getProductPricing('P-1');
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/P-1\/ai\/pricing\/$/);
	});

	it('createProductPricing -> POST dengan payload margin/COGS', async () => {
		const fetchMock = mockApi();
		await createProductPricing('P-1', { cogs_per_unit_idr: 28500, target_margin_percent: 22, target_country_code: 'JP' });
		expect(initOf(fetchMock).method).toBe('POST');
		expect(JSON.parse(String(initOf(fetchMock).body)).target_country_code).toBe('JP');
	});

	it('generateCatalogDescription -> POST /products/{id}/ai/catalog-description/', async () => {
		const fetchMock = mockApi();
		await generateCatalogDescription('P-1');
		expect(urlOf(fetchMock)).toMatch(/\/api\/v1\/products\/P-1\/ai\/catalog-description\/$/);
		expect(initOf(fetchMock).method).toBe('POST');
	});
});
