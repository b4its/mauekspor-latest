import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listVillages,
	getVillage,
	createVillage,
	updateVillage,
	deleteVillage
} from './villages';

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

describe('villages API client contract', () => {
	it('listVillages -> GET /villages/ with query params', async () => {
		const fetchMock = mockApi([{ id: 'DES-GAYO', name: 'Desa Kopi Gayo' }]);
		const res = await listVillages({ search: 'Gayo', province: 'Aceh' });
		const url = String(fetchMock.mock.calls[0][0]);
		expect(url).toMatch(/\/api\/v1\/villages\/\?/);
		expect(url).toContain('search=Gayo');
		expect(url).toContain('province=Aceh');
		expect(res.data[0].id).toBe('DES-GAYO');
	});

	it('getVillage -> GET /villages/{id}/', async () => {
		const fetchMock = mockApi({ id: 'DES-GAYO', name: 'Desa Kopi Gayo', products: [] });
		const res = await getVillage('DES-GAYO');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/villages\/DES-GAYO\/$/);
		expect(res.data.name).toBe('Desa Kopi Gayo');
	});

	it('createVillage -> POST /villages/', async () => {
		const fetchMock = mockApi({ id: 'DES-NEW', name: 'Desa Kakao Baru' });
		const res = await createVillage({ name: 'Desa Kakao Baru', readiness: 85 });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/villages\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({ name: 'Desa Kakao Baru', readiness: 85 });
		expect(res.data.id).toBe('DES-NEW');
	});

	it('updateVillage -> PUT /villages/{id}/', async () => {
		const fetchMock = mockApi({ id: 'DES-GAYO', readiness: 95 });
		const res = await updateVillage('DES-GAYO', { readiness: 95 });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/villages\/DES-GAYO\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('PUT');
		expect(JSON.parse(String(init.body))).toEqual({ readiness: 95 });
		expect(res.data.readiness).toBe(95);
	});

	it('deleteVillage -> DELETE /villages/{id}/', async () => {
		const fetchMock = mockApi({ status: 'deleted', id: 'DES-GAYO' });
		const res = await deleteVillage('DES-GAYO');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/villages\/DES-GAYO\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('DELETE');
		expect(res.data.status).toBe('deleted');
	});
});
