import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listExportAnalyses,
	getExportAnalysis,
	createExportAnalysis,
	deleteExportAnalysis,
	reanalyzeExportAnalysis,
	compareExportAnalyses,
	runRegulationCheck,
	getRegulationRecommendations,
	analysisPdfUrl,
	listCountries,
	getCountry
} from './export-analysis';
import { listBuyerRequests, getBuyerRequest, matchBuyerRequest, updateBuyerRequestStatus } from './buyer-requests';
import { listTradeProjects, getTradeProject, createTradeProject } from './trade-projects';
import { listBusinessProfiles, getBusinessProfile, updateCertifications, getDashboardSummary } from './business-profile';
import { listEducationalModules, getEducationalModule, publishEducationalModule } from './educational';
import { listEducationalArticles } from './educational-articles';
import { listKnowledgeArticles, publishKnowledgeArticle } from './knowledge';
import { listCalendarEvents, markCalendarEventDone } from './calendar';

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

describe('export-analysis API contract', () => {
	it('listExportAnalyses -> GET /export-analysis/', async () => {
		const fetchMock = mockApi();
		await listExportAnalyses();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/export-analysis\/$/);
	});

	it('getExportAnalysis -> GET /export-analysis/{id}/', async () => {
		const fetchMock = mockApi();
		await getExportAnalysis('EA-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/export-analysis\/EA-1\/$/);
	});

	it('createExportAnalysis -> POST /export-analysis/', async () => {
		const fetchMock = mockApi();
		await createExportAnalysis({ productId: 'P-1', destination: 'JP' } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('reanalyzeExportAnalysis -> POST /export-analysis/{id}/reanalyze/', async () => {
		const fetchMock = mockApi();
		await reanalyzeExportAnalysis('EA-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/export-analysis\/EA-1\/reanalyze\/$/);
	});

	it('deleteExportAnalysis -> DELETE /export-analysis/{id}/', async () => {
		const fetchMock = mockApi();
		await deleteExportAnalysis('EA-1');
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('compareExportAnalyses -> POST /export-analysis/compare/ dengan payload', async () => {
		const fetchMock = mockApi();
		await compareExportAnalyses({ product_id: 'P-1', country_codes: ['JP', 'DE'] } as never);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/export-analysis\/compare\/$/);
		expect(JSON.parse(String(init.body)).country_codes).toEqual(['JP', 'DE']);
	});

	it('runRegulationCheck -> POST /export-analysis/{id}/regulation-recommendations/', async () => {
		const fetchMock = mockApi();
		await runRegulationCheck('EA-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/export-analysis\/EA-1\/regulation-recommendations\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('getRegulationRecommendations -> GET dengan ?language=', async () => {
		const fetchMock = mockApi();
		await getRegulationRecommendations('EA-1', 'en');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/export-analysis\/EA-1\/regulation-recommendations\/\?language=en$/);
	});

	it('analysisPdfUrl -> URL absolut pdf', () => {
		expect(analysisPdfUrl('EA-1')).toMatch(/\/export-analysis\/EA-1\/pdf\/$/);
	});

	it('listCountries -> GET /countries/', async () => {
		const fetchMock = mockApi();
		await listCountries();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/countries\/$/);
	});

	it('getCountry -> GET /countries/{code}/', async () => {
		const fetchMock = mockApi();
		await getCountry('JP');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/countries\/JP\/$/);
	});
});

describe('buyer-requests, trade-projects, business-profile API contract', () => {
	it('listBuyerRequests -> GET /buyer-requests/', async () => {
		const fetchMock = mockApi();
		await listBuyerRequests();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/buyer-requests\/$/);
	});

	it('getBuyerRequest -> GET /buyer-requests/{id}/', async () => {
		const fetchMock = mockApi();
		await getBuyerRequest('BR-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/buyer-requests\/BR-1\/$/);
	});

	it('matchBuyerRequest -> POST /buyer-requests/{id}/match/', async () => {
		const fetchMock = mockApi();
		await matchBuyerRequest('BR-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/buyer-requests\/BR-1\/match\/$/);
	});

	it('updateBuyerRequestStatus -> PATCH /buyer-requests/{id}/status/ dengan {status}', async () => {
		const fetchMock = mockApi();
		await updateBuyerRequestStatus('BR-1', { status: 'Closed' } as never);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/buyer-requests\/BR-1\/status\/$/);
		expect(JSON.parse(String(init.body)).status).toBe('Closed');
	});

	it('listTradeProjects -> GET /trade-projects/', async () => {
		const fetchMock = mockApi();
		await listTradeProjects();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/trade-projects\/$/);
	});

	it('getTradeProject -> GET /trade-projects/{id}/', async () => {
		const fetchMock = mockApi();
		await getTradeProject('TP-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/trade-projects\/TP-1\/$/);
	});

	it('createTradeProject -> POST /trade-projects/', async () => {
		const fetchMock = mockApi();
		await createTradeProject({ name: 'Proyek', product: 'Kopi', buyer: 'X', country: 'JP', incoterm: 'FOB', targetValue: 100 } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('listBusinessProfiles -> GET /business-profiles/', async () => {
		const fetchMock = mockApi();
		await listBusinessProfiles();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/business-profiles\/$/);
	});

	it('getBusinessProfile -> GET /business-profiles/{id}/', async () => {
		const fetchMock = mockApi();
		await getBusinessProfile('BP-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/business-profiles\/BP-1\/$/);
	});

	it('updateCertifications -> PUT /business-profiles/{id}/certifications/ dengan array', async () => {
		const fetchMock = mockApi();
		await updateCertifications('BP-1', ['Halal', 'HACCP']);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/business-profiles\/BP-1\/certifications\/$/);
		expect(JSON.parse(String(init.body)).certifications).toEqual(['Halal', 'HACCP']);
	});

	it('getDashboardSummary -> GET /business-profiles/dashboard/summary/', async () => {
		const fetchMock = mockApi();
		await getDashboardSummary();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/business-profiles\/dashboard\/summary\/$/);
	});
});

describe('educational, knowledge, calendar API contract', () => {
	it('listEducationalModules -> GET /educational/modules/', async () => {
		const fetchMock = mockApi();
		await listEducationalModules();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/educational\/$/);
	});

	it('getEducationalModule -> GET /educational/modules/{id}/', async () => {
		const fetchMock = mockApi();
		await getEducationalModule('EDU-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/educational\/modules\/EDU-1\/$/);
	});

	it('publishEducationalModule -> POST /educational/modules/{id}/publish/', async () => {
		const fetchMock = mockApi();
		await publishEducationalModule('EDU-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/educational\/EDU-1\/publish\/$/);
	});

	it('listEducationalArticles -> GET /educational/articles/', async () => {
		const fetchMock = mockApi();
		await listEducationalArticles();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/educational\/articles\/$/);
	});

	it('listKnowledgeArticles -> GET /knowledge/', async () => {
		const fetchMock = mockApi();
		await listKnowledgeArticles();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/knowledge\/$/);
	});

	it('publishKnowledgeArticle -> POST /knowledge/{id}/publish/', async () => {
		const fetchMock = mockApi();
		await publishKnowledgeArticle('KB-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/knowledge\/KB-1\/publish\/$/);
	});

	it('listCalendarEvents -> GET /calendar/', async () => {
		const fetchMock = mockApi();
		await listCalendarEvents();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/calendar\/$/);
	});

	it('markCalendarEventDone -> POST /calendar/{id}/done/', async () => {
		const fetchMock = mockApi();
		await markCalendarEventDone('CAL-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/calendar\/CAL-1\/done\/$/);
	});
});
