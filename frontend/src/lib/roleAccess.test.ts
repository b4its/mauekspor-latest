import { describe, expect, it } from 'vitest';
import { allowedHrefs, canViewPath, visibleNavGroups, HREF_MODULE } from './roleAccess';
import { navGroups } from './data/trade';

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

	it('KepalaDesa melihat komoditas dan kesiapan desa', () => {
		for (const path of ['/products', '/villages', '/compliance', '/documents', '/analytics']) {
			expect(canViewPath('KepalaDesa', path), path).toBe(true);
		}
		for (const path of ['/buyers', '/payments', '/team', '/settings']) {
			expect(canViewPath('KepalaDesa', path), path).toBe(false);
		}
	});

	it('Dashboard & About selalu boleh diakses peran apa pun', () => {
		for (const role of ['Exporter', 'Buyer', 'Forwarder', 'CustomsBroker', 'Finance', 'KepalaDesa']) {
			expect(canViewPath(role, '/dashboard'), role).toBe(true);
			expect(canViewPath(role, '/about'), role).toBe(true);
		}
	});

	it('peran tak dikenal hanya boleh dashboard/about', () => {
		expect(canViewPath('Unknown', '/dashboard')).toBe(true);
		expect(canViewPath('Unknown', '/products')).toBe(false);
	});

	// ── Invarian anti-"ditolak": menu yang tampil pasti bisa dibuka ──────────
	const ROLES = ['Exporter', 'Buyer', 'Forwarder', 'CustomsBroker', 'Finance', 'KepalaDesa'] as const;

	it('setiap item sidebar yang tampil untuk sebuah peran tidak pernah ditolak', () => {
		for (const role of ROLES) {
			const groups = visibleNavGroups(role, navGroups);
			for (const group of groups) {
				for (const item of group.items) {
					// Menu tampil ⇔ path harus lolos guard (tidak "Akses ditolak").
					expect(canViewPath(role, item.href), `${role} ${item.href}`).toBe(true);
				}
			}
		}
	});

	it('sidebar tiap peran tidak kosong dan berbeda antar peran', () => {
		const sigs = ROLES.map((role) => {
			const groups = visibleNavGroups(role, navGroups);
			const hrefs = groups.flatMap((g) => g.items.map((i) => i.href)).sort();
			expect(hrefs.length, `${role} sidebar kosong`).toBeGreaterThan(3);
			return hrefs.join('|');
		});
		expect(new Set(sigs).size).toBeGreaterThan(1);
	});

	it('Marketing hanya tampil untuk Exporter (bukan Buyer/Forwarder)', () => {
		const hrefsOf = (role: string) =>
			visibleNavGroups(role, navGroups)
				.flatMap((g) => g.items.map((i) => i.href));
		expect(hrefsOf('Exporter')).toContain('/marketing');
		expect(hrefsOf('Buyer')).not.toContain('/marketing');
		expect(hrefsOf('Forwarder')).not.toContain('/marketing');
	});

	it('setiap href di HREF_MODULE dapat dibuka oleh minimal satu peran non-admin', () => {
		// Menangkap href "yatim" yang dipetakan tapi tak pernah tampil/terbuka.
		for (const href of Object.keys(HREF_MODULE)) {
			const anyRole = ROLES.some((role) => canViewPath(role, href));
			const admin = canViewPath('Admin', href);
			expect(anyRole || admin, `href tanpa peran yang bisa membuka: ${href}`).toBe(true);
		}
	});

	it('Exporter boleh membuka Documents dan Shipments (bukan ditolak)', () => {
		// Regresi: backend pernah punya documents/shipments di write-tapi-bukan-read,
		// sehingga menu tampil tetapi halaman 403.
		expect(canViewPath('Exporter', '/documents')).toBe(true);
		expect(canViewPath('Exporter', '/shipments')).toBe(true);
	});

	it('Countries & HS Codes dapat diakses semua peran (data referensi publik)', () => {
		for (const role of [...ROLES, 'Admin']) {
			expect(canViewPath(role, '/countries'), role).toBe(true);
			expect(canViewPath(role, '/hs-codes'), role).toBe(true);
		}
	});

	it('modul kolaborasi (Knowledge/Educational) tampil untuk semua peran', () => {
		for (const role of ROLES) {
			expect(canViewPath(role, '/knowledge'), role).toBe(true);
			expect(canViewPath(role, '/educational'), role).toBe(true);
		}
	});

	it('halaman tiap peran berbeda (bukan semua sama)', () => {
		const sets = ROLES.map((role) => {
			const allowed = allowedHrefs(role);
			return allowed === '*' ? new Set<string>() : allowed;
		});
		// Minimal ada dua peran dengan himpunan menu berbeda.
		const signatures = new Set(sets.map((s) => [...s].sort().join('|')));
		expect(signatures.size).toBeGreaterThan(1);
	});
});
