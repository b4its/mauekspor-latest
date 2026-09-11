import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listCostingScenarios,
	getCostingScenario,
	createCostingScenario,
	updateCostingScenario,
	deleteCostingScenario,
	recalculateCostingScenario,
	compareCostingScenarios,
	costingPdfUrl,
	getExchangeRate,
	updateExchangeRate,
	refreshExchangeRate
} from './costing';
import { listTradeDocuments, getTradeDocument, generateTradeDocument, approveTradeDocument } from './documents';

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

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('costing API contract', () => {
	it('listCostingScenarios -> GET /costing/', async () => {
		const fetchMock = mockApi();
		await listCostingScenarios();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/costing\/$/);
	});

	it('getCostingScenario -> GET /costing/{id}/', async () => {
		const fetchMock = mockApi();
		await getCostingScenario('CST-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/costing\/CST-1\/$/);
	});

	it('createCostingScenario -> POST /costing/ dengan payload', async () => {
		const fetchMock = mockApi();
		await createCostingScenario({ title: 'T', projectId: 'P-1', productId: 'PR-1', incoterm: 'FOB', margin: 20, destination: 'JP' });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body)).incoterm).toBe('FOB');
	});

	it('updateCostingScenario -> PUT /costing/{id}/', async () => {
		const fetchMock = mockApi();
		await updateCostingScenario('CST-1', { margin: 25 });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('PUT');
		expect(JSON.parse(String(init.body)).margin).toBe(25);
	});

	it('deleteCostingScenario -> DELETE /costing/{id}/', async () => {
		const fetchMock = mockApi();
		await deleteCostingScenario('CST-1');
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('recalculateCostingScenario -> POST /costing/{id}/recalculate/', async () => {
		const fetchMock = mockApi();
		await recalculateCostingScenario('CST-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/costing\/CST-1\/recalculate\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('compareCostingScenarios -> POST /costing/compare/ dengan {ids}', async () => {
		const fetchMock = mockApi();
		await compareCostingScenarios(['CST-1', 'CST-2']);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/costing\/compare\/$/);
		expect(JSON.parse(String(init.body))).toEqual({ ids: ['CST-1', 'CST-2'] });
	});

	it('costingPdfUrl mengembalikan URL absolut pdf', () => {
		expect(costingPdfUrl('CST-1')).toMatch(/\/api\/v1\/costing\/CST-1\/pdf\/$/);
	});

	it('getExchangeRate -> GET /costing/exchange-rate/', async () => {
		const fetchMock = mockApi();
		await getExchangeRate();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/costing\/exchange-rate\/$/);
	});

	it('updateExchangeRate -> PUT dengan {rate}', async () => {
		const fetchMock = mockApi();
		await updateExchangeRate(15800);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('PUT');
		expect(JSON.parse(String(init.body)).rate).toBe(15800);
	});

	it('refreshExchangeRate -> POST /costing/exchange-rate/refresh/', async () => {
		const fetchMock = mockApi();
		await refreshExchangeRate();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/costing\/exchange-rate\/refresh\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});

describe('documents API contract', () => {
	it('listTradeDocuments -> GET /documents/', async () => {
		const fetchMock = mockApi();
		await listTradeDocuments();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/documents\/$/);
	});

	it('getTradeDocument -> GET /documents/{id}/', async () => {
		const fetchMock = mockApi();
		await getTradeDocument('DOC-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/documents\/DOC-1\/$/);
	});

	it('generateTradeDocument -> POST /documents/generate/ dengan projectId+type', async () => {
		const fetchMock = mockApi();
		await generateTradeDocument({ projectId: 'P-1', type: 'Commercial Invoice' });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/documents\/generate\/$/);
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body)).type).toBe('Commercial Invoice');
	});

	it('approveTradeDocument -> POST /documents/{id}/approve/', async () => {
		const fetchMock = mockApi();
		await approveTradeDocument('DOC-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/documents\/DOC-1\/approve\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});
