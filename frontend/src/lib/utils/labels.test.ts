import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/i18n.svelte', () => ({
	t: (key: string) =>
		({
			Aktif: 'Active',
			Ditangguhkan: 'Suspended',
			Selesai: 'Done',
			Rendah: 'Low',
			Tinggi: 'High',
			Kritis: 'Critical',
			Operasional: 'Operations',
			Eksportir: 'Exporter',
			Info: 'Info'
		})[key] ?? key
}));

import { label } from './labels';

describe('label()', () => {
	it('menerjemahkan status umum', () => {
		expect(label('Active')).toBe('Active');
		expect(label('Suspended')).toBe('Suspended');
	});

	it('menerjemahkan prioritas dan severity', () => {
		expect(label('High')).toBe('High');
		expect(label('Critical')).toBe('Critical');
		expect(label('Info')).toBe('Info');
	});

	it('menerjemahkan peran tim', () => {
		expect(label('Operations')).toBe('Operations');
		expect(label('Exporter')).toBe('Exporter');
	});

	it('mengembalikan nilai tak dikenal apa adanya', () => {
		expect(label('Something Custom')).toBe('Something Custom');
	});

	it('menangani nilai kosong dengan placeholder', () => {
		expect(label(null)).toBe('—');
		expect(label(undefined)).toBe('—');
		expect(label('')).toBe('—');
	});

	it('menerjemahkan status alur ekspor (kunci baru)', () => {
		// Kunci baru tetap melewati t(); pastikan nilainya TIDAK lagi mentah.
		for (const raw of ['Confirmed', 'In Shipment', 'Settled', 'Overdue', 'Revoked', 'Exception']) {
			expect(label(raw)).not.toBe(raw);
		}
		expect(label('Draft')).toBe('Draf');
	});
});
