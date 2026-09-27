/**
 * Format tanggal & waktu ber-locale.
 *
 * Sebelumnya banyak halaman menampilkan string ISO mentah (`2026-08-05 10:42`)
 * yang identik di locale id/en. Helper ini memusatkan format agar konsisten
 * dengan locale aktif dan tetap aman untuk nilai non-tanggal ("Not uploaded").
 */
import { i18n } from '$lib/i18n.svelte';

const LOCALE_MAP: Record<string, string> = { id: 'id-ID', en: 'en-US' };

function activeLocale(): string {
	return LOCALE_MAP[i18n.locale] ?? 'id-ID';
}

/** Parse longgar: Date valid, "YYYY-MM-DD[ HH:mm]", atau ISO. null bila gagal. */
function toDate(value: unknown): Date | null {
	if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
	if (typeof value === 'number') {
		const d = new Date(value);
		return Number.isNaN(d.getTime()) ? null : d;
	}
	if (typeof value !== 'string') return null;
	const raw = value.trim();
	if (!raw || raw.toLowerCase() === 'now') return null;
	// "2026-08-05 10:42" → ISO agar dikenali semua engine.
	const normalized = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(raw) ? raw.replace(' ', 'T') : raw;
	const date = new Date(normalized);
	return Number.isNaN(date.getTime()) ? null : date;
}

/** Format tanggal (mis. "5 Agu 2026"). Fallback: nilai asli apa adanya. */
function fallbackText(value: unknown): string {
	return typeof value === 'string' && value.trim() ? value : '—';
}

export function formatDate(value: unknown, opts: Intl.DateTimeFormatOptions = {}): string {
	const date = toDate(value);
	if (!date) return fallbackText(value);
	return new Intl.DateTimeFormat(activeLocale(), {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
		...opts
	}).format(date);
}

/** Format tanggal + jam. */
export function formatDateTime(value: unknown): string {
	const date = toDate(value);
	if (!date) return fallbackText(value);
	return new Intl.DateTimeFormat(activeLocale(), {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	}).format(date);
}

/** Format jam saja (mis. "10:42"). */
export function formatTime(value: unknown): string {
	const date = toDate(value);
	if (!date) return fallbackText(value);
	return new Intl.DateTimeFormat(activeLocale(), { hour: '2-digit', minute: '2-digit' }).format(date);
}

/** Rentang tanggal ringkas (mis. "5 - 12 Agu 2026"). */
export function formatDateRange(start: unknown, end: unknown): string {
	const a = toDate(start);
	const b = toDate(end);
	if (!a) return fallbackText(start);
	if (!b) return formatDate(start);
	const sameYear = a.getFullYear() === b.getFullYear();
	const sameMonth = sameYear && a.getMonth() === b.getMonth();
	if (sameMonth) {
		return `${new Intl.DateTimeFormat(activeLocale(), { day: 'numeric' }).format(a)} - ${formatDate(b)}`;
	}
	return `${formatDate(a)} - ${formatDate(b)}`;
}

/** Waktu relatif ringkas ("3 hari lalu"). Fallback ke formatDate. */
export function formatRelative(value: unknown): string {
	const date = toDate(value);
	if (!date) return fallbackText(value);
	const diffMs = Date.now() - date.getTime();
	const diffMinutes = Math.round(diffMs / 60000);
	const rtf = new Intl.RelativeTimeFormat(activeLocale(), { numeric: 'auto' });
	const abs = Math.abs(diffMinutes);
	if (abs < 1) return rtf.format(0, 'minute');
	if (abs < 60) return rtf.format(-diffMinutes, 'minute');
	const diffHours = Math.round(diffMinutes / 60);
	if (Math.abs(diffHours) < 24) return rtf.format(-diffHours, 'hour');
	const diffDays = Math.round(diffHours / 24);
	if (Math.abs(diffDays) < 30) return rtf.format(-diffDays, 'day');
	const diffMonths = Math.round(diffDays / 30);
	if (Math.abs(diffMonths) < 12) return rtf.format(-diffMonths, 'month');
	return rtf.format(-Math.round(diffMonths / 12), 'year');
}
