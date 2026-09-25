import type { UserRole } from '$lib/api/auth';

/**
 * Peta akses per-peran untuk UI (sidebar & route guard).
 *
 * Setiap peran hanya melihat modul yang relevan dengan pekerjaannya. Peta ini
 * SENGAJA selaras dengan penegakan sisi backend (`backend/app/core/permissions.py`)
 * agar menu yang tampil ⇔ data yang boleh diakses.
 *
 * `hrefs` = daftar path nav yang boleh DILIHAT peran tersebut.
 * `Admin` memakai `'*'` (semua).
 */
export type RoleAccess = {
	/** Path nav yang boleh dilihat. */
	hrefs: Set<string> | '*';
	/** Modul backend yang boleh dibaca (untuk rujukan bila diperlukan). */
	modules: Set<string> | '*';
};

const ADMIN_ONLY_HREFS = [
	'/users',
	'/audit',
	'/api-keys',
	'/settings',
	'/admin',
	'/admin/countries'
];

/** Modul yang hanya Admin boleh lihat (selaras dengan ADMIN_ONLY_MODULES backend). */
export const ADMIN_ONLY_MODULES = new Set(['users', 'audit', 'api-keys', 'settings', 'admin']);

/**
 * Href → modul backend (dipakai untuk memetakan route ke modul izin).
 * Semua href yang tidak terdaftar dianggap publik/semua-peran (mis. /dashboard, /about).
 */
export const HREF_MODULE: Record<string, string> = {
	'/users': 'users',
	'/audit': 'audit',
	'/api-keys': 'api-keys',
	'/settings': 'settings',
	'/admin': 'admin',
	'/admin/countries': 'admin',
	'/business-profile': 'business-profiles',
	'/trade-projects': 'trade-projects',
	'/products': 'products',
	'/villages': 'villages',
	'/export-analysis': 'export-analysis',
	'/compliance': 'compliance',
	'/markets': 'markets',
	'/catalogs': 'catalogs',
	'/catalogs/public': 'catalogs',
	'/buyers': 'buyers',
	'/buyers/portal': 'buyers/portal',
	'/buyers/my-profile': 'buyers/portal',
	'/buyers/profile': 'buyers/portal',
	'/buyer-requests': 'buyer-requests',
	'/suppliers': 'suppliers',
	'/forwarders': 'forwarders',
	'/forwarders/my-profile': 'forwarders',
	'/forwarders/profile': 'forwarders',
	'/forwarders/catalogs': 'catalogs',
	'/rfq': 'rfqs',
	'/quotations': 'quotations',
	'/costing': 'costing',
	'/orders': 'orders',
	'/payments': 'payments',
	'/tasks': 'tasks',
	'/documents': 'documents',
	'/shipments': 'shipments',
	'/analytics': 'analytics',
	'/reports': 'reports',
	'/team': 'team',
	'/notifications': 'notifications',
	'/integrations': 'integrations',
	'/templates': 'templates',
	'/automations': 'automations',
	'/knowledge': 'knowledge',
	'/educational': 'educational',
	'/chat': 'chat',
	'/marketing': 'products',
	'/calendar': 'calendar',
	'/files': 'files',
	'/messages': 'messages',
	'/billing': 'billing',
	'/support': 'support'
};

/** Modul yang boleh DILIHAT (read) per peran. Selaras dengan akses UI. */
const ROLE_READ_MODULES: Record<UserRole, Set<string>> = {
	Admin: new Set(), // diabaikan (pakai '*')
	Exporter: new Set([
		'business-profiles', 'trade-projects', 'products', 'villages', 'export-analysis',
		'compliance', 'markets', 'catalogs', 'buyers', 'buyers/portal', 'buyer-requests',
		'suppliers', 'forwarders', 'rfqs', 'quotations', 'costing', 'orders', 'payments',
		'tasks', 'documents', 'shipments', 'analytics', 'reports', 'team', 'notifications',
		'integrations', 'templates', 'automations', 'knowledge', 'educational', 'chat',
		'calendar', 'files', 'messages', 'billing', 'support'
	]),
	Buyer: new Set([
		'products', 'catalogs', 'buyers/portal', 'buyer-requests', 'quotations', 'orders',
		'analytics', 'reports', 'messages', 'notifications', 'support', 'knowledge', 'educational'
	]),
	Forwarder: new Set([
		'trade-projects', 'catalogs', 'shipments', 'documents', 'forwarders',
		'analytics', 'reports', 'messages', 'notifications', 'support', 'calendar', 'files'
	]),
	CustomsBroker: new Set([
		'trade-projects', 'compliance', 'documents', 'shipments', 'payments', 'analytics',
		'reports', 'messages', 'notifications', 'support', 'files'
	]),
	Finance: new Set([
		'orders', 'quotations', 'payments', 'billing', 'costing', 'analytics', 'reports',
		'messages', 'notifications', 'support'
	])
};

/** Href yang selalu boleh dilihat semua peran (dashboard, about, halaman publik). */
const ALWAYS_ALLOWED = new Set([
	'/dashboard',
	'/about',
	'/catalogs/public'
]);

/**
 * Daftar href yang boleh dilihat untuk sebuah peran.
 * Mengembalikan `'*'` bila peran = Admin.
 */
export function allowedHrefs(role: UserRole | string | null | undefined): Set<string> | '*' {
	const r = (role ?? '') as UserRole;
	if (r === 'Admin') return '*';
	const modules = ROLE_READ_MODULES[r];
	if (!modules) return new Set(); // peran tak dikenal → hanya dashboard/about

	const hrefs = new Set<string>();
	for (const href of Object.keys(HREF_MODULE)) {
		if (modules.has(HREF_MODULE[href])) hrefs.add(href);
	}
	for (const href of ALWAYS_ALLOWED) hrefs.add(href);
	return hrefs;
}

/**
 * Apakah seorang peran boleh melihat suatu path.
 * Pencocokan prefix (mis. `/products/PRD-1` cocok dengan `/products`).
 */
export function canViewPath(role: UserRole | string | null | undefined, path: string): boolean {
	const allowed = allowedHrefs(role);
	if (allowed === '*') return true;
	if (ALWAYS_ALLOWED.has(path)) return true;

	// Cari href terpanjang yang merupakan prefix dari path.
	let match = '';
	for (const href of allowed) {
		if (path === href || path.startsWith(href + '/')) {
			if (href.length > match.length) match = href;
		}
	}
	return match.length > 0;
}
