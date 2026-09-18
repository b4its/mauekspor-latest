import { beforeEach, describe, expect, it } from 'vitest';
import { t, i18n, toggleLocale, nextLocale, type Locale } from './i18n.svelte';
import { hasKey } from './i18n.svelte';

const uiFiles = import.meta.glob('../routes/**/*.svelte', { query: '?raw', import: 'default' }) as unknown as Record<string, () => Promise<string>>;
const componentFiles = import.meta.glob('./components/**/*.svelte', { query: '?raw', import: 'default' }) as unknown as Record<string, () => Promise<string>>;

beforeEach(() => {
	// Reset ke locale default ID agar test deterministik
	i18n.locale = 'id' as Locale;
});

describe('i18n t()', () => {
	it('mengembalikan teks Indonesia saat locale = id', () => {
		i18n.locale = 'id';
		expect(t('Produk')).toBe('Produk');
		expect(t('Masuk')).toBe('Masuk');
		expect(t('Pengiriman')).toBe('Pengiriman');
	});

	it('mengembalikan teks Inggris saat locale = en', () => {
		i18n.locale = 'en';
		expect(t('Produk')).toBe('Product');
		expect(t('Masuk')).toBe('Sign in');
		expect(t('Pengiriman')).toBe('Shipment');
	});

	it('fallback ke kunci asli jika tidak ada di kamus', () => {
		expect(t('kunci-tidak-ada-xyz')).toBe('kunci-tidak-ada-xyz');
	});

	it('kunci sidebar (EN) ter-resolve ke id/en yang benar', () => {
		i18n.locale = 'id';
		expect(t('Dashboard')).toBe('Dasbor');
		i18n.locale = 'en';
		expect(t('Dashboard')).toBe('Dashboard');
		expect(t('Products')).toBe('Village Flagship Commodities');
		expect(t('Analytics')).toBe('Analytics');
	});

	it('kalimat hero ter-resolve di kedua locale', () => {
		i18n.locale = 'id';
		expect(t('Dari kesiapan produk hingga')).toBe('Dari kesiapan produk hingga');
		i18n.locale = 'en';
		expect(t('Dari kesiapan produk hingga')).toBe('From product readiness to');
	});
});

describe('i18n locale switching', () => {
	it('toggleLocale beralih id <-> en', () => {
		i18n.locale = 'id';
		toggleLocale();
		expect(i18n.locale).toBe('en');
		expect(t('Batal')).toBe('Cancel');
		toggleLocale();
		expect(i18n.locale).toBe('id');
		expect(t('Batal')).toBe('Batal');
	});

	it('nextLocale mengembalikan locale lawan tanpa mengubah state', () => {
		i18n.locale = 'id';
		expect(nextLocale()).toBe('en');
		expect(i18n.locale).toBe('id');
		i18n.locale = 'en';
		expect(nextLocale()).toBe('id');
	});
});

describe('i18n kamus integritas (sampel lintas fitur)', () => {
	const samples: Array<[string, string, string]> = [
		// [kunci, id, en]
		['Produk', 'Produk', 'Product'],
		['Pembeli', 'Pembeli', 'Buyer'],
		['Pemasok', 'Pemasok', 'Supplier'],
		['Pengiriman', 'Pengiriman', 'Shipment'],
		['Dokumen', 'Dokumen', 'Documents'],
		['Laporan', 'Laporan', 'Report'],
		['Buat laporan', 'Buat laporan', 'Generate report'],
		['Kembali ke produk', 'Kembali ke produk', 'Back to products'],
		['Jatuh tempo', 'Jatuh tempo', 'Due'],
		['Bandingkan Pasar', 'Bandingkan Pasar', 'Compare Markets'],
		['Analisis Ekspor', 'Analisis Ekspor', 'Export Analysis'],
		['Quotations', 'Penawaran Harga', 'Quotations']
	];

	it('nilai id/en konsisten untuk sampel kunci', () => {
		for (const [key, id, en] of samples) {
			i18n.locale = 'id';
			expect(t(key), `id locale untuk ${key}`).toBe(id);
			i18n.locale = 'en';
			expect(t(key), `en locale untuk ${key}`).toBe(en);
		}
	});
});

describe('i18n kamus kelengkapan (semua kunci t() di file UI)', () => {
	it('setiap kunci t() di routes/ dan lib/components/ ada di kamus', async () => {
		const modules = await Promise.all(Object.values(uiFiles).map((m) => m));
		const components = await Promise.all(Object.values(componentFiles).map((m) => m));
		const contents = [...modules, ...components];
		const keys = new Set<string>();
		for (const content of contents) {
			for (const match of String(content).matchAll(/\bt\('([^']+)'/g)) keys.add(match[1]);
		}
		const missing = [...keys].filter((k) => !hasKey(k)).sort();
		expect(missing, `kunci tanpa entri kamus (${contents.length} file dipindai): ${missing.join(', ')}`).toEqual([]);
	});
});
