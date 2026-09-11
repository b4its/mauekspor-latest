import { afterEach, describe, expect, it, vi } from 'vitest';
import { openWhatsApp, getWhatsAppTemplates } from './utils/whatsapp';
import { i18n } from './i18n.svelte';
import type { Locale } from './i18n.svelte';

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('openWhatsApp', () => {
	it('membuka wa.me dengan nomor dan pesan ter-encode', () => {
		const open = vi.fn();
		vi.stubGlobal('window', { open });
		openWhatsApp('+62 21 555 0100', 'Halo');
		expect(open).toHaveBeenCalledOnce();
		const url = open.mock.calls[0][0] as string;
		expect(url).toMatch(/^https:\/\/wa\.me\/62215550100\?text=Halo$/);
	});

	it('mengabaikan nomor kosong', () => {
		const open = vi.fn();
		vi.stubGlobal('window', { open });
		openWhatsApp('', 'Halo');
		expect(open).not.toHaveBeenCalled();
	});

	it('membersihkan karakter non-digit dari nomor', () => {
		const open = vi.fn();
		vi.stubGlobal('window', { open });
		openWhatsApp('+62 (812) 345-6789', 'test');
		const url = open.mock.calls[0][0] as string;
		expect(url).toContain('wa.me/628123456789');
	});

	it('meng-encode parameter pesan', () => {
		const open = vi.fn();
		vi.stubGlobal('window', { open });
		openWhatsApp('62123', 'Halo {name}, apa kabar?');
		const url = open.mock.calls[0][0] as string;
		expect(url).toContain(encodeURIComponent('{name}'));
		expect(url).toContain(encodeURIComponent(' apa kabar?'));
	});

	it('template getWhatsAppTemplates konsisten dengan openWhatsApp (placeholder digunakan)', () => {
		vi.stubGlobal('window', { open: vi.fn() });
		const templates = getWhatsAppTemplates();
		for (const tpl of templates) {
			const msg = tpl.text.replace('{name}', 'Budi').replace('{company}', 'PT Maju');
			expect(() => openWhatsApp('62123', msg)).not.toThrow();
		}
	});
});

describe('getWhatsAppTemplates integration with i18n', () => {
	it('template pertama dalam bahasa Indonesia saat locale = id', () => {
		i18n.locale = 'id';
		const templates = getWhatsAppTemplates();
		expect(templates[0].label).toBe('Perkenalan');
		expect(templates[0].text).toContain('saya dari {company}');
	});

	it('template pertama dalam bahasa Inggris saat locale = en', () => {
		i18n.locale = 'en';
		const templates = getWhatsAppTemplates();
		expect(templates[0].label).toBe('Introduction');
		expect(templates[0].text).toContain("I'm from {company}");
	});
});