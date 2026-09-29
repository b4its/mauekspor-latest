import { describe, expect, it } from 'vitest';
import {
	buildMonthCells,
	dayKey,
	groupEventsByDay,
	isoDate,
	shiftMonth
} from './calendar';

describe('dayKey', () => {
	it('mengambil bagian tanggal dari berbagai format', () => {
		expect(dayKey('2026-08-07')).toBe('2026-08-07');
		expect(dayKey('2026-08-07 10:42')).toBe('2026-08-07');
		expect(dayKey('2026-08-07T10:42:00Z')).toBe('2026-08-07');
	});

	it('mengembalikan string kosong untuk nilai tak valid', () => {
		expect(dayKey('')).toBe('');
		expect(dayKey('now')).toBe('');
		expect(dayKey(null)).toBe('');
		expect(dayKey(undefined)).toBe('');
	});
});

describe('isoDate', () => {
	it('memformat Date lokal ke YYYY-MM-DD dengan padding', () => {
		expect(isoDate(new Date(2026, 7, 7))).toBe('2026-08-07');
		expect(isoDate(new Date(2026, 0, 1))).toBe('2026-01-01');
	});
});

describe('groupEventsByDay', () => {
	it('mengelompokkan event per hari dan mengabaikan tanggal kosong', () => {
		const events = [
			{ id: 'a', date: '2026-08-07' },
			{ id: 'b', date: '2026-08-07 09:00' },
			{ id: 'c', date: '2026-08-08' },
			{ id: 'd', date: '' }
		];
		const map = groupEventsByDay(events);
		expect(map.get('2026-08-07')?.map((e) => e.id)).toEqual(['a', 'b']);
		expect(map.get('2026-08-08')?.map((e) => e.id)).toEqual(['c']);
		expect(map.size).toBe(2);
	});
});

describe('buildMonthCells', () => {
	const events = [
		{ id: 'a', date: '2026-08-07' },
		{ id: 'b', date: '2026-08-07' },
		{ id: 'c', date: '2026-08-20' }
	];

	it('menghasilkan 42 sel (6 minggu)', () => {
		const cells = buildMonthCells(2026, 7, { events });
		expect(cells).toHaveLength(42);
	});

	it('dimulai pada hari Senin', () => {
		const cells = buildMonthCells(2026, 7, { events });
		// 2026-08-01 jatuh pada hari Sabtu → minggu pertama mulai 2026-07-27 (Senin).
		expect(cells[0].date).toBe('2026-07-27');
	});

	it('menandai sel di luar bulan berjalan', () => {
		const cells = buildMonthCells(2026, 7, { events });
		const inMonth = cells.filter((c) => c.inMonth);
		expect(inMonth[0].date).toBe('2026-08-01');
		expect(inMonth[inMonth.length - 1].date).toBe('2026-08-31');
		expect(cells[0].inMonth).toBe(false); // 27 Jul
	});

	it('menempelkan event pada tanggal yang tepat', () => {
		const cells = buildMonthCells(2026, 7, { events });
		const d7 = cells.find((c) => c.date === '2026-08-07');
		const d20 = cells.find((c) => c.date === '2026-08-20');
		const d8 = cells.find((c) => c.date === '2026-08-08');
		expect(d7?.events).toHaveLength(2);
		expect(d20?.events).toHaveLength(1);
		expect(d8?.events).toHaveLength(0);
	});

	it('menandai hari ini & tanggal terpilih', () => {
		const cells = buildMonthCells(2026, 7, {
			events,
			today: '2026-08-07',
			selected: '2026-08-20'
		});
		expect(cells.find((c) => c.date === '2026-08-07')?.isToday).toBe(true);
		expect(cells.find((c) => c.date === '2026-08-20')?.isSelected).toBe(true);
		expect(cells.find((c) => c.date === '2026-08-01')?.isToday).toBe(false);
	});
});

describe('shiftMonth', () => {
	it('maju & mundur melewati batas tahun', () => {
		expect(shiftMonth(2026, 11, 1)).toEqual({ year: 2027, month: 0 });
		expect(shiftMonth(2026, 0, -1)).toEqual({ year: 2025, month: 11 });
		expect(shiftMonth(2026, 7, 1)).toEqual({ year: 2026, month: 8 });
	});
});
