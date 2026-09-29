import type { ComplianceTask, DocumentItem, RiskLevel, TaskStatus } from '$lib/data/trade';

// ─── Dynamic currency formatter ──────────────────────────────────────────────
// Default: IDR (Rupiah). Bisa diubah via setDisplayCurrency().
// Semua komponen yang pakai currency.format() akan otomatis ikut.

let _displayCurrency = 'IDR';
let _formatter: Intl.NumberFormat = _makeFormatter('IDR');

function _makeFormatter(code: string): Intl.NumberFormat {
	const localeMap: Record<string, string> = {
		IDR: 'id-ID', USD: 'en-US', EUR: 'de-DE', JPY: 'ja-JP',
		GBP: 'en-GB', SGD: 'en-SG', AUD: 'en-AU', CNY: 'zh-CN',
		KRW: 'ko-KR', MYR: 'ms-MY', THB: 'th-TH', AED: 'ar-AE', SAR: 'ar-SA',
	};
	const locale = localeMap[code] ?? 'en-US';
	const fractions = code === 'IDR' || code === 'JPY' || code === 'KRW' ? 0 : 2;
	return new Intl.NumberFormat(locale, {
		style: 'currency',
		currency: code,
		maximumFractionDigits: fractions,
		minimumFractionDigits: fractions === 0 ? 0 : 2,
	});
}

/** Set display currency (dipanggil dari settings/store). */
export function setDisplayCurrency(code: string) {
	_displayCurrency = code.toUpperCase();
	_formatter = _makeFormatter(_displayCurrency);
}

/** Get current display currency code. */
export function getDisplayCurrency(): string {
	return _displayCurrency;
}

/** Format amount dengan display currency aktif. */
export function formatCurrency(amount: number): string {
	return _formatter.format(toFiniteNumber(amount));
}

/** Format amount dengan currency code spesifik. */
export function formatCurrencyAs(amount: number, code: string): string {
	return _makeFormatter(code).format(toFiniteNumber(amount));
}

// Backward-compatible: object dengan .format() method (seperti Intl.NumberFormat)
export const currency = {
	format: formatCurrency,
};

/**
 * Paksa nilai apa pun menjadi angka finite. `Intl.NumberFormat.format(undefined)`
 * menghasilkan "NaN" (mis. "RpNaN"), yang bocor ke UI ketika sebuah field opsional
 * (mis. `line.unitPrice`) tidak ada. Semua nilai non-finite → 0 agar formatter
 * aman dipakai langsung pada data backend yang mungkin parsial.
 */
export function toFiniteNumber(value: unknown): number {
	const n = typeof value === 'number' ? value : Number(value);
	return Number.isFinite(n) ? n : 0;
}

/**
 * Outstanding = max(total - paid, 0). Piutang tak pernah negatif walau
 * pembayaran melebihi total (overpay), yang sebelumnya tampil "-Rp 1".
 */
export function outstandingAmount(total: unknown, paid: unknown): number {
	return Math.max(toFiniteNumber(total) - toFiniteNumber(paid), 0);
}

/** Format jumlah angka dengan pemisah ribuan sesuai locale aktif. */
const _numberLocaleMap: Record<string, string> = {
	IDR: 'id-ID', USD: 'en-US', EUR: 'de-DE', JPY: 'ja-JP', GBP: 'en-GB',
	SGD: 'en-SG', AUD: 'en-AU', CNY: 'zh-CN', KRW: 'ko-KR', MYR: 'ms-MY',
	THB: 'th-TH', AED: 'ar-AE', SAR: 'ar-SA'
};

export function formatNumber(value: number): string {
	const locale = _numberLocaleMap[_displayCurrency] ?? 'id-ID';
	return new Intl.NumberFormat(locale).format(toFiniteNumber(value));
}

// ─── Status tone ─────────────────────────────────────────────────────────────
export function statusTone(status: TaskStatus | RiskLevel | DocumentItem['status'] | string) {
	if (['Verified', 'Ready', 'Approved', 'Passed', 'Done', 'Delivered', 'Low', 'Enriched', 'Qualified', 'Active', 'Settled', 'Deposit Paid', 'Info', 'Read', 'Connected', 'Resolved', 'Complete', 'Published', 'Matched'].includes(status)) return 'green';
	if (['In Review', 'Evidence Uploaded', 'Needs Review', 'Current', 'Loaded', 'Customs Submitted', 'In Transit', 'Medium', 'Needs HS Review', 'Needs Evidence', 'Due Soon', 'Pending', 'Open', 'In Progress', 'Warning', 'Scheduled', 'Invited', 'Unread', 'Available', 'Needs Auth', 'Waiting Reply', 'Missing Metadata', 'Trial', 'Expiring Soon', 'Draft', 'New', 'Quoted'].includes(status)) return 'orange';
	if (['Blocked', 'Missing', 'Failed', 'Exception', 'High', 'Critical', 'At Risk', 'Overdue', 'Suspended', 'Error', 'Escalated', 'Past Due', 'Cancelled', 'Revoked'].includes(status)) return 'red';
	return 'blue';
}

export type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline';

/**
 * Petakan "tone" dari `statusTone()` ke varian Badge UI.
 *
 * Sebelumnya fungsi identik ini disalin ke 63 berkas rute; sekarang menjadi
 * satu sumber agar palet status konsisten di seluruh aplikasi.
 */
export function toneVariant(tone: string): BadgeVariant {
	if (tone === 'green') return 'default';
	if (tone === 'red') return 'destructive';
	if (tone === 'orange') return 'outline';
	return 'secondary';
}

export function taskSummary(tasks: ComplianceTask[]) {
	return {
		verified: tasks.filter((task) => task.status === 'Verified').length,
		blocked: tasks.filter((task) => task.status === 'Blocked').length,
		pending: tasks.filter((task) => task.status !== 'Verified').length
	};
}
