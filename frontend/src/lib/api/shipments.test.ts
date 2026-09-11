import { afterEach, describe, expect, it, vi } from 'vitest';
import { listShipments, getShipment, updateShipmentMilestone, resolveShipmentException } from './shipments';
import { listPayments, getPayment, markPaymentReceived, sendPaymentReminder } from './payments';
import { listSuppliers, getSupplier, verifySupplier, requestSupplierEvidence } from './suppliers';

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

describe('shipments API contract', () => {
	it('listShipments -> GET /shipments/', async () => {
		const fetchMock = mockApi();
		await listShipments();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/shipments\/$/);
	});

	it('getShipment -> GET /shipments/{id}/', async () => {
		const fetchMock = mockApi();
		await getShipment('SHP-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/shipments\/SHP-1\/$/);
	});

	it('updateShipmentMilestone -> POST /shipments/{id}/milestones/ dengan {milestone}', async () => {
		const fetchMock = mockApi();
		await updateShipmentMilestone('SHP-1', 'In Transit');
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/shipments\/SHP-1\/milestones\/$/);
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({ milestone: 'In Transit' });
	});

	it('resolveShipmentException -> POST /shipments/{id}/exceptions/resolve/ dengan payload', async () => {
		const fetchMock = mockApi();
		await resolveShipmentException({ shipmentId: 'SHP-1', note: 'catatan', owner: 'Ops' });
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/shipments\/SHP-1\/exceptions\/resolve\/$/);
		expect(JSON.parse(String(init.body)).note).toBe('catatan');
	});
});

describe('payments API contract', () => {
	it('listPayments -> GET /payments/', async () => {
		const fetchMock = mockApi();
		await listPayments();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/payments\/$/);
	});

	it('getPayment -> GET /payments/{id}/', async () => {
		const fetchMock = mockApi();
		await getPayment('PAY-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/payments\/PAY-1\/$/);
	});

	it('markPaymentReceived -> POST /payments/{id}/mark-received/', async () => {
		const fetchMock = mockApi();
		await markPaymentReceived('PAY-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/payments\/PAY-1\/mark-received\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('sendPaymentReminder -> POST /payments/{id}/send-reminder/', async () => {
		const fetchMock = mockApi();
		await sendPaymentReminder('PAY-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/payments\/PAY-1\/send-reminder\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});

describe('suppliers API contract', () => {
	it('listSuppliers -> GET /suppliers/', async () => {
		const fetchMock = mockApi();
		await listSuppliers();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/suppliers\/$/);
	});

	it('getSupplier -> GET /suppliers/{id}/', async () => {
		const fetchMock = mockApi();
		await getSupplier('SUP-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/suppliers\/SUP-1\/$/);
	});

	it('verifySupplier -> POST /suppliers/{id}/verify/', async () => {
		const fetchMock = mockApi();
		await verifySupplier('SUP-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/suppliers\/SUP-1\/verify\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});

	it('requestSupplierEvidence -> POST /suppliers/{id}/request-evidence/', async () => {
		const fetchMock = mockApi();
		await requestSupplierEvidence('SUP-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/suppliers\/SUP-1\/request-evidence\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('POST');
	});
});
