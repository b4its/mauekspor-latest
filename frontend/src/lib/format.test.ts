import { describe, expect, it } from 'vitest';
import { currency, statusTone, taskSummary } from './utils/format';
import type { ComplianceTask } from './data/trade';

describe('currency formatter', () => {
	it('memformat USD tanpa desimal', () => {
		expect(currency.format(0)).toBe('$0');
		expect(currency.format(42800)).toBe('$42,800');
		expect(currency.format(1000000)).toBe('$1,000,000');
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
