import { afterEach, describe, expect, it, vi } from 'vitest';
import { listAutomations, activateAutomation, runAutomation } from './automations';
import { listNotifications, markNotificationRead, archiveNotification } from './notifications';

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

describe('automations API contract', () => {
	it('listAutomations -> GET /automations/', async () => {
		const fetchMock = mockApi();
		await listAutomations();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/automations\/$/);
	});

	it('activateAutomation -> POST /automations/{id}/activate/', async () => {
		const fetchMock = mockApi();
		await activateAutomation('AUT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/automations\/AUT-1\/activate\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('runAutomation -> POST /automations/{id}/run/', async () => {
		const fetchMock = mockApi();
		await runAutomation('AUT-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/automations\/AUT-1\/run\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});

describe('notifications API contract', () => {
	it('listNotifications -> GET /notifications/', async () => {
		const fetchMock = mockApi();
		await listNotifications();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/notifications\/$/);
	});

	it('markNotificationRead -> POST /notifications/{id}/read/', async () => {
		const fetchMock = mockApi();
		await markNotificationRead('N-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/notifications\/N-1\/read\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('archiveNotification -> POST /notifications/{id}/archive/', async () => {
		const fetchMock = mockApi();
		await archiveNotification('N-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/notifications\/N-1\/archive\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});
