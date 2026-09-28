/**
 * Pengurutan generik untuk daftar di sisi klien.
 *
 * Halaman list memuat seluruh baris (createRemoteList) lalu memfilter dan
 * memaginasi di klien. Helper ini menyatukan logika pengurutan agar kontrol
 * "Urutkan" di toolbar punya perilaku yang konsisten di semua halaman:
 * angka dibandingkan sebagai angka (termasuk angka tersimpan sebagai teks),
 * tanggal/ISO-string dibandingkan apa adanya, sisanya sebagai teks
 * case-insensitive dengan locale aktif.
 */

export type SortDir = 'asc' | 'desc';

/** Deskripsi satu opsi pengurutan yang bisa dipilih pengguna. */
export type SortOption = {
	/** Nilai yang dikirim/disimpan (biasanya nama field). */
	value: string;
	/** Label yang ditampilkan (sudah diterjemahkan). */
	label: string;
};

/** Kunci default saat tidak ada pengurutan aktif. */
export const SORT_NONE = '';

function isNumeric(value: unknown): boolean {
	if (typeof value === 'number') return !Number.isNaN(value);
	if (typeof value === 'string' && value.trim() !== '') {
		return Number.isFinite(Number(value.replace(/[\s,]/g, '')));
	}
	return false;
}

function numericValue(value: unknown): number {
	if (typeof value === 'number') return value;
	return Number(String(value).replace(/[\s,]/g, ''));
}

/**
 * Urutkan array tanpa memutasi input.
 *
 * @param items    Data sumber.
 * @param key      Nama field; string kosong = kembalikan apa adanya.
 * @param dir      'asc' | 'desc'.
 * @param locale   Locale untuk pembandingan teks (default 'id').
 */
export function sortBy<T extends Record<string, unknown>>(
	items: T[],
	key: string,
	dir: SortDir = 'asc',
	locale = 'id'
): T[] {
	if (!key) return items;
	const factor = dir === 'desc' ? -1 : 1;
	// Salin agar tidak memutasi array sumber (dipakai $derived).
	return [...items].sort((a, b) => {
		const av = a[key];
		const bv = b[key];
		if (isNumeric(av) && isNumeric(bv)) {
			return (numericValue(av) - numericValue(bv)) * factor;
		}
		const as = av === null || av === undefined ? '' : String(av);
		const bs = bv === null || bv === undefined ? '' : String(bv);
		return as.localeCompare(bs, locale, { numeric: true, sensitivity: 'base' }) * factor;
	});
}

/** Balik arah pengurutan. */
export function toggleDir(dir: SortDir): SortDir {
	return dir === 'asc' ? 'desc' : 'asc';
}
