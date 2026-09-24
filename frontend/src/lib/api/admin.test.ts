import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listAdminTables,
	listAdminRecords,
	getAdminRecord,
	createAdminRecord,
	updateAdminRecord,
	deleteAdminRecord,
	getAiStatus,
	testAi
} from './admin';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data
	} as unknown as Response;
}

function mockApi<T = unknown>(data: T = {} as T) {
	const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data }));
	vi.stubGlobal('fetch', fetchMock);
	return fetchMock;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('admin API client contract', () => {
	it('listAdminTables -> GET /admin/tables/', async () => {
		const fetchMock = mockApi([{ name: 'users', count: 10 }]);
		const res = await listAdminTables();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/tables\/$/);
		expect(res.data[0].name).toBe('users');
	});

	it('listAdminRecords -> GET /admin/data/{table}/ with pagination params', async () => {
		const fetchMock = mockApi([{ id: 'USR-1', name: 'Admin' }]);
		const res = await listAdminRecords('users', { search: 'Admin', limit: 10, offset: 0 });
		const url = String(fetchMock.mock.calls[0][0]);
		expect(url).toMatch(/\/api\/v1\/admin\/data\/users\/\?/);
		expect(url).toContain('search=Admin');
		expect(url).toContain('limit=10');
		expect(res.data[0].id).toBe('USR-1');
	});

	it('getAdminRecord -> GET /admin/data/{table}/{id}/', async () => {
		const fetchMock = mockApi({ id: 'USR-1', name: 'Admin' });
		const res = await getAdminRecord('users', 'USR-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/data\/users\/USR-1\/$/);
		expect(res.data.id).toBe('USR-1');
	});

	it('createAdminRecord -> POST /admin/data/{table}/', async () => {
		const fetchMock = mockApi({ id: 'USR-2', name: 'Exporter' });
		const res = await createAdminRecord('users', { name: 'Exporter' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/data\/users\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({ name: 'Exporter' });
		expect(res.data.id).toBe('USR-2');
	});

	it('updateAdminRecord -> PUT /admin/data/{table}/{id}/', async () => {
		const fetchMock = mockApi({ id: 'USR-1', name: 'SuperAdmin' });
		const res = await updateAdminRecord('users', 'USR-1', { name: 'SuperAdmin' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/data\/users\/USR-1\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('PUT');
		expect(JSON.parse(String(init.body))).toEqual({ name: 'SuperAdmin' });
		expect(res.data.name).toBe('SuperAdmin');
	});

	it('deleteAdminRecord -> DELETE /admin/data/{table}/{id}/', async () => {
		const fetchMock = mockApi({ status: 'deleted' });
		const res = await deleteAdminRecord('users', 'USR-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/data\/users\/USR-1\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('DELETE');
		expect(res.data.status).toBe('deleted');
	});

	it('getAiStatus -> GET /ai/status/', async () => {
		const fetchMock = mockApi({
			mode: 'mock',
			health: 'healthy',
			using_remote: false,
			using_mock: true
		});
		const res = await getAiStatus();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/ai\/status\/$/);
		expect(res.data.mode).toBe('mock');
		expect(res.data.health).toBe('healthy');
	});

	it('testAi -> POST /ai/test/', async () => {
		const fetchMock = mockApi({
			response: 'Tes AI berhasil',
			ai_mode: 'mock',
			ai_health: 'healthy',
			success: true
		});
		const res = await testAi();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/ai\/test\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(res.data.success).toBe(true);
	});
});
