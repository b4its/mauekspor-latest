/**
 * Sinkronisasi state filter/pencarian ke query string URL.
 *
 * Banyak halaman punya filter & kotak pencarian yang hilang saat refresh,
 * tombol back, atau dibagikan lewat tautan. Helper ini menyimpan state yang
 * bernilai ke URL tanpa memicu navigasi penuh (replaceState + noScroll),
 * dan menghapus parameter yang kembali ke nilai default agar URL tetap bersih.
 */
import { goto } from '$app/navigation';

type FilterState = Record<string, string | number | boolean | null | undefined>;

/** Nilai yang dianggap "default" dan tidak perlu muncul di URL. */
function isDefault(value: FilterState[string], fallback: FilterState[string]): boolean {
	if (value === null || value === undefined || value === '') return true;
	if (fallback === null || fallback === undefined || fallback === '') return false;
	return String(value) === String(fallback);
}

/**
 * Tulis state ke query string dengan mempertahankan parameter lain yang tidak
 * dikelola (mis. `?query=` dari deep-link halaman lain).
 */
export function syncFiltersToUrl(
	current: URL,
	state: FilterState,
	defaults: FilterState = {},
	managed: string[] = Object.keys(state)
): void {
	const params = new URLSearchParams(current.search);
	for (const [key, value] of Object.entries(state)) {
		if (isDefault(value, defaults[key])) {
			params.delete(key);
		} else {
			params.set(key, String(value));
		}
	}
	// Buang parameter yang dikelola tapi tidak lagi bernilai.
	for (const key of managed) {
		if (!(key in state)) params.delete(key);
	}
	const query = params.toString();
	const target = `${current.pathname}${query ? `?${query}` : ''}`;
	if (target === `${current.pathname}${current.search}`) return;
	void goto(target, { replaceState: true, keepFocus: true, noScroll: true });
}

/** Baca nilai string dari URL dengan fallback aman. */
export function readParam(current: URL, key: string, fallback = ''): string {
	return current.searchParams.get(key) ?? fallback;
}
