import { beforeEach, describe, expect, it } from 'vitest';
import { i18n } from './i18n.svelte';
import { getWhatsAppTemplates } from './utils/whatsapp';
import type { Locale } from './i18n.svelte';

beforeEach(() => {
	i18n.locale = 'id' as Locale;
});

describe('getWhatsAppTemplates', () => {
	it('mengembalikan 6 template default', () => {
		expect(getWhatsAppTemplates()).toHaveLength(6);
	});

	it('label & teks dalam bahasa Indonesia saat locale = id', () => {
		i18n.locale = 'id';
		const templates = getWhatsAppTemplates();
		expect(templates[0].label).toBe('Perkenalan');
		expect(templates[0].text).toContain('saya dari {company}');
		expect(templates[1].label).toBe('Minta penawaran');
	});

	it('label & teks dalam bahasa Inggris saat locale = en', () => {
		i18n.locale = 'en';
		const templates = getWhatsAppTemplates();
		expect(templates[0].label).toBe('Introduction');
		expect(templates[0].text).toContain("I'm from {company}");
		expect(templates[1].label).toBe('Request quote');
	});

	it('placeholder {name} dan {company} tetap ada di kedua locale', () => {
		for (const locale of ['id', 'en'] as Locale[]) {
			i18n.locale = locale;
			for (const template of getWhatsAppTemplates()) {
				expect(template.text).toContain('{name}');
				expect(template.text).toContain('{company}');
			}
		}
	});
});
