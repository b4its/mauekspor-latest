import type { Country } from '$lib/api/export-analysis';

export type CountryListItem = {
	country_code: string;
	country_name: string;
	region: string;
	has_details?: boolean;
	risk_level?: string;
	customs_system?: string;
	regulationsCount?: number;
};

export type CountryStats = {
	total: number;
	detailed: number;
	highRisk: number;
};

export function filterCountries(
	items: CountryListItem[],
	opts: { search?: string; region?: string; onlyDetailed?: boolean }
): CountryListItem[] {
	const search = (opts.search ?? '').trim().toLowerCase();
	const region = opts.region ?? '';
	return items.filter((c) => {
		if (search && !(c.country_name + ' ' + c.country_code).toLowerCase().includes(search)) return false;
		if (region && c.region !== region) return false;
		if (opts.onlyDetailed && !c.has_details) return false;
		return true;
	});
}

export function computeCountryStats(items: CountryListItem[]): CountryStats {
	return {
		total: items.length,
		detailed: items.filter((c) => c.has_details).length,
		highRisk: items.filter((c) => c.risk_level === 'High' || c.risk_level === 'Elevated').length,
	};
}

// ── Sumber tunggal daftar negara dunia (sinkron di semua halaman) ────────────
//
// Semua input negara (select form) memakai daftar yang SAMA dari backend
// `/countries/` (ISO 3166 alpha-2 + nama kanonik). Hasilnya di-cache di memori
// agar tidak fetch ulang tiap komponen. Nama & kode yang dipakai konsisten
// dengan halaman lain (direktori negara, analisis ekspor, regulasi, dll).

let cache: CountryListItem[] | null = null;
let inflight: Promise<CountryListItem[]> | null = null;

/** Normalisasi entri negara ke bentuk minimal yang dipakai select. */
export function toCountryListItem(c: Country): CountryListItem {
	return {
		country_code: String(c.country_code ?? '').toUpperCase(),
		country_name: c.country_name ?? String(c.country_code ?? ''),
		region: c.region ?? '',
		has_details: c.has_details,
		risk_level: c.risk_level,
		customs_system: c.customs_system,
		regulationsCount: c.regulationsCount
	};
}

/**
 * Muat daftar negara dunia dari backend, dengan cache. Aman dipanggil berulang:
 * request yang berjalan akan dishare (dedupe).
 */
export async function loadWorldCountries(): Promise<CountryListItem[]> {
	if (cache) return cache;
	if (inflight) return inflight;
	const { listCountries } = await import('$lib/api/export-analysis');
	inflight = listCountries()
		.then((res) => {
			const items = (res.data ?? []).map(toCountryListItem).filter((c) => c.country_code);
			items.sort((a, b) => a.country_name.localeCompare(b.country_name));
			cache = items;
			return items;
		})
		.finally(() => {
			inflight = null;
		});
	return inflight;
}

/** Setel ulang cache (mis. untuk test). */
export function _resetCountryCache() {
	cache = null;
	inflight = null;
}

export type CountryOption = { value: string; label: string; sub?: string };

/**
 * Bentuk opsi select dari daftar negara. `value` = kode ISO, `label` = nama
 * kanonik, `sub` = kode + region. Konsisten dengan seluruh halaman.
 */
export function toCountryOptions(items: CountryListItem[]): CountryOption[] {
	return items.map((c) => ({
		value: c.country_code,
		label: c.country_name,
		sub: c.region ? `${c.country_code} — ${c.region}` : c.country_code
	}));
}

/**
 * Terjemahkan sebuah nilai negara (kode ISO ATAU nama) menjadi nama kanonik.
 * Dipakai agar nilai lama (mis. teks "Japan") tampil konsisten sebagai nama
 * resmi. Bila tak dikenali, kembalikan nilai aslinya apa adanya.
 */
export function resolveCountryName(value: string, items: CountryListItem[]): string {
	const v = (value ?? '').trim();
	if (!v) return '';
	const upper = v.toUpperCase();
	const byCode = items.find((c) => c.country_code.toUpperCase() === upper);
	if (byCode) return byCode.country_name;
	const lower = v.toLowerCase();
	const byName = items.find((c) => c.country_name.toLowerCase() === lower);
	return byName ? byName.country_name : v;
}

/**
 * Terjemahkan sebuah nilai negara menjadi kode ISO bila mungkin (untuk menyimpan
 * kode kanonik). Bila berupa nama yang dikenali → kode; bila sudah kode → kode;
 * selain itu kembalikan nilai aslinya.
 */
export function resolveCountryCode(value: string, items: CountryListItem[]): string {
	const v = (value ?? '').trim();
	if (!v) return '';
	const upper = v.toUpperCase();
	if (items.some((c) => c.country_code.toUpperCase() === upper)) return upper;
	const lower = v.toLowerCase();
	const byName = items.find((c) => c.country_name.toLowerCase() === lower);
	return byName ? byName.country_code : v;
}
