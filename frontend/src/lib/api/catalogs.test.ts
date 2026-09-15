import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listCatalogs,
	getCatalog,
	createCatalog,
	updateCatalog,
	deleteCatalog,
	publishCatalog,
	unpublishCatalog,
	generateCatalogDescription,
	listForwarderCatalogs,
	createCatalogPricing,
	createCatalogMarketIntelligence,
	generateCatalogAiDescription,
	listCatalogImages,
	addCatalogImage,
	updateCatalogImage,
	deleteCatalogImage,
	listVariantTypes,
	addVariantType,
	createCatalogPricing as createPricing
} from './catalogs';
import { listOrders, getOrder, createOrder, confirmOrder } from './orders';
import { listQuotations, getQuotation, createQuotation, acceptQuotation } from './quotations';
import { listTasks, getTask, completeTask, assignTask } from './tasks';
import { listTeamMembers, inviteTeamMember, updateTeamMemberRole } from './team';
import { listSupportTickets, createSupportTicket, resolveSupportTicket } from './support';
import { getBilling, changePlan, downloadInvoice } from './billing';
import { listApiKeys, createApiKey, revokeApiKey } from './api-keys';
import { listComplianceRequirements, getComplianceRequirement } from './compliance';
import { getSettings, updateSettings } from './settings';

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

describe('catalogs API contract', () => {
	it('listCatalogs -> GET /catalogs/', async () => {
		const fetchMock = mockApi();
		await listCatalogs();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/catalogs\/$/);
	});

	it('getCatalog -> GET /catalogs/{id}/', async () => {
		const fetchMock = mockApi();
		await getCatalog('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/$/);
	});

	it('createCatalog -> POST /catalogs/', async () => {
		const fetchMock = mockApi();
		await createCatalog({ title: 'Katalog', productId: 'P-1', targetMarket: 'JP', moq: '100' } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('updateCatalog -> PUT /catalogs/{id}/', async () => {
		const fetchMock = mockApi();
		await updateCatalog('CAT-1', { moq: '200' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('PUT');
	});

	it('deleteCatalog -> DELETE /catalogs/{id}/', async () => {
		const fetchMock = mockApi();
		await deleteCatalog('CAT-1');
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('publishCatalog -> POST /catalogs/{id}/publish/', async () => {
		const fetchMock = mockApi();
		await publishCatalog('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/publish\/$/);
	});

	it('unpublishCatalog -> POST /catalogs/{id}/unpublish/', async () => {
		const fetchMock = mockApi();
		await unpublishCatalog('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/unpublish\/$/);
	});

	it('generateCatalogDescription -> POST /catalogs/{id}/generate-description/', async () => {
		const fetchMock = mockApi();
		await generateCatalogDescription('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/generate-description\/$/);
	});

	it('listForwarderCatalogs -> GET /catalogs/forwarder/', async () => {
		const fetchMock = mockApi();
		await listForwarderCatalogs();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/forwarder\/$/);
	});

	it('createCatalogPricing -> POST /catalogs/{id}/ai/pricing/ dengan payload', async () => {
		const fetchMock = mockApi();
		await createCatalogPricing('CAT-1', { cogs_per_unit_idr: 1000 });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/ai\/pricing\/$/);
		expect(JSON.parse(String(init.body)).cogs_per_unit_idr).toBe(1000);
	});

	it('createCatalogMarketIntelligence -> POST /catalogs/{id}/ai/market-intelligence/', async () => {
		const fetchMock = mockApi();
		await createCatalogMarketIntelligence('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/ai\/market-intelligence\/$/);
	});

	it('generateCatalogAiDescription -> POST /catalogs/{id}/ai/description/ dengan save_to_catalog', async () => {
		const fetchMock = mockApi();
		await generateCatalogAiDescription('CAT-1', true);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/ai\/description\/$/);
		expect(JSON.parse(String(init.body)).save_to_catalog).toBe(true);
	});

	it('listCatalogImages -> GET /catalogs/{id}/images/', async () => {
		const fetchMock = mockApi();
		await listCatalogImages('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/images\/$/);
	});

	it('addCatalogImage -> POST /catalogs/{id}/images/', async () => {
		const fetchMock = mockApi();
		await addCatalogImage('CAT-1', { image_url: 'http://x/i.png', alt_text: 'foto', is_primary: true });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(JSON.parse(String(init.body)).is_primary).toBe(true);
	});

	it('updateCatalogImage -> PUT /catalogs/{id}/images/{iid}/', async () => {
		const fetchMock = mockApi();
		await updateCatalogImage('CAT-1', 'IMG-1', { alt_text: 'baru' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/images\/IMG-1\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('PUT');
	});

	it('deleteCatalogImage -> DELETE /catalogs/{id}/images/{iid}/', async () => {
		const fetchMock = mockApi();
		await deleteCatalogImage('CAT-1', 'IMG-1');
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('listVariantTypes -> GET /catalogs/{id}/variant-types/', async () => {
		const fetchMock = mockApi();
		await listVariantTypes('CAT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/catalogs\/CAT-1\/variant-types\/$/);
	});

	it('addVariantType -> POST /catalogs/{id}/variant-types/', async () => {
		const fetchMock = mockApi();
		await addVariantType('CAT-1', { type_name: 'Ukuran' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('createCatalogPricing (alias createPricing) tidak bertabrakan', async () => {
		const fetchMock = mockApi();
		await createPricing('CAT-1', {});
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});
});

describe('orders, quotations, tasks, team API contract', () => {
	it('listOrders -> GET /orders/', async () => {
		const fetchMock = mockApi();
		await listOrders();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/orders\/$/);
	});

	it('getOrder -> GET /orders/{id}/', async () => {
		const fetchMock = mockApi();
		await getOrder('ORD-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/orders\/ORD-1\/$/);
	});

	it('createOrder -> POST /orders/', async () => {
		const fetchMock = mockApi();
		await createOrder({ projectId: 'P-1', supplier: 'S', buyer: 'B' } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('confirmOrder -> POST /orders/{id}/confirm/', async () => {
		const fetchMock = mockApi();
		await confirmOrder('ORD-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/orders\/ORD-1\/confirm\/$/);
	});

	it('listQuotations -> GET /quotations/', async () => {
		const fetchMock = mockApi();
		await listQuotations();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/quotations\/$/);
	});

	it('getQuotation -> GET /quotations/{id}/', async () => {
		const fetchMock = mockApi();
		await getQuotation('Q-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/quotations\/Q-1\/$/);
	});

	it('createQuotation -> POST /quotations/', async () => {
		const fetchMock = mockApi();
		await createQuotation({ rfqId: 'RFQ-1', incoterm: 'FOB', value: 100, currency: 'USD', validUntil: '2026-09-01' } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('acceptQuotation -> POST /quotations/{id}/accept/', async () => {
		const fetchMock = mockApi();
		await acceptQuotation('Q-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/quotations\/Q-1\/accept\/$/);
	});

	it('completeTask -> POST /tasks/{id}/complete/', async () => {
		const fetchMock = mockApi();
		await completeTask('T-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/tasks\/T-1\/complete\/$/);
	});

	it('assignTask -> POST /tasks/{id}/assign/ dengan {owner}', async () => {
		const fetchMock = mockApi();
		await assignTask('T-1', 'Ops Lead');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/tasks\/T-1\/assign\/$/);
		expect(JSON.parse(String(init.body)).owner).toBe('Ops Lead');
	});

	it('inviteTeamMember -> POST /team/invite/ dengan email+role', async () => {
		const fetchMock = mockApi();
		await inviteTeamMember('x@y.com', 'Finance');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/team\/invite\/$/);
		expect(JSON.parse(String(init.body)).email).toBe('x@y.com');
	});

	it('updateTeamMemberRole -> PATCH /team/{id}/role/', async () => {
		const fetchMock = mockApi();
		await updateTeamMemberRole('TM-1', 'Operations' as never);
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/team\/TM-1\/role\/$/);
	});
});

describe('support, billing, api-keys, compliance, settings API contract', () => {
	it('createSupportTicket -> POST /support/', async () => {
		const fetchMock = mockApi();
		await createSupportTicket({ subject: 'Masalah', category: 'Bug', description: 'x' } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('resolveSupportTicket -> POST /support/{id}/resolve/', async () => {
		const fetchMock = mockApi();
		await resolveSupportTicket('ST-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/support\/ST-1\/resolve\/$/);
	});

	it('getBilling -> GET /billing/', async () => {
		const fetchMock = mockApi();
		await getBilling();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/billing\/$/);
	});

	it('changePlan -> POST /billing/plan/', async () => {
		const fetchMock = mockApi();
		await changePlan('Growth' as never);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/billing\/change-plan\/$/);
		expect(JSON.parse(String(init.body)).plan).toBe('Growth');
	});

	it('downloadInvoice -> POST /billing/{id}/invoice/', async () => {
		const fetchMock = mockApi();
		await downloadInvoice('INV-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/billing\/INV-1\/invoice\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('createApiKey -> POST /api-keys/ dengan name+scopes', async () => {
		const fetchMock = mockApi();
		await createApiKey('Key', ['read']);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body)).scopes).toEqual(['read']);
	});

	it('revokeApiKey -> POST /api-keys/{id}/revoke/', async () => {
		const fetchMock = mockApi();
		await revokeApiKey('AK-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api-keys\/AK-1\/revoke\/$/);
	});

	it('getComplianceRequirement -> GET /compliance/{id}/', async () => {
		const fetchMock = mockApi();
		await getComplianceRequirement('REQ-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/compliance\/requirements\/REQ-1\/$/);
	});

	it('listComplianceRequirements -> GET /compliance/', async () => {
		const fetchMock = mockApi();
		await listComplianceRequirements();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/compliance\/requirements\/$/);
	});

	it('getSettings -> GET /settings/', async () => {
		const fetchMock = mockApi();
		await getSettings();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/settings\/$/);
	});

	it('updateSettings -> PUT /settings/', async () => {
		const fetchMock = mockApi();
		await updateSettings({ companyName: 'PT X' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('PUT');
	});
});
