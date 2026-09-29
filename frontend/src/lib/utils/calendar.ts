/**
 * Utilitas kalender bulanan murni (tanpa DOM) untuk komponen CalendarGrid.
 *
 * Dipisah agar logika penanggalan (grid 6×7, penanda hari, kunci tanggal) dapat
 * diuji unit tanpa merender komponen.
 */

/** Normalisasi tanggal apa pun (ISO / "YYYY-MM-DD HH:mm") → "YYYY-MM-DD". */
export function dayKey(value: unknown): string {
	const m = /^(\d{4}-\d{2}-\d{2})/.exec(String(value ?? ''));
	return m ? m[1] : '';
}

/** Kunci hari dari objek Date lokal → "YYYY-MM-DD". */
export function isoDate(d: Date): string {
	return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/** Kelompokkan event berdasarkan kunci hari (YYYY-MM-DD). */
export function groupEventsByDay<T extends { date: string }>(events: T[]): Map<string, T[]> {
	const map = new Map<string, T[]>();
	for (const ev of events) {
		const key = dayKey(ev.date);
		if (!key) continue;
		const list = map.get(key) ?? [];
		list.push(ev);
		map.set(key, list);
	}
	return map;
}

export type CalendarCell<T> = {
	date: string;
	day: number;
	inMonth: boolean;
	isToday: boolean;
	isSelected: boolean;
	events: T[];
};

/**
 * Bangun sel grid kalender bulanan: 42 hari (6 minggu) dimulai Senin pada
 * minggu pertama bulan `year`/`month` (month 0-11). Setiap sel menandai apakah
 * tanggal berada di bulan berjalan, "hari ini", terpilih, dan daftar event-nya.
 */
export function buildMonthCells<T extends { date: string }>(
	year: number,
	month: number,
	opts: { events?: T[]; selected?: string; today?: string } = {}
): CalendarCell<T>[] {
	const byDay = groupEventsByDay(opts.events ?? []);
	const today = opts.today ?? isoDate(new Date());
	const selected = opts.selected ?? '';
	const first = new Date(year, month, 1);
	const offset = (first.getDay() + 6) % 7; // Senin = 0
	const start = new Date(year, month, 1 - offset);
	const cells: CalendarCell<T>[] = [];
	for (let i = 0; i < 42; i++) {
		const d = new Date(start.getFullYear(), start.getMonth(), start.getDate() + i);
		const key = isoDate(d);
		cells.push({
			date: key,
			day: d.getDate(),
			inMonth: d.getMonth() === month && d.getFullYear() === year,
			isToday: key === today,
			isSelected: key === selected,
			events: byDay.get(key) ?? []
		});
	}
	return cells;
}

/** Offset (0=Senin..6=Minggu) kolom awal bulan — berguna untuk header. */
export function mondayFirstWeekdays(): number[] {
	return [0, 1, 2, 3, 4, 5, 6];
}

/** Hitung bulan sebelumnya/berikutnya sebagai {year, month}. */
export function shiftMonth(year: number, month: number, delta: number): { year: number; month: number } {
	const d = new Date(year, month + delta, 1);
	return { year: d.getFullYear(), month: d.getMonth() };
}
