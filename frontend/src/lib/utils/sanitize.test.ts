import { describe, expect, it } from 'vitest';
import { escapeHtml, renderSafeInlineMarkdown, sanitizeGeneratedHtml } from './sanitize';

describe('HTML sanitization', () => {
	it('escapes raw tags and attributes', () => {
		expect(escapeHtml('<img src=x onerror=alert(1)>')).toBe(
			'&lt;img src=x onerror=alert(1)&gt;'
		);
	});

	it('keeps supported inline markdown but never raw HTML', () => {
		const output = renderSafeInlineMarkdown('**aman** <script>alert(1)</script>');
		expect(output).toContain('<strong>aman</strong>');
		expect(output).not.toContain('<script>');
		expect(output).toContain('&lt;script&gt;');
	});

	it('removes active URL protocols and event handlers', () => {
		const output = sanitizeGeneratedHtml(
			'<a href="javascript:alert(1)" onclick="alert(2)">x</a>'
		);
		expect(output).toBe('<a href="#">x</a>');
	});
});
