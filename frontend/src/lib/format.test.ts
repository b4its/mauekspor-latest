import { describe, expect, it } from 'vitest';
import { currency, formatCurrency, formatNumber, outstandingAmount, setDisplayCurrency, statusTone, taskSummary, toFiniteNumber } from './utils/format';
import type { ComplianceTask } from './data/trade';

describe('currency formatter', () => {
	it('memformat IDR (default) tanpa desimal', () => {
		expect(currency.format(0)).toMatch(/Rp.*0/);
		expect(currency.format(42800)).toMatch(/Rp.*42.*800/);
		expect(currency.format(1000000)).toMatch(/Rp.*1.*000.*000/);
	});

	it('bisa switch ke USD', () => {
		setDisplayCurrency('USD');
		expect(currency.format(42800)).toMatch(/\$42,800/);
		setDisplayCurrency('IDR'); // reset
	});

	it('bisa switch ke EUR', () => {
		setDisplayCurrency('EUR');
		expect(currency.format(1000)).toMatch(/1.*000/);
		setDisplayCurrency('IDR'); // reset
	});

	it('formatCurrency helper bekerja', () => {
		setDisplayCurrency('IDR');
		expect(formatCurrency(50000)).toMatch(/Rp.*50.*000/);
	});

	it('formatNumber memakai pemisah ribuan sesuai locale', () => {
		setDisplayCurrency('IDR');
		expect(formatNumber(1234567)).toBe('1.234.567');
		setDisplayCurrency('USD');
		expect(formatNumber(1234567)).toBe('1,234,567');
		setDisplayCurrency('IDR'); // reset
	});

	it('getDisplayCurrency return code aktif', () => {
		setDisplayCurrency('USD');
		expect(currency.format(100)).toMatch(/\$/);
		setDisplayCurrency('IDR'); // reset
	});

	it('tidak pernah menghasilkan NaN untuk input tidak valid', () => {
		setDisplayCurrency('IDR');
		for (const bad of [undefined, null, NaN, Infinity, -Infinity]) {
			expect(currency.format(bad as unknown as number)).not.toMatch(/NaN/);
		}
	});

	it('toFiniteNumber mengoersi non-finite jadi 0', () => {
		expect(toFiniteNumber(undefined)).toBe(0);
		expect(toFiniteNumber(null)).toBe(0);
		expect(toFiniteNumber(NaN)).toBe(0);
		expect(toFiniteNumber('42800')).toBe(42800);
		expect(toFiniteNumber(42.5)).toBe(42.5);
	});

	it('outstandingAmount tidak pernah negatif (clamp overpay)', () => {
		expect(outstandingAmount(1000, 400)).toBe(600);
		expect(outstandingAmount(1000, 1000)).toBe(0);
		expect(outstandingAmount(1000, 1200)).toBe(0); // overpay -> 0, bukan -200
		expect(outstandingAmount(undefined, undefined)).toBe(0);
	});
});

describe('statusTone', () => {
	it('status positif -> green', () => {
		for (const s of ['Verified', 'Ready', 'Approved', 'Done', 'Active', 'Published', 'Resolved', 'Complete', 'Qualified']) {
			expect(statusTone(s), s).toBe('green');
		}
	});

	it('status menengah -> orange', () => {
		for (const s of ['In Review', 'Pending', 'Open', 'In Progress', 'Draft', 'Needs Review', 'Due Soon', 'Warning', 'New', 'Invited']) {
			expect(statusTone(s), s).toBe('orange');
		}
	});

	it('status kritis -> red', () => {
		for (const s of ['Blocked', 'Missing', 'Failed', 'Exception', 'High', 'Critical', 'At Risk', 'Overdue', 'Escalated', 'Cancelled']) {
			expect(statusTone(s), s).toBe('red');
		}
	});

	it('status tidak dikenal -> blue', () => {
		expect(statusTone('Whatever Unknown Status')).toBe('blue');
		expect(statusTone('')).toBe('blue');
	});
});

describe('taskSummary', () => {
	const tasks = [
		{ id: 't1', status: 'Verified' },
		{ id: 't2', status: 'Verified' },
		{ id: 't3', status: 'Blocked' },
		{ id: 't4', status: 'Pending' }
	] as unknown as ComplianceTask[];

	it('menghitung verified, blocked, dan pending', () => {
		const summary = taskSummary(tasks);
		expect(summary.verified).toBe(2);
		expect(summary.blocked).toBe(1);
		expect(summary.pending).toBe(2); // bukan Verified (Blocked + Pending)
	});

	it('daftar kosong -> semua nol', () => {
		expect(taskSummary([])).toEqual({ verified: 0, blocked: 0, pending: 0 });
	});
});
