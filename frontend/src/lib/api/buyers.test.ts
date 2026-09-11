import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listBuyers,
	getBuyer,
	createBuyer,
	qualifyBuyer,
	logBuyerContact,
	createBuyerProfile,
	getMyBuyerProfile,
	updateBuyerProfile
} from './buyers';
import {
	listForwarders,
	getForwarder,
	requestForwarderQuote,
	createForwarderProfile,
	getMyForwarderProfile,
	updateForwarderProfile,
	getForwarderRecommendations,
	createForwarderReview,
	updateForwarderReview,
	deleteForwarderReview,
	getForwarderStatistics
} from './forwarders';

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

describe('buyers API contract', () => {
	it('listBuyers -> GET /buyers/', async () => {
		const fetchMock = mockApi();
		await listBuyers();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyers\/$/);
	});

	it('getBuyer -> GET /buyers/{id}/', async () => {
		const fetchMock = mockApi();
		await getBuyer('B-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyers\/B-1\/$/);
	});

	it('createBuyer -> POST /buyers/ dengan payload', async () => {
		const fetchMock = mockApi();
		await createBuyer({ name: 'X', country: 'JP', segment: 'Retail', interestedProducts: ['Kopi'] });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body)).segment).toBe('Retail');
	});

	it('qualifyBuyer -> POST /buyers/{id}/qualify/', async () => {
		const fetchMock = mockApi();
		await qualifyBuyer('B-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyers\/B-1\/qualify\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('logBuyerContact -> POST /buyers/{id}/contacts/ dengan {note}', async () => {
		const fetchMock = mockApi();
		await logBuyerContact('B-1', 'Follow-up');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyers\/B-1\/contacts\/$/);
		expect(JSON.parse(String(init.body)).note).toBe('Follow-up');
	});

	it('createBuyerProfile -> POST /buyers/profile/', async () => {
		const fetchMock = mockApi();
		await createBuyerProfile({ companyName: 'PT X' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyers\/profile\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('getMyBuyerProfile -> GET /buyers/profile/me/', async () => {
		const fetchMock = mockApi();
		await getMyBuyerProfile();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyers\/profile\/me\/$/);
	});

	it('updateBuyerProfile -> PUT /buyers/profile/{id}/', async () => {
		const fetchMock = mockApi();
		await updateBuyerProfile('BP-1', { businessType: 'Importer' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('PUT');
	});
});

describe('forwarders API contract', () => {
	it('listForwarders -> GET /forwarders/', async () => {
		const fetchMock = mockApi();
		await listForwarders();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/forwarders\/$/);
	});

	it('getForwarder -> GET /forwarders/{id}/', async () => {
		const fetchMock = mockApi();
		await getForwarder('FWD-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/forwarders\/FWD-1\/$/);
	});

	it('requestForwarderQuote -> POST /forwarders/{id}/request-quote/', async () => {
		const fetchMock = mockApi();
		await requestForwarderQuote('FWD-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/forwarders\/FWD-1\/request-quote\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('getForwarderRecommendations -> GET /forwarders/recommendations/?destination_country=', async () => {
		const fetchMock = mockApi();
		await getForwarderRecommendations('Japan');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/forwarders\/recommendations\/\?destination_country=Japan$/);
	});

	it('createForwarderReview -> POST /forwarders/{id}/reviews/ dengan rating', async () => {
		const fetchMock = mockApi();
		await createForwarderReview('FWD-1', { rating: 5, review_text: 'Bagus' });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/forwarders\/FWD-1\/reviews\/$/);
		expect(JSON.parse(String(init.body)).rating).toBe(5);
	});

	it('updateForwarderReview -> PUT /forwarders/{id}/reviews/{rid}/', async () => {
		const fetchMock = mockApi();
		await updateForwarderReview('FWD-1', 'RV-1', { rating: 4 });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/forwarders\/FWD-1\/reviews\/RV-1\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('PUT');
	});

	it('deleteForwarderReview -> DELETE /forwarders/{id}/reviews/{rid}/delete/', async () => {
		const fetchMock = mockApi();
		await deleteForwarderReview('FWD-1', 'RV-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/forwarders\/FWD-1\/reviews\/RV-1\/delete\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('getForwarderStatistics -> GET /forwarders/{id}/statistics/', async () => {
		const fetchMock = mockApi();
		await getForwarderStatistics('FWD-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/forwarders\/FWD-1\/statistics\/$/);
	});

	it('createForwarderProfile -> POST /forwarders/profile/', async () => {
		const fetchMock = mockApi();
		await createForwarderProfile({ companyName: 'NGL' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/forwarders\/profile\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('getMyForwarderProfile -> GET /forwarders/profile/me/', async () => {
		const fetchMock = mockApi();
		await getMyForwarderProfile();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/forwarders\/profile\/me\/$/);
	});
});
