import { apiFetch } from '$lib/api/client';

type Fetcher<T> = () => Promise<{ data: T[]; meta?: Record<string, unknown> }>;
type GetFetcher<T> = (id: string) => Promise<{ data: T; meta?: Record<string, unknown> }>;

export function loadById<T>(getter: GetFetcher<T>, seed: T[], id: string): Promise<T | undefined> {
	return getter(id)
		.then((res) => res.data)
		.catch(() => seed.find((item) => (item as { id: string }).id === id));
}

export function createRemoteList<T extends { id: string }>(fetcher: Fetcher<T>, seed: T[]) {
	// Salin seed agar mutasi mergeById tidak mencemari array global (mis. dari trade.ts)
	let items = $state<T[]>([...seed]);
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
		load
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