import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	loadWorldCountries,
	toCountryOptions,
	toCountryListItem,
	resolveCountryName,
	resolveCountryCode,
	_resetCountryCache,
	type CountryListItem
} from './countries';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data
	} as unknown as Response;
}

const sample = [
	{ country_code: 'jp', country_name: 'Japan', region: 'Asia' },
	{ country_code: 'ID', country_name: 'Indonesia', region: 'Asia' },
	{ country_code: 'US', country_name: 'United States', region: 'Americas' }
];

afterEach(() => {
	vi.unstubAllGlobals();
	_resetCountryCache();
});

describe('countries loader', () => {
	it('memuat dari /countries/ dan menormalkan kode + urut nama', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data: sample }));
		vi.stubGlobal('fetch', fetchMock);
		const items = await loadWorldCountries();
		expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/v1\/countries\/$/);
		expect(items.map((c) => c.country_code)).toEqual(['ID', 'JP', 'US']); // terurut nama
	});

	it('meng-cache hasil (fetch sekali saja)', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data: sample }));
		vi.stubGlobal('fetch', fetchMock);
		await loadWorldCountries();
		await loadWorldCountries();
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});
});

describe('toCountryListItem', () => {
	it('uppercase kode dan pertahankan nama', () => {
		const item = toCountryListItem({ country_code: 'jp', country_name: 'Japan', region: 'Asia' });
		expect(item).toEqual({ country_code: 'JP', country_name: 'Japan', region: 'Asia' });
	});
});

describe('toCountryOptions', () => {
	it('value=kode, label=nama kanonik, sub=kode—region', () => {
		const items: CountryListItem[] = sample.map((c) => toCountryListItem(c as never));
		const opts = toCountryOptions(items);
		expect(opts[0]).toEqual({ value: 'JP', label: 'Japan', sub: 'JP — Asia' });
	});
});

describe('resolveCountryName / resolveCountryCode', () => {
	const items = sample.map((c) => toCountryListItem(c as never));

	it('menerjemahkan kode ke nama kanonik', () => {
		expect(resolveCountryName('jp', items)).toBe('Japan');
		expect(resolveCountryName('US', items)).toBe('United States');
	});

	it('menerjemahkan nama ke kode kanonik', () => {
		expect(resolveCountryCode('Japan', items)).toBe('JP');
		expect(resolveCountryCode('indonesia', items)).toBe('ID');
	});

	it('nilai tak dikenal dikembalikan apa adanya', () => {
		expect(resolveCountryName('Atlantis', items)).toBe('Atlantis');
		expect(resolveCountryCode('Atlantis', items)).toBe('Atlantis');
		expect(resolveCountryName('', items)).toBe('');
	});
});
