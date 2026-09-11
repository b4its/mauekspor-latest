import { describe, expect, it, vi } from 'vitest';
import { createRemoteList, loadById } from './remote-list.svelte';

describe('createRemoteList', () => {
	const seed = [
		{ id: 'a', name: 'Seed A' },
		{ id: 'b', name: 'Seed B' }
	];

	it('memulai dengan seed dan loading true', () => {
		const list = createRemoteList(async () => ({ data: [] }), seed);
		expect(list.items).toHaveLength(2);
		expect(list.loading).toBe(true);
		expect(list.error).toBe('');
	});

	it('load() menggabungkan data remote (update + tambah) tanpa duplikasi', async () => {
		const fetcher = vi.fn().mockResolvedValue({
			data: [
				{ id: 'a', name: 'Seed A UPDATED' },
				{ id: 'c', name: 'Remote C' }
			]
		});
		const list = createRemoteList(fetcher, seed);
		await list.load();

		expect(fetcher).toHaveBeenCalledTimes(1);
		expect(list.items).toHaveLength(3); // a (updated), b, c
		expect(list.items.find((i) => i.id === 'a')?.name).toBe('Seed A UPDATED');
		expect(list.items.find((i) => i.id === 'c')?.name).toBe('Remote C');
		expect(list.loading).toBe(false);
		expect(list.error).toBe('');
	});

	it('load() menampilkan error dan tetap memakai seed saat fetcher gagal', async () => {
		const fetcher = vi.fn().mockRejectedValue(new Error('network down'));
		const list = createRemoteList(fetcher, seed);
		await list.load();

		expect(list.items).toHaveLength(2);
		expect(list.error).toContain('Tidak dapat memuat data dari server');
		expect(list.loading).toBe(false);
	});

	it('load() dapat dipanggil berulang', async () => {
		const fetcher = vi.fn().mockResolvedValue({ data: [{ id: 'a', name: 'X' }] });
		const list = createRemoteList(fetcher, seed);
		await list.load();
		await list.load();
		expect(fetcher).toHaveBeenCalledTimes(2);
	});
});

describe('loadById', () => {
	const seed = [
		{ id: 'a', name: 'Seed A' },
		{ id: 'b', name: 'Seed B' }
	];

	it('mengembalikan data dari getter saat sukses', async () => {
		const getter = vi.fn().mockResolvedValue({ data: { id: 'a', name: 'Remote A' } });
		const result = await loadById(getter, seed, 'a');
		expect(result?.name).toBe('Remote A');
	});

	it('fallback ke seed saat getter gagal', async () => {
		const getter = vi.fn().mockRejectedValue(new Error('boom'));
		const result = await loadById(getter, seed, 'b');
		expect(result?.name).toBe('Seed B');
	});

	it('mengembalikan undefined saat getter gagal dan id tidak ada di seed', async () => {
		const getter = vi.fn().mockRejectedValue(new Error('boom'));
		const result = await loadById(getter, seed, 'zzz');
		expect(result).toBeUndefined();
	});
});
