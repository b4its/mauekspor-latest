import { apiFetch } from '$lib/api/client';

type Fetcher<T> = () => Promise<{ data: T[]; meta?: Record<string, unknown> }>;
type GetFetcher<T> = (id: string) => Promise<{ data: T; meta?: Record<string, unknown> }>;

/** True bila error berasal dari penolakan auth/server (bukan "tidak ada"). */
export function isAuthOrServerError(err: unknown): boolean {
	const status = (err as { status?: number })?.status;
	return typeof status === 'number' && (status === 401 || status === 403 || status >= 500);
}

export function loadById<T>(getter: GetFetcher<T>, seed: T[], id: string): Promise<T | undefined> {
	return getter(id)
		.then((res) => res.data)
		.catch(() => seed.find((item) => (item as { id: string }).id === id));
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
		const seeded = seed.find((item) => item.id === id);
		if (isAuthOrServerError(err)) {
			return { record: seeded, forbidden: true };
		}
		return { record: seeded, forbidden: false };
	}
}

export function createRemoteList<T extends { id: string }>(fetcher: Fetcher<T>, seed: T[]) {
	// Deep-copy seed agar mutasi tidak mencemari array global trade.ts
	let items = $state<T[]>(seed.length ? JSON.parse(JSON.stringify(seed)) : []);
	let loading = $state(true);
	let error = $state('');

	async function load() {
		try {
			const res = await fetcher();
			mergeById(items, res.data);
			error = '';
		} catch {
			error = 'Tidak dapat memuat data dari server; menampilkan data lokal.';
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
		load,
		remove,
		upsert,
		setItems
	};
}

function mergeById<T extends { id: string }>(target: T[], remote: T[]) {
	const known = new Map(target.map((item) => [item.id, item]));
	for (const item of remote) {
		known.set(item.id, item);
	}
	target.length = 0;
	target.push(...known.values());
}