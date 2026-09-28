import { apiFetch } from '$lib/api/client';

type Fetcher<T> = () => Promise<{ data: T[]; meta?: Record<string, unknown> }>;
type GetFetcher<T> = (id: string) => Promise<{ data: T; meta?: Record<string, unknown> }>;

/**
 * Demo/local-data mode (PRD §5.11 G-09 "Truth in UI").
 *
 * Default OFF: bila API gagal, JANGAN perlakukan seed demo sebagai data bisnis
 * valid — tampilkan daftar kosong + error agar staf tidak mengambil keputusan
 * atas data fiktif. Set VITE_DEMO_DATA=1 (atau ?demo=1 di URL) untuk mengaktifkan
 * fallback seed saat presentasi/demo offline.
 */
// Override runtime untuk test / pemanggilan programatik.
let _demoOverride: boolean | null = null;

/** Paksa mode demo on/off (dipakai test; null = kembali ke env/URL). */
export function setDemoDataMode(enabled: boolean | null): void {
	_demoOverride = enabled;
}

function truthy(value: unknown): boolean {
	return ['1', 'true', 'yes'].includes(String(value ?? '').toLowerCase());
}

function demoDataEnabled(): boolean {
	if (_demoOverride !== null) return _demoOverride;
	const envFlag =
		typeof import.meta !== 'undefined' && (import.meta as { env?: Record<string, string> }).env
			? (import.meta as { env?: Record<string, string> }).env?.VITE_DEMO_DATA
			: undefined;
	if (truthy(envFlag)) return true;
	if (typeof window !== 'undefined') {
		try {
			const url = new URL(window.location.href);
			if (truthy(url.searchParams.get('demo'))) return true;
		} catch {
			/* abaikan */
		}
	}
	return false;
}

/** True bila error berasal dari penolakan auth/server (bukan "tidak ada"). */
export function isAuthOrServerError(err: unknown): boolean {
	const status = (err as { status?: number })?.status;
	return typeof status === 'number' && (status === 401 || status === 403 || status >= 500);
}

export function loadById<T>(getter: GetFetcher<T>, seed: T[], id: string): Promise<T | undefined> {
	return getter(id)
		.then((res) => res.data)
		.catch(() => (demoDataEnabled() ? seed.find((item) => (item as { id: string }).id === id) : undefined));
}

export type LoadedRecord<T> = {
	/** Data dari API (atau seed sebagai fallback). */
	record: T | undefined;
	/** True bila server menolak (401/403/5xx) ATAU record tak terverifikasi —
	 * halaman harus tetap dirender agar klien (yang punya token) bisa memuat ulang,
	 * bukan di-404. */
	forbidden: boolean;
};

/**
 * Loader id yang aman untuk SSR: bila API menolak karena auth (SSR tidak punya
 * token), JANGAN mengembalikan 404 — kembalikan seed/undefined + `forbidden`
 * agar halaman tetap render dan memuat ulang di klien.
 */
export async function loadRecord<T extends { id: string }>(
	getter: GetFetcher<T>,
	seed: T[],
	id: string
): Promise<LoadedRecord<T>> {
	try {
		const res = await getter(id);
		return { record: res.data, forbidden: false };
	} catch (err) {
		// Seed hanya sebagai fallback di mode demo (PRD G-09). Selain itu,
		// jangan tampilkan record lokal palsu; biarkan halaman menangani 404/err.
		const seeded = demoDataEnabled() ? seed.find((item) => item.id === id) : undefined;
		if (isAuthOrServerError(err)) {
			return { record: seeded, forbidden: true };
		}
		return { record: seeded, forbidden: false };
	}
}

export function createRemoteList<T extends { id: string }>(fetcher: Fetcher<T>, seed: T[]) {
	// Seed hanya dipakai sebagai fallback saat mode demo aktif (default: tidak).
	let items = $state<T[]>([]);
	let loading = $state(true);
	let error = $state('');
	// True bila data yang tampil berasal dari seed lokal karena server gagal.
	let usingFallback = $state(false);

	async function load() {
		try {
			const res = await fetcher();
			setItems(res.data);
			error = '';
			usingFallback = false;
		} catch {
			if (demoDataEnabled() && seed.length) {
				// Deep-copy seed agar mutasi tidak mencemari array global trade.ts
				setItems(JSON.parse(JSON.stringify(seed)));
				usingFallback = true;
				error = 'Mode demo: data lokal ditampilkan karena server tidak tersedia.';
			} else {
				setItems([]);
				usingFallback = false;
				error = 'Tidak dapat memuat data dari server. Coba muat ulang.';
			}
		} finally {
			loading = false;
		}
	}

	function remove(id: string) {
		const idx = items.findIndex((item) => item.id === id);
		if (idx >= 0) {
			items.splice(idx, 1);
		}
	}

	function upsert(item: T) {
		const idx = items.findIndex((i) => i.id === item.id);
		if (idx >= 0) {
			items[idx] = item;
		} else {
			items.unshift(item);
		}
	}

	function setItems(newItems: T[]) {
		items.length = 0;
		items.push(...newItems);
	}

	return {
		get items() {
			return items;
		},
		get loading() {
			return loading;
		},
		get error() {
			return error;
		},
		get usingFallback() {
			return usingFallback;
		},
		load,
		remove,
		upsert,
		setItems
	};
}
