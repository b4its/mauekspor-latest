import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	reverseGeocode,
	searchPlaces,
	formatAddress,
	toPlaceInfo,
	_resetGeocodeCache
} from './geocode';

function jsonResponse(status: number, body: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: () => 'application/json' },
		json: async () => body
	} as unknown as Response;
}

afterEach(() => {
	vi.unstubAllGlobals();
	_resetGeocodeCache();
});

describe('formatAddress', () => {
	it('mengutamakan display_name bila ada', () => {
		expect(formatAddress({ road: 'Jalan X' }, 'Full Address')).toBe('Full Address');
	});

	it('menyusun alamat dari komponen', () => {
		const addr = { house_number: '12', road: 'Jalan Merdeka', city: 'Bandung', state: 'Jawa Barat', country: 'Indonesia' };
		expect(formatAddress(addr)).toBe('12 Jalan Merdeka, Bandung, Jawa Barat, Indonesia');
	});

	it('kosong bila tidak ada data', () => {
		expect(formatAddress(undefined)).toBe('');
	});
});

describe('toPlaceInfo', () => {
	it('memetakan respons Nominatim', () => {
		const info = toPlaceInfo({
			lat: '-6.2',
			lon: '106.8166',
			display_name: 'Jakarta, Indonesia',
			address: { city: 'Jakarta', state: 'DKI Jakarta', country: 'Indonesia', country_code: 'id' }
		});
		expect(info.lat).toBeCloseTo(-6.2);
		expect(info.lng).toBeCloseTo(106.8166);
		expect(info.displayName).toBe('Jakarta, Indonesia');
		expect(info.city).toBe('Jakarta');
		expect(info.countryCode).toBe('ID');
	});
});

describe('reverseGeocode', () => {
	it('memanggil Nominatim reverse dan mengembalikan PlaceInfo', async () => {
		const fetchMock = vi.fn().mockResolvedValue(
			jsonResponse(200, {
				lat: '4.6306',
				lon: '96.8474',
				display_name: 'Bebesen, Aceh Tengah, Aceh, Indonesia',
				address: { road: 'Jalan Utama', city: 'Takengon', state: 'Aceh', country: 'Indonesia', country_code: 'id' }
			})
		);
		vi.stubGlobal('fetch', fetchMock);
		const info = await reverseGeocode(4.6306, 96.8474);
		expect(String(fetchMock.mock.calls[0][0])).toContain('/reverse?');
		expect(info?.displayName).toContain('Aceh');
		expect(info?.countryCode).toBe('ID');
	});

	it('meng-cache hasil per koordinat (fetch sekali)', async () => {
		const fetchMock = vi.fn().mockResolvedValue(
			jsonResponse(200, { lat: '1', lon: '1', display_name: 'X', address: {} })
		);
		vi.stubGlobal('fetch', fetchMock);
		await reverseGeocode(1, 1);
		await reverseGeocode(1, 1);
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});

	it('mengembalikan null bila gagal / koordinat tidak valid', async () => {
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(500, {})));
		expect(await reverseGeocode(1, 1)).toBeNull();
		expect(await reverseGeocode(NaN, 10)).toBeNull();
	});
});

describe('searchPlaces', () => {
	it('mengembalikan kosong untuk query pendek', async () => {
		const fetchMock = vi.fn();
		vi.stubGlobal('fetch', fetchMock);
		expect(await searchPlaces('ab')).toEqual([]);
		expect(fetchMock).not.toHaveBeenCalled();
	});

	it('memetakan hasil pencarian tempat', async () => {
		const fetchMock = vi.fn().mockResolvedValue(
			jsonResponse(200, [
				{ lat: '-6.2', lon: '106.8', display_name: 'Jakarta, Indonesia', name: 'Jakarta' }
			])
		);
		vi.stubGlobal('fetch', fetchMock);
		const res = await searchPlaces('Jakarta');
		expect(String(fetchMock.mock.calls[0][0])).toContain('/search?');
		expect(res).toHaveLength(1);
		expect(res[0].lat).toBeCloseTo(-6.2);
		expect(res[0].lng).toBeCloseTo(106.8);
	});

	it('toleran terhadap kegagalan jaringan', async () => {
		vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
		expect(await searchPlaces('Jakarta')).toEqual([]);
	});
});
