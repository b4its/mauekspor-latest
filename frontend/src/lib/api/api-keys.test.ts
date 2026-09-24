import { describe, expect, it, vi } from 'vitest';
import { listApiKeys, createApiKey, revokeApiKey, deleteApiKey } from './api-keys';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data,
		text: async () => JSON.stringify(data)
	} as unknown as Response;
}

function mockApi<T = unknown>(data: T = {} as T) {
	const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data }));
	vi.stubGlobal('fetch', fetchMock);
	return fetchMock;
}

describe('api-keys api', () => {
	it('listApiKeys memanggil GET /api/v1/api-keys/', async () => {
		const fetchMock = mockApi([{ id: 'KEY-1', name: 'Dev Key' }]);
		const res = await listApiKeys();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/api-keys\/$/);
		expect(res.data).toHaveLength(1);
	});

	it('createApiKey memanggil POST /api/v1/api-keys/ dengan body name dan scopes', async () => {
		const fetchMock = mockApi({ id: 'KEY-2', name: 'Prod Key', scopes: ['catalogs:read'] });
		const res = await createApiKey('Prod Key', ['catalogs:read']);
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/api-keys\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(init.body as string)).toEqual({ name: 'Prod Key', scopes: ['catalogs:read'] });
		expect(res.data.id).toBe('KEY-2');
	});

	it('revokeApiKey memanggil POST /api/v1/api-keys/{id}/revoke/', async () => {
		const fetchMock = mockApi({ id: 'KEY-1', status: 'Revoked' });
		const res = await revokeApiKey('KEY-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/api-keys\/KEY-1\/revoke\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(res.data.status).toBe('Revoked');
	});

	it('deleteApiKey memanggil DELETE /api/v1/api-keys/{id}/', async () => {
		const fetchMock = mockApi({ deleted: true });
		const res = await deleteApiKey('KEY-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/api-keys\/KEY-1\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('DELETE');
		expect(res.data.deleted).toBe(true);
	});
});
