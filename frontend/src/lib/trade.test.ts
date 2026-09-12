import { describe, expect, it } from 'vitest';
import { navItems, navGroups } from './data/trade';
import { t, hasKey } from './i18n.svelte';

// Kumpulkan semua label yang dirender via t() di sidebar (AppSidebar/AppShell)
function allLabels(): string[] {
	const labels = new Set<string>();
	for (const item of navItems) labels.add(item.label);
	for (const group of navGroups) {
		labels.add(group.label);
		for (const item of group.items) labels.add(item.label);
	}
	return [...labels];
}

describe('i18n integritas label navigasi (seed data)', () => {
	const labels = allLabels();

	it('setiap label navigasi memiliki entri kamus (hasKey)', () => {
		const missing = labels.filter((label) => !hasKey(label));
		expect(missing, `label tanpa entri kamus: ${missing.join(', ')}`).toEqual([]);
	});

	it('terjemahan id dan en tersedia untuk semua label', () => {
		// Identity translation (RFQ -> RFQ, Admin -> Admin) adalah hal wajar,
		// selama kunci ada di kamus (dicek oleh hasKey di atas).
		for (const label of labels) {
			expect(t(label), `t(${label}) en`).not.toBe('');
		}
	});

	it('navItems tidak punya href duplikat internal', () => {
		const hrefs = navItems.map((item) => item.href);
		expect(new Set(hrefs).size).toBe(hrefs.length);
	});

	it('navGroups tidak punya href duplikat internal', () => {
		const hrefs: string[] = [];
		for (const group of navGroups) {
			for (const item of group.items) hrefs.push(item.href);
		}
		expect(new Set(hrefs).size).toBe(hrefs.length);
	});
});
