import { afterEach, describe, expect, it, vi } from 'vitest';
import { getAnalyticsOverview, getAnalyticsLanes, refreshAnalytics } from './analytics';
import { listAuditEvents, exportAuditTrail } from './audit';
import { listMessages, sendMessage, resolveMessageThread } from './messages';
import { listMarketInsights, getMarketInsight, createMarketInsight, refreshMarketInsight } from './markets';
import { listRFQs, getRFQ, createRFQ, shortlistRFQMatch } from './rfq';
import { listFiles, verifyFileAsset, fileDownloadUrl } from './files';
import { listChatSessions, createChatSession, sendSessionMessage, getChatSuggestions } from './chat';

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

describe('analytics & audit API contract', () => {
	it('getAnalyticsOverview -> GET /analytics/overview/', async () => {
		const fetchMock = mockApi();
		await getAnalyticsOverview();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/analytics\/overview\/$/);
	});

	it('getAnalyticsLanes -> GET /analytics/lanes/', async () => {
		const fetchMock = mockApi();
		await getAnalyticsLanes();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/analytics\/lanes\/$/);
	});

	it('refreshAnalytics -> POST /analytics/refresh/', async () => {
		const fetchMock = mockApi();
		await refreshAnalytics();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/analytics\/refresh\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('listAuditEvents -> GET /audit/', async () => {
		const fetchMock = mockApi();
		await listAuditEvents();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/audit\/$/);
	});

	it('exportAuditTrail -> POST /audit/export/', async () => {
		const fetchMock = mockApi();
		await exportAuditTrail();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/audit\/export\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});

describe('messages API contract', () => {
	it('listMessages -> GET /messages/', async () => {
		const fetchMock = mockApi();
		await listMessages();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/$/);
	});

	it('sendMessage -> POST /messages/{id}/send/ dengan {body}', async () => {
		const fetchMock = mockApi();
		await sendMessage('MSG-1', 'Halo');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/messages\/MSG-1\/send\/$/);
		expect(JSON.parse(String(init.body)).body).toBe('Halo');
	});

	it('resolveMessageThread -> POST /messages/{id}/resolve/', async () => {
		const fetchMock = mockApi();
		await resolveMessageThread('MSG-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/messages\/MSG-1\/resolve\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});

describe('markets API contract', () => {
	it('listMarketInsights -> GET /markets/', async () => {
		const fetchMock = mockApi();
		await listMarketInsights();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/markets\/$/);
	});

	it('getMarketInsight -> GET /markets/{id}/', async () => {
		const fetchMock = mockApi();
		await getMarketInsight('MKT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/markets\/MKT-1\/$/);
	});

	it('createMarketInsight -> POST /markets/ dengan payload', async () => {
		const fetchMock = mockApi();
		await createMarketInsight({ productId: 'P-1', country: 'JP' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('refreshMarketInsight -> POST /markets/{id}/refresh/', async () => {
		const fetchMock = mockApi();
		await refreshMarketInsight('MKT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/markets\/MKT-1\/refresh\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});

describe('rfq API contract', () => {
	it('listRFQs -> GET /rfqs/', async () => {
		const fetchMock = mockApi();
		await listRFQs();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/rfqs\/$/);
	});

	it('getRFQ -> GET /rfqs/{id}/', async () => {
		const fetchMock = mockApi();
		await getRFQ('RFQ-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/rfqs\/RFQ-1\/$/);
	});

	it('createRFQ -> POST /rfqs/ dengan payload', async () => {
		const fetchMock = mockApi();
		await createRFQ({ buyer: 'B-1', product: 'Kopi', destination: 'JP', quantity: '100', incoterm: 'FOB', deadline: '2026-09-01' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('shortlistRFQMatch -> POST /rfqs/{id}/shortlist/ dengan {supplier}', async () => {
		const fetchMock = mockApi();
		await shortlistRFQMatch('RFQ-1', 'NGL');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/rfqs\/RFQ-1\/shortlist\/$/);
		expect(JSON.parse(String(init.body)).supplier).toBe('NGL');
	});
});

describe('files & chat API contract', () => {
	it('listFiles -> GET /files/', async () => {
		const fetchMock = mockApi();
		await listFiles();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/files\/$/);
	});

	it('verifyFileAsset -> POST /files/{id}/verify/', async () => {
		const fetchMock = mockApi();
		await verifyFileAsset('F-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/files\/F-1\/verify\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('fileDownloadUrl -> URL absolut download', () => {
		expect(fileDownloadUrl('F-1')).toMatch(/\/api\/v1\/files\/F-1\/download\/$/);
	});

	it('listChatSessions -> GET /chat/sessions/', async () => {
		const fetchMock = mockApi();
		await listChatSessions();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/chat\/sessions\/$/);
	});

	it('createChatSession -> POST /chat/sessions/ dengan title', async () => {
		const fetchMock = mockApi();
		await createChatSession('Sesi Baru');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body)).title).toBe('Sesi Baru');
	});

	it('sendSessionMessage -> POST /chat/sessions/{id}/messages/', async () => {
		const fetchMock = mockApi();
		await sendSessionMessage('S-1', 'Halo AI');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/chat\/sessions\/S-1\/messages\/$/);
		expect(JSON.parse(String(init.body)).text ?? JSON.parse(String(init.body)).message).toBeDefined();
	});

	it('getChatSuggestions -> GET /chat/suggestions/', async () => {
		const fetchMock = mockApi();
		await getChatSuggestions();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/chat\/suggestions\/$/);
	});
});
