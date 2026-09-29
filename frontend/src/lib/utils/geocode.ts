/**
 * Geocoding helper — reverse & forward geocoding lewat Nominatim (OpenStreetMap).
 *
 * Dipakai oleh komponen peta lokasi (LocationMapPicker):
 * - `reverseGeocode(lat, lng)` → alamat/ jalan/ kota/ negara dari koordinat.
 * - `searchPlaces(query)` → daftar kandidat tempat untuk kotak pencarian.
 *
 * Menggunakan endpoint publik Nominatim tanpa API key (sama seperti tile OSM
 * yang sudah dipakai peta desa). Semua fungsi toleran error: mengembalikan
 * null/[] alih-alih melempar, agar UI peta tetap berfungsi bila geocoding
 * tidak tersedia. Hasil reverse di-cache per koordinat terbulatkan.
 */

export type PlaceInfo = {
	/** Koordinat tempat. */
	lat: number;
	lng: number;
	/** Alamat lengkap yang sudah diformat. */
	displayName: string;
	/** Komponen alamat terpisah (jalan, kota, provinsi, negara, kode pos). */
	road?: string;
	houseNumber?: string;
	suburb?: string;
	city?: string;
	county?: string;
	state?: string;
	postcode?: string;
	country?: string;
	countryCode?: string;
};

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';

// Cache reverse geocode: kunci = lat/lng dibulatkan 4 desimal (~11 m).
const reverseCache = new Map<string, PlaceInfo | null>();

function cacheKey(lat: number, lng: number): string {
	return `${lat.toFixed(4)},${lng.toFixed(4)}`;
}

/** Susun alamat ringkas dari komponen Nominatim. */
export function formatAddress(address?: Record<string, unknown>, displayName?: string): string {
	if (displayName) return displayName;
	if (!address) return '';
	const parts = [
		[address.house_number, address.road].filter(Boolean).join(' '),
		address.suburb || address.neighbourhood || address.village || address.hamlet,
		address.city || address.town || address.municipality || address.county,
		address.state,
		address.postcode,
		address.country
	].filter((p) => typeof p === 'string' && p.trim());
	return parts.join(', ');
}

/** Petakan respons Nominatim menjadi PlaceInfo. */
export function toPlaceInfo(raw: Record<string, any>, fallbackLat?: number, fallbackLng?: number): PlaceInfo {
	const address = (raw.address ?? {}) as Record<string, unknown>;
	const lat = Number(raw.lat ?? fallbackLat);
	const lng = Number(raw.lon ?? raw.lng ?? fallbackLng);
	return {
		lat: Number.isFinite(lat) ? lat : (fallbackLat ?? 0),
		lng: Number.isFinite(lng) ? lng : (fallbackLng ?? 0),
		displayName: String(raw.display_name ?? formatAddress(address)),
		road: address.road as string | undefined,
		houseNumber: address.house_number as string | undefined,
		suburb: (address.suburb || address.neighbourhood || address.village) as string | undefined,
		city: (address.city || address.town || address.municipality) as string | undefined,
		county: address.county as string | undefined,
		state: address.state as string | undefined,
		postcode: address.postcode as string | undefined,
		country: address.country as string | undefined,
		countryCode: (address.country_code as string)?.toUpperCase()
	};
}

/**
 * Reverse geocode koordinat → alamat. Mengembalikan null bila gagal.
 * Hasil di-cache agar klik berulang tidak memanggil jaringan terus-menerus.
 */
export async function reverseGeocode(lat: number, lng: number, signal?: AbortSignal): Promise<PlaceInfo | null> {
	if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
	const key = cacheKey(lat, lng);
	if (reverseCache.has(key)) return reverseCache.get(key) ?? null;

	try {
		const url = `${NOMINATIM_BASE}/reverse?format=jsonv2&lat=${lat}&lon=${lng}&addressdetails=1&accept-language=id,en`;
		const res = await fetch(url, { signal, headers: { Accept: 'application/json' } });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const body = (await res.json()) as Record<string, any>;
		if (!body || body.error) throw new Error('not found');
		const info = toPlaceInfo(body, lat, lng);
		reverseCache.set(key, info);
		return info;
	} catch (err) {
		// Abort (mis. komponen dilepas) bukan kegagalan → jangan cache.
		if ((err as Error)?.name === 'AbortError') return null;
		reverseCache.set(key, null);
		return null;
	}
}

export type PlaceSuggestion = {
	label: string;
	lat: number;
	lng: number;
	displayName: string;
};

/** Pencarian tempat (forward geocode) untuk kotak pencarian peta. */
export async function searchPlaces(query: string, signal?: AbortSignal, limit = 6): Promise<PlaceSuggestion[]> {
	const q = (query ?? '').trim();
	if (q.length < 3) return [];
	try {
		const url = `${NOMINATIM_BASE}/search?format=jsonv2&q=${encodeURIComponent(q)}&limit=${limit}&addressdetails=0&accept-language=id,en`;
		const res = await fetch(url, { signal, headers: { Accept: 'application/json' } });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const body = (await res.json()) as Array<Record<string, any>>;
		return body.map((item) => {
			const lat = Number(item.lat);
			const lng = Number(item.lon);
			const name = String(item.display_name ?? item.name ?? '').split(',').slice(0, 2).join(',').trim();
			return { label: name || q, lat, lng, displayName: String(item.display_name ?? '') };
		}).filter((s) => Number.isFinite(s.lat) && Number.isFinite(s.lng));
	} catch (err) {
		if ((err as Error)?.name === 'AbortError') return [];
		return [];
	}
}

/** Bersihkan cache (untuk test). */
export function _resetGeocodeCache() {
	reverseCache.clear();
}
