import { describe, expect, it } from 'vitest';
import { sortBy, toggleDir, SORT_NONE } from './sort';

const rows = [
	{ id: 'C', value: 3, name: 'charlie' },
	{ id: 'A', value: 1, name: 'Alpha' },
	{ id: 'B', value: 2, name: 'bravo' }
];

describe('sortBy', () => {
	it('mengembalikan array apa adanya bila key kosong', () => {
		expect(sortBy(rows, SORT_NONE)).toBe(rows);
	});

	it('mengurutkan angka secara numerik menaik', () => {
		expect(sortBy(rows, 'value', 'asc').map((r) => r.value)).toEqual([1, 2, 3]);
	});

	it('mengurutkan angka menurun', () => {
		expect(sortBy(rows, 'value', 'desc').map((r) => r.value)).toEqual([3, 2, 1]);
	});

	it('mengurutkan angka tersimpan sebagai teks secara numerik', () => {
		const text = [{ n: '10' }, { n: '2' }, { n: '1' }];
		expect(sortBy(text, 'n', 'asc').map((r) => r.n)).toEqual(['1', '2', '10']);
	});

	it('mengurutkan teks case-insensitive', () => {
		expect(sortBy(rows, 'name', 'asc').map((r) => r.name)).toEqual(['Alpha', 'bravo', 'charlie']);
	});

	it('tidak memutasi array sumber', () => {
		const before = rows.map((r) => r.id);
		sortBy(rows, 'value', 'desc');
		expect(rows.map((r) => r.id)).toEqual(before);
	});

	it('menempatkan nilai kosong tanpa error', () => {
		const mixed = [{ v: 'b' }, { v: null }, { v: 'a' }];
		const sorted = sortBy(mixed, 'v', 'asc');
		expect(sorted).toHaveLength(3);
		expect(sorted[sorted.length - 1].v).toBe('b');
	});
});

describe('toggleDir', () => {
	it('membalik arah', () => {
		expect(toggleDir('asc')).toBe('desc');
		expect(toggleDir('desc')).toBe('asc');
	});
});
