import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listMessages,
	sendMessage,
	resolveMessageThread,
	updateMessageThread,
	createMessageThread,
	deleteMessageThread
} from './messages';

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

describe('messages API client contract', () => {
	it('listMessages -> GET /messages/', async () => {
		const fetchMock = mockApi([{ id: 'MSG-001', subject: 'Inquiry' }]);
		const res = await listMessages();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/$/);
		expect(res.data[0].id).toBe('MSG-001');
	});

	it('createMessageThread -> POST /messages/', async () => {
		const fetchMock = mockApi({ id: 'MSG-002', subject: 'New Thread' });
		const res = await createMessageThread({ subject: 'New Thread', channel: 'Email' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({ subject: 'New Thread', channel: 'Email' });
		expect(res.data.id).toBe('MSG-002');
	});

	it('sendMessage -> POST /messages/{id}/send/', async () => {
		const fetchMock = mockApi({ id: 'MSG-001', lastMessage: 'Reply' });
		const res = await sendMessage('MSG-001', 'Reply');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/MSG-001\/send\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({ body: 'Reply' });
		expect(res.data.lastMessage).toBe('Reply');
	});

	it('resolveMessageThread -> POST /messages/{id}/resolve/', async () => {
		const fetchMock = mockApi({ id: 'MSG-001', status: 'Resolved' });
		const res = await resolveMessageThread('MSG-001');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/MSG-001\/resolve\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(res.data.status).toBe('Resolved');
	});

	it('updateMessageThread -> PATCH /messages/{id}/', async () => {
		const fetchMock = mockApi({ id: 'MSG-001', status: 'Open' });
		const res = await updateMessageThread('MSG-001', { status: 'Open' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/MSG-001\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('PATCH');
		expect(JSON.parse(String(init.body))).toEqual({ status: 'Open' });
		expect(res.data.status).toBe('Open');
	});

	it('deleteMessageThread -> DELETE /messages/{id}/', async () => {
		const fetchMock = mockApi({ status: 'deleted', id: 'MSG-001' });
		const res = await deleteMessageThread('MSG-001');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/messages\/MSG-001\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('DELETE');
		expect(res.data.status).toBe('deleted');
	});
});
