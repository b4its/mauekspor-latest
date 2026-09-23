import { describe, expect, it } from 'vitest';
import { userAccounts, navItems } from '$lib/data/trade';

/**
 * Regresi audit: role user harus sinkron dengan UserRole backend
 * (Admin|Exporter|Buyer|Forwarder|CustomsBroker|Finance). Sebelumnya seed
 * memakai role 'UMKM' yang tidak pernah dikembalikan backend → filter role
 * di halaman Users tidak pernah cocok.
 */
describe('userAccounts role alignment', () => {
	const VALID_ROLES = ['Admin', 'Exporter', 'Buyer', 'Forwarder', 'CustomsBroker', 'Finance'];

	it('semua role user ada di daftar peran backend', () => {
		const invalid = userAccounts.filter((u) => !VALID_ROLES.includes(u.role));
		expect(invalid).toEqual([]);
	});

	it('tidak ada lagi role legacy UMKM', () => {
		expect(userAccounts.some((u) => (u.role as string) === 'UMKM')).toBe(false);
	});
});

describe('navigasi Buyer Portal terdaftar', () => {
	it('navItems memuat /buyers/portal', () => {
		expect(navItems.some((i) => i.href === '/buyers/portal')).toBe(true);
	});
});
