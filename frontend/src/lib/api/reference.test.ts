import { afterEach, describe, expect, it, vi } from 'vitest';
import { getReference } from './reference';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data
	} as unknown as Response;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('reference api', () => {
	it('getReference -> GET /reference/', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data: { snapshotDate: '2026-09-29' } }));
		vi.stubGlobal('fetch', fetchMock);
		const res = await getReference();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/reference\/?$/);
		const opts = fetchMock.mock.calls[0][1] as RequestInit;
		expect((opts?.method ?? 'GET').toUpperCase()).toBe('GET');
		expect(res.data.snapshotDate).toBe('2026-09-29');
	});
});
