import { describe, it, expect } from 'vitest';
import { canViewPath, visibleNavGroups, allowedHrefs } from './roleAccess';
import { navGroups, navItems } from './data/trade';

const ROLES = ['Exporter', 'Buyer', 'Forwarder', 'CustomsBroker', 'Finance', 'KepalaDesa', 'Admin'] as const;

describe('sidebar ⇔ access invariant for EVERY role', () => {
	it('no visible sidebar item is ever denied', () => {
		for (const role of ROLES) {
			for (const g of visibleNavGroups(role, navGroups)) {
				for (const item of g.items) {
					expect(canViewPath(role, item.href), `${role} ${item.href}`).toBe(true);
				}
			}
		}
	});

	it('every navGroups href is allowed for at least one role (no orphan menu)', () => {
		const allHrefs = navGroups.flatMap((g) => g.items.map((i) => i.href));
		for (const href of allHrefs) {
			const openable = ROLES.some((r) => canViewPath(r, href));
			expect(openable, `orphan menu href: ${href}`).toBe(true);
		}
	});

	it('Admin sees all navGroups items', () => {
		const vis = visibleNavGroups('Admin', navGroups).flatMap((g) => g.items.map((i) => i.href));
		const all = navGroups.flatMap((g) => g.items.map((i) => i.href));
		expect(new Set(vis)).toEqual(new Set(all));
	});

	it('each role sidebar is non-empty and distinct', () => {
		const sigs = ROLES.filter((r) => r !== 'Admin').map((r) => {
			const hrefs = visibleNavGroups(r, navGroups).flatMap((g) => g.items.map((i) => i.href)).sort();
			expect(hrefs.length, `${r} sidebar empty`).toBeGreaterThan(3);
			return hrefs.join('|');
		});
		expect(new Set(sigs).size).toBeGreaterThan(1);
	});

	it('items in navItems not present in navGroups do not break the invariant', () => {
		// navItems (command palette) harus juga lolos canViewPath khi tampil.
		for (const role of ROLES) {
			const allowed = allowedHrefs(role);
			for (const item of navItems) {
				if (allowed === '*' || allowed.has(item.href)) {
					expect(canViewPath(role, item.href), `${role} ${item.href}`).toBe(true);
				}
			}
		}
	});
});
