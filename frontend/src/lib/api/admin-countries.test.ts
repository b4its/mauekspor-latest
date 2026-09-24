import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	listAdminCountries,
	createAdminCountry,
	updateAdminCountry,
	deleteAdminCountry,
	listAdminRegulations,
	createAdminRegulation,
	updateAdminRegulation,
	deleteAdminRegulation,
	importAdminRegulations,
	type AdminCountry,
	type AdminRegulation
} from './admin-countries';

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

describe('admin-countries API contract', () => {
	it('listAdminCountries -> GET /countries/', async () => {
		const fetchMock = mockApi<AdminCountry[]>([
			{ id: 'CTY-1', country_code: 'JP', country_name: 'Japan', region: 'Asia' }
		]);
		const res = await listAdminCountries();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/countries\/$/);
		expect(res.data[0].country_code).toBe('JP');
	});

	it('createAdminCountry -> POST /admin/countries/', async () => {
		const fetchMock = mockApi();
		await createAdminCountry({ country_code: 'jp', country_name: 'Japan', region: 'Asia' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/countries\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({ country_code: 'jp', country_name: 'Japan', region: 'Asia' });
	});

	it('updateAdminCountry -> PUT /admin/countries/{code}/', async () => {
		const fetchMock = mockApi();
		await updateAdminCountry('JP', { country_name: 'Jepang', region: 'Asia' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/countries\/JP\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('PUT');
		expect(JSON.parse(String(init.body))).toEqual({ country_name: 'Jepang', region: 'Asia' });
	});

	it('deleteAdminCountry -> DELETE /admin/countries/{code}/delete/', async () => {
		const fetchMock = mockApi();
		await deleteAdminCountry('JP');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/countries\/JP\/delete\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('listAdminRegulations -> GET /admin/countries/{code}/regulations/', async () => {
		const fetchMock = mockApi<AdminRegulation[]>([
			{ id: 'REG-1', country_code: 'JP', rule_category: 'Labeling', forbidden_keywords: 'x', required_specs: 'y', description_rule: 'z' }
		]);
		const res = await listAdminRegulations('JP');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/countries\/JP\/regulations\/$/);
		expect(res.data[0].rule_category).toBe('Labeling');
	});

	it('listAdminRegulations with category filter', async () => {
		const fetchMock = mockApi();
		await listAdminRegulations('JP', 'Customs');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/rule_category=Customs$/);
	});

	it('createAdminRegulation -> POST /admin/countries/{code}/regulations/create/', async () => {
		const fetchMock = mockApi();
		await createAdminRegulation('JP', { rule_category: 'Labeling', forbidden_keywords: 'a', required_specs: 'b', description_rule: 'c' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/countries\/JP\/regulations\/create\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(JSON.parse(String(init.body))).toEqual({
			rule_category: 'Labeling',
			forbidden_keywords: 'a',
			required_specs: 'b',
			description_rule: 'c'
		});
	});

	it('updateAdminRegulation -> PUT /admin/regulations/{id}/', async () => {
		const fetchMock = mockApi();
		await updateAdminRegulation('REG-1', { rule_category: 'Customs', forbidden_keywords: '', required_specs: '', description_rule: '' });
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/regulations\/REG-1\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('PUT');
	});

	it('deleteAdminRegulation -> DELETE /admin/regulations/{id}/delete/', async () => {
		const fetchMock = mockApi();
		await deleteAdminRegulation('REG-1');
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/regulations\/REG-1\/delete\/$/);
		expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe('DELETE');
	});

	it('importAdminRegulations -> POST /admin/regulations/import/ (multipart)', async () => {
		const fetchMock = mockApi({ imported: 3 });
		const file = new File(['a,b\n1,2'], 'reg.csv', { type: 'text/csv' });
		const res = await importAdminRegulations(file);
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/admin\/regulations\/import\/$/);
		const init = fetchMock.mock.calls[0][1] as RequestInit;
		expect(init.method).toBe('POST');
		expect(res.data.imported).toBe(3);
	});
});
