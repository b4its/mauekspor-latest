import { afterEach, describe, expect, it, vi } from 'vitest';
import { getModuleQuiz, submitModuleQuiz } from './educational';

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

describe('educational quiz api', () => {
	it('getModuleQuiz -> GET /educational/modules/{id}/quiz/', async () => {
		const fetchMock = mockApi();
		await getModuleQuiz('EDU-DES-PANEN-01');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/educational\/modules\/EDU-DES-PANEN-01\/quiz\/?$/);
		const opts = fetchMock.mock.calls[0][1] as RequestInit;
		expect((opts?.method ?? 'GET').toUpperCase()).toBe('GET');
	});

	it('submitModuleQuiz -> POST .../quiz/submit/ with answers body', async () => {
		const fetchMock = mockApi();
		await submitModuleQuiz('EDU-DES-PANEN-01', { 'q-1': 2 });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/educational\/modules\/EDU-DES-PANEN-01\/quiz\/submit\/?$/);
		const opts = fetchMock.mock.calls[0][1] as RequestInit;
		expect(opts?.method).toBe('POST');
		expect(JSON.parse(String(opts?.body))).toEqual({ answers: { 'q-1': 2 } });
	});
});
