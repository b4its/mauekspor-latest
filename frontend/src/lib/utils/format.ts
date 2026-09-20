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
	return _formatter.format(amount);
}

/** Format amount dengan currency code spesifik. */
export function formatCurrencyAs(amount: number, code: string): string {
	return _makeFormatter(code).format(amount);
}

// Backward-compatible: object dengan .format() method (seperti Intl.NumberFormat)
export const currency = {
	format: formatCurrency,
};

// ─── Status tone ─────────────────────────────────────────────────────────────
export function statusTone(status: TaskStatus | RiskLevel | DocumentItem['status'] | string) {
	if (['Verified', 'Ready', 'Approved', 'Passed', 'Done', 'Delivered', 'Low', 'Enriched', 'Qualified', 'Active', 'Settled', 'Deposit Paid', 'Info', 'Read', 'Connected', 'Resolved', 'Complete', 'Published', 'Matched'].includes(status)) return 'green';
	if (['In Review', 'Evidence Uploaded', 'Needs Review', 'Current', 'Loaded', 'Customs Submitted', 'In Transit', 'Medium', 'Needs HS Review', 'Needs Evidence', 'Due Soon', 'Pending', 'Open', 'In Progress', 'Warning', 'Scheduled', 'Invited', 'Unread', 'Available', 'Needs Auth', 'Waiting Reply', 'Missing Metadata', 'Trial', 'Expiring Soon', 'Draft', 'New', 'Quoted'].includes(status)) return 'orange';
	if (['Blocked', 'Missing', 'Failed', 'Exception', 'High', 'Critical', 'At Risk', 'Overdue', 'Suspended', 'Error', 'Escalated', 'Past Due', 'Cancelled', 'Revoked'].includes(status)) return 'red';
	return 'blue';
}

export function taskSummary(tasks: ComplianceTask[]) {
	return {
		verified: tasks.filter((task) => task.status === 'Verified').length,
		blocked: tasks.filter((task) => task.status === 'Blocked').length,
		pending: tasks.filter((task) => task.status !== 'Verified').length
	};
}
