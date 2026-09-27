import { describe, expect, it } from 'vitest';
import { paginate, calcTotalPages } from './pagination';

describe('paginate + calcTotalPages (dipakai bersama reset filter)', () => {
	const items = Array.from({ length: 42 }, (_, i) => ({ id: `i-${i}` }));

	it('membagi item sesuai halaman dan ukuran', () => {
		expect(paginate(items, 1, 10)).toHaveLength(10);
		expect(paginate(items, 5, 10)).toHaveLength(2);
		expect(paginate(items, 1, 10)[0].id).toBe('i-0');
	});

	it('menghitung total halaman dengan benar', () => {
		expect(calcTotalPages(42, 10)).toBe(5);
		expect(calcTotalPages(40, 10)).toBe(4);
		expect(calcTotalPages(0, 10)).toBe(1);
	});

	it('halaman di luar rentang di-clamp, bukan menghasilkan daftar kosong', () => {
		// paginate melakukan clamp: bila hasil menyusut dari 42 → 3 item tetapi
		// halaman masih 5, ia tetap mengembalikan halaman terakhir yang valid.
		const narrowed = items.slice(0, 3);
		expect(paginate(narrowed, 5, 10)).toHaveLength(3);
		expect(paginate(narrowed, 1, 10)).toHaveLength(3);
		expect(paginate(items, 99, 10)).toHaveLength(2);
	});

	it('halaman < 1 di-clamp ke halaman pertama', () => {
		expect(paginate(items, 0, 10)[0].id).toBe('i-0');
		expect(paginate(items, -5, 10)[0].id).toBe('i-0');
	});
});
