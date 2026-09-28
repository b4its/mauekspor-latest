/** Escape teks sebelum diproses sebagai Markdown/inline markup. */
export function escapeHtml(value: string): string {
	return value
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#39;');
}

/**
 * Pertahanan kedua untuk HTML yang dihasilkan parser Markdown.
 *
 * Input mentah sudah di-escape, sehingga tag hanya berasal dari parser. Fungsi
 * ini membuang protokol URL aktif dan atribut event bila parser/dependency
 * berubah di masa depan. Ini sengaja kecil dan fail-closed tanpa dependency DOM
 * agar aman saat SSR maupun browser.
 */
export function sanitizeGeneratedHtml(html: string): string {
	return html
		.replace(/\s+on[a-z]+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi, '')
		.replace(/\s+(href|src)\s*=\s*(["'])\s*(?:javascript|vbscript|data):[^"']*\2/gi, ' $1="#"')
		.replace(/<\/?(?:script|style|iframe|object|embed|form|input|button|textarea|select|option|meta|link|base)[^>]*>/gi, '');
}

/** Render inline **bold**, *italic*, dan `code` setelah HTML mentah di-escape. */
export function renderSafeInlineMarkdown(value: string): string {
	return sanitizeGeneratedHtml(
		escapeHtml(value)
			.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
			.replace(/\*(.+?)\*/g, '<em>$1</em>')
			.replace(/`(.+?)`/g, '<code class="rounded bg-muted px-1 py-0.5 font-mono text-xs">$1</code>')
	);
}
