import { describe, expect, it } from 'vitest';
import { createBulkSelection } from './bulkSelection.svelte';

describe('createBulkSelection', () => {
	it('toggle menambah dan menghapus id', () => {
		const bulk = createBulkSelection();
		bulk.toggle('a');
		bulk.toggle('b');
		expect(bulk.count).toBe(2);
		expect(bulk.has('a')).toBe(true);
		bulk.toggle('a');
		expect(bulk.has('a')).toBe(false);
		expect(bulk.count).toBe(1);
	});

	it('toggleAll memilih semua, lalu membatalkan semua', () => {
		const bulk = createBulkSelection();
		bulk.toggleAll(['a', 'b', 'c']);
		expect(bulk.ids.sort()).toEqual(['a', 'b', 'c']);
		expect(bulk.allOf(['a', 'b', 'c'])).toBe(true);
		bulk.toggleAll(['a', 'b', 'c']);
		expect(bulk.count).toBe(0);
	});

	it('clear mengosongkan pilihan', () => {
		const bulk = createBulkSelection();
		bulk.toggle('x');
		bulk.clear();
		expect(bulk.count).toBe(0);
	});

	it('keepOnly membuang id yang tidak lagi ada', () => {
		const bulk = createBulkSelection();
		bulk.toggle('a');
		bulk.toggle('b');
		bulk.toggle('gone');
		bulk.keepOnly(['a', 'b']);
		expect(bulk.ids.sort()).toEqual(['a', 'b']);
	});

	it('allOf false untuk daftar kosong', () => {
		const bulk = createBulkSelection();
		expect(bulk.allOf([])).toBe(false);
	});
});
