import { afterEach, describe, expect, it, vi } from 'vitest';
import { previewFileAsset, analyzeFileAsset } from './files';

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

describe('files api', () => {
	it('previewFileAsset -> GET /files/{id}/preview/', async () => {
		const fetchMock = mockApi();
		await previewFileAsset('FIL-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/files\/FIL-1\/preview\/?$/);
		const opts = fetchMock.mock.calls[0][1] as RequestInit;
		expect((opts?.method ?? 'GET').toUpperCase()).toBe('GET');
	});

	it('analyzeFileAsset -> POST /files/{id}/analyze/', async () => {
		const fetchMock = mockApi();
		await analyzeFileAsset('FIL-2');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/files\/FIL-2\/analyze\/?$/);
		const opts = fetchMock.mock.calls[0][1] as RequestInit;
		expect(opts?.method).toBe('POST');
	});
});
