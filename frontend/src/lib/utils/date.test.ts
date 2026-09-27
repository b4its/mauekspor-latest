import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/i18n.svelte', () => ({ i18n: { locale: 'id' } }));

import { formatDate, formatDateTime, formatDateRange, formatRelative, formatTime } from './date';

describe('date utils', () => {
	it('memformat tanggal ISO ke locale id', () => {
		expect(formatDate('2026-08-05')).toContain('2026');
		expect(formatDate('2026-08-05')).toContain('Agu');
	});

	it('menerima format "YYYY-MM-DD HH:mm"', () => {
		expect(formatDate('2026-08-05 10:42')).toContain('2026');
	});

	it('mengembalikan nilai asli bila bukan tanggal', () => {
		expect(formatDate('Not uploaded')).toBe('Not uploaded');
		expect(formatDate('')).toBe('—');
		expect(formatDate(null)).toBe('—');
	});

	it('formatDateTime menyertakan tahun dan menit', () => {
		const out = formatDateTime('2026-08-05 10:42');
		expect(out).toContain('2026');
		expect(out).toMatch(/\d{2}[.:]\d{2}/);
	});

	it('formatTime hanya menampilkan jam', () => {
		expect(formatTime('2026-08-05 10:42')).not.toContain('2026');
	});

	it('formatDateRange ringkas untuk bulan yang sama', () => {
		const out = formatDateRange('2026-08-05', '2026-08-12');
		expect(out).toContain('2026');
		expect(out).toContain('-');
	});

	it('formatRelative memberi label relatif', () => {
		const now = new Date();
		const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
		const out = formatRelative(threeDaysAgo);
		expect(out.includes('hari') || out.includes('kemarin')).toBe(true);
	});

	it('formatRelative fallback untuk nilai tak dikenal', () => {
		expect(formatRelative('Planned soon')).toBe('Planned soon');
	});
});
