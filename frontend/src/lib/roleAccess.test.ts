import { describe, expect, it } from 'vitest';
import { allowedHrefs, canViewPath } from './roleAccess';

describe('roleAccess', () => {
	it('Admin dapat melihat semua path', () => {
		expect(allowedHrefs('Admin')).toBe('*');
		expect(canViewPath('Admin', '/users')).toBe(true);
		expect(canViewPath('Admin', '/settings')).toBe(true);
		expect(canViewPath('Admin', '/admin/countries')).toBe(true);
	});

	it('Exporter tidak boleh akses halaman admin-only', () => {
		expect(canViewPath('Exporter', '/users')).toBe(false);
		expect(canViewPath('Exporter', '/audit')).toBe(false);
		expect(canViewPath('Exporter', '/settings')).toBe(false);
		expect(canViewPath('Exporter', '/api-keys')).toBe(false);
	});

	it('Exporter boleh akses modul operasionalnya', () => {
		for (const path of ['/products', '/suppliers', '/costing', '/team', '/trade-projects', '/quotations']) {
			expect(canViewPath('Exporter', path), path).toBe(true);
		}
		// detail/prefix juga cocok
		expect(canViewPath('Exporter', '/products/PRD-COF-001')).toBe(true);
	});

	it('Buyer hanya melihat modul relevan', () => {
		for (const path of ['/buyer-requests', '/quotations', '/orders', '/catalogs', '/buyers/portal']) {
			expect(canViewPath('Buyer', path), path).toBe(true);
		}
		for (const path of ['/suppliers', '/team', '/costing', '/payments', '/buyers', '/forwarders', '/users', '/settings']) {
			expect(canViewPath('Buyer', path), path).toBe(false);
		}
	});

	it('Forwarder hanya melihat pengiriman/dokumen', () => {
		for (const path of ['/shipments', '/documents', '/catalogs', '/forwarders']) {
			expect(canViewPath('Forwarder', path), path).toBe(true);
		}
		for (const path of ['/buyers', '/suppliers', '/costing', '/payments', '/team']) {
			expect(canViewPath('Forwarder', path), path).toBe(false);
		}
	});

	it('Dashboard & About selalu boleh diakses peran apa pun', () => {
		for (const role of ['Exporter', 'Buyer', 'Forwarder', 'CustomsBroker', 'Finance']) {
			expect(canViewPath(role, '/dashboard'), role).toBe(true);
			expect(canViewPath(role, '/about'), role).toBe(true);
		}
	});

	it('peran tak dikenal hanya boleh dashboard/about', () => {
		expect(canViewPath('Unknown', '/dashboard')).toBe(true);
		expect(canViewPath('Unknown', '/products')).toBe(false);
	});
});
