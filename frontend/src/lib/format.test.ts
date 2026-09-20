import { describe, expect, it } from 'vitest';
import { currency, formatCurrency, setDisplayCurrency, statusTone, taskSummary } from './utils/format';
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

	it('getDisplayCurrency return code aktif', () => {
		setDisplayCurrency('USD');
		expect(currency.format(100)).toMatch(/\$/);
		setDisplayCurrency('IDR'); // reset
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
