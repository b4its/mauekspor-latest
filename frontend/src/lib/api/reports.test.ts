import { afterEach, describe, expect, it, vi } from 'vitest';
import { listReports, getReport, generateReport, scheduleReport } from './reports';
import { listTemplates, createTemplate, useTemplate } from './templates';
import { listUsers, getUser, deleteUser } from './users';
import { login, register, getSession, logout, registerAdmin } from './auth';
import { listHsCodes, autocompleteHsCodes, getHsCode } from './hs-codes';
import { listIntegrations, connectIntegration, syncIntegration } from './integrations';
import { listEducationalArticles, createEducationalArticle, publishEducationalArticle } from './educational-articles';

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

describe('reports API contract', () => {
	it('listReports -> GET /reports/', async () => {
		const fetchMock = mockApi();
		await listReports();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/reports\/$/);
	});

	it('getReport -> GET /reports/{id}/', async () => {
		const fetchMock = mockApi();
		await getReport('RPT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/reports\/RPT-1\/$/);
	});

	it('generateReport -> POST /reports/{id}/generate/', async () => {
		const fetchMock = mockApi();
		await generateReport('RPT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/reports\/RPT-1\/generate\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('scheduleReport -> POST /reports/{id}/schedule/', async () => {
		const fetchMock = mockApi();
		await scheduleReport('RPT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/reports\/RPT-1\/schedule\/$/);
	});
});

describe('templates API contract', () => {
	it('listTemplates -> GET /templates/', async () => {
		const fetchMock = mockApi();
		await listTemplates();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/templates\/$/);
	});

	it('createTemplate -> POST /templates/ dengan payload', async () => {
		const fetchMock = mockApi();
		await createTemplate({ title: 'T', category: 'Document', description: 'd' });
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('useTemplate -> POST /templates/{id}/use/', async () => {
		const fetchMock = mockApi();
		await useTemplate('TPL-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/templates\/TPL-1\/use\/$/);
	});
});

describe('users API contract', () => {
	it('listUsers tanpa params -> GET /users/', async () => {
		const fetchMock = mockApi();
		await listUsers();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/users\/$/);
	});

	it('listUsers dengan params -> query search/role/limit', async () => {
		const fetchMock = mockApi();
		await listUsers({ search: 'rizal', role: 'UMKM', limit: 10 });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/users\/\?search=rizal&role=UMKM&limit=10$/);
	});

	it('getUser -> GET /users/{id}/', async () => {
		const fetchMock = mockApi();
		await getUser('U-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/users\/U-1\/$/);
	});

	it('deleteUser -> DELETE /users/{id}/', async () => {
		const fetchMock = mockApi();
		await deleteUser('U-1');
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});
});

describe('auth API contract', () => {
	it('login -> POST /auth/login/ dengan email+password', async () => {
		const fetchMock = mockApi();
		await login({ email: 'a@b.c', password: 'password123' });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/login\/$/);
		expect(JSON.parse(String(init.body)).email).toBe('a@b.c');
	});

	it('register -> POST /auth/register/', async () => {
		const fetchMock = mockApi();
		await register({ name: 'N', organization: 'O', role: 'Exporter', email: 'a@b.c', password: 'password123' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/register\/$/);
	});

	it('getSession -> GET /auth/me/', async () => {
		const fetchMock = mockApi();
		await getSession();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/me\/$/);
	});

	it('logout -> POST /auth/logout/', async () => {
		const fetchMock = mockApi();
		await logout();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/logout\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('registerAdmin -> POST /auth/register-admin/', async () => {
		const fetchMock = mockApi();
		await registerAdmin({ name: 'A', organization: 'O', role: 'Admin', email: 'a@b.c', password: 'password123', admin_code: 'X' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/register-admin\/$/);
	});
});

describe('hs-codes & integrations API contract', () => {
	it('listHsCodes -> GET /hs-codes/?search=&limit=50', async () => {
		const fetchMock = mockApi();
		await listHsCodes();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/hs-codes\/\?search=&limit=50$/);
	});

	it('autocompleteHsCodes -> GET /hs-codes/autocomplete/?q=', async () => {
		const fetchMock = mockApi();
		await autocompleteHsCodes('kopi');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/hs-codes\/autocomplete\/\?q=kopi&limit=10$/);
	});

	it('getHsCode -> GET /hs-codes/{code}/', async () => {
		const fetchMock = mockApi();
		await getHsCode('0901');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/hs-codes\/0901\/$/);
	});

	it('listIntegrations -> GET /integrations/', async () => {
		const fetchMock = mockApi();
		await listIntegrations();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/integrations\/$/);
	});

	it('connectIntegration -> POST /integrations/{id}/connect/', async () => {
		const fetchMock = mockApi();
		await connectIntegration('INT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/integrations\/INT-1\/connect\/$/);
	});

	it('syncIntegration -> POST /integrations/{id}/sync/', async () => {
		const fetchMock = mockApi();
		await syncIntegration('INT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/integrations\/INT-1\/sync\/$/);
	});
});

describe('educational-articles API contract', () => {
	it('listEducationalArticles -> GET /educational/articles/', async () => {
		const fetchMock = mockApi();
		await listEducationalArticles();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/educational\/articles\/$/);
	});

	it('createEducationalArticle -> POST /educational/articles/', async () => {
		const fetchMock = mockApi();
		await createEducationalArticle({ title: 'T', content: 'C', order_index: 1 } as never);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('publishEducationalArticle -> POST /educational/articles/{id}/publish/', async () => {
		const fetchMock = mockApi();
		await publishEducationalArticle('ART-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/educational\/articles\/ART-1\/publish\/$/);
	});
});
