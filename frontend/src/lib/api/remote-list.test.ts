import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createRemoteList, loadById, setDemoDataMode } from './remote-list.svelte';

// Demo mode OFF by default → seed tidak dipakai sebagai fallback (PRD G-09).
beforeEach(() => {
	setDemoDataMode(false);
	if (typeof window !== 'undefined') {
		window.history.replaceState({}, '', '/');
	}
});

afterEach(() => {
	setDemoDataMode(null);
});

describe('createRemoteList (truth-in-UI, demo OFF)', () => {
	const seed = [
		{ id: 'a', name: 'Seed A' },
		{ id: 'b', name: 'Seed B' }
	];

	it('mulai KOSONG (bukan seed) dan loading true', () => {
		const list = createRemoteList(async () => ({ data: [] }), seed);
		expect(list.items).toHaveLength(0);
		expect(list.loading).toBe(true);
		expect(list.usingFallback).toBe(false);
	});

	it('load() memakai data remote', async () => {
		const fetcher = vi.fn().mockResolvedValue({ data: [{ id: 'c', name: 'Remote C' }] });
		const list = createRemoteList(fetcher, seed);
		await list.load();
		expect(list.items).toHaveLength(1);
		expect(list.items[0].id).toBe('c');
		expect(list.usingFallback).toBe(false);
		expect(list.error).toBe('');
	});

	it('load() gagal → daftar kosong + error (tidak menampilkan seed)', async () => {
		const fetcher = vi.fn().mockRejectedValue(new Error('network down'));
		const list = createRemoteList(fetcher, seed);
		await list.load();
		expect(list.items).toHaveLength(0);
		expect(list.usingFallback).toBe(false);
		expect(list.error).toContain('Tidak dapat memuat data dari server');
		expect(list.loading).toBe(false);
	});
});

describe('createRemoteList (demo ON)', () => {
	const seed = [{ id: 'a', name: 'Seed A' }];

	it('memakai seed saat gagal bila demo mode aktif', async () => {
		setDemoDataMode(true);
		const list = createRemoteList(async () => Promise.reject(new Error('x')), seed);
		await list.load();
		expect(list.items).toHaveLength(1);
		expect(list.usingFallback).toBe(true);
	});
});

describe('loadById', () => {
	const seed = [
		{ id: 'a', name: 'Seed A' },
		{ id: 'b', name: 'Seed B' }
	];

	it('mengembalikan data dari getter saat sukses', async () => {
		const getter = vi.fn().mockResolvedValue({ data: { id: 'a', name: 'Remote A' } });
		expect((await loadById(getter, seed, 'a'))?.name).toBe('Remote A');
	});

	it('mengembalikan undefined saat gagal (demo OFF, tidak pakai seed)', async () => {
		const getter = vi.fn().mockRejectedValue(new Error('boom'));
		expect(await loadById(getter, seed, 'b')).toBeUndefined();
	});

	it('fallback ke seed saat demo ON', async () => {
		setDemoDataMode(true);
		const getter = vi.fn().mockRejectedValue(new Error('boom'));
		expect((await loadById(getter, seed, 'b'))?.name).toBe('Seed B');
	});
});
