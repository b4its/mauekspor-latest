<script lang="ts">
	/**
	 * Kalender bulanan (gaya kalender asli) dengan penanda (mark) per agenda.
	 *
	 * Menampilkan grid nyata 7 kolom × 6 baris untuk satu bulan, menandai tanggal
	 * yang memiliki event dengan titik berwarna sesuai tipe + jumlah event, serta
	 * menandai "hari ini" dan tanggal terpilih. Klik tanggal untuk memilih hari
	 * (agenda hari itu ditampilkan oleh pemanggil melalui callback `onselect`).
	 *
	 * Murni Svelte + Intl (tanpa dependensi baru). Minggu dimulai Senin agar
	 * sesuai kebiasaan id-ID; nama hari/bulan mengikuti locale aktif.
	 */
	import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import { untrack } from 'svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { i18n, t } from '$lib/i18n.svelte';
	import { buildMonthCells, dayKey, isoDate, shiftMonth as shiftMonthPure } from '$lib/utils/calendar';

	export type CalendarGridEvent = {
		id: string;
		title: string;
		date: string; // YYYY-MM-DD (atau ISO)
		time?: string;
		type: string;
	};

	type Props = {
		events: CalendarGridEvent[];
		/** Tanggal terpilih (YYYY-MM-DD). */
		selected?: string;
		/** Bulan awal yang ditampilkan (YYYY-MM). Default: bulan dari `selected`/hari ini. */
		initialMonth?: string;
		onselect?: (date: string) => void;
	};
	let { events, selected = '', initialMonth = '', onselect }: Props = $props();

	const LOCALE_MAP: Record<string, string> = { id: 'id-ID', en: 'en-US' };
	function locale(): string {
		return LOCALE_MAP[i18n.locale] ?? 'id-ID';
	}

	const today = isoDate(new Date());

	function monthFromKey(key: string): { year: number; month: number } {
		const m = /^(\d{4})-(\d{2})/.exec(key ?? '');
		if (m) return { year: Number(m[1]), month: Number(m[2]) - 1 };
		const base = selected ? new Date(`${dayKey(selected)}T00:00:00`) : new Date();
		const safe = Number.isNaN(base.getTime()) ? new Date() : base;
		return { year: safe.getFullYear(), month: safe.getMonth() };
	}

	// Bulan yang sedang ditampilkan (indeks 0-11). Sengaja hanya menangkap nilai
	// AWAL dari prop — perubahan bulan berikutnya dikendalikan lewat navigasi UI.
	let view = $state(untrack(() => monthFromKey(initialMonth || selected)));

	function shiftMonth(delta: number) {
		view = shiftMonthPure(view.year, view.month, delta);
	}
	function goToday() {
		const now = new Date();
		view = { year: now.getFullYear(), month: now.getMonth() };
		if (onselect) onselect(today);
	}

	// Kelompokkan event per hari (YYYY-MM-DD).
	const DEFAULT_COLORS: Record<string, string> = {
		Compliance: 'bg-red-500',
		Payment: 'bg-emerald-500',
		Shipment: 'bg-blue-500',
		Buyer: 'bg-violet-500',
		Supplier: 'bg-amber-500'
	};
	function dotColor(type: string): string {
		return DEFAULT_COLORS[type] ?? 'bg-slate-400';
	}

	// Sel grid: 42 hari (6 minggu) dimulai dari Senin pada minggu pertama bulan.
	let cells = $derived(buildMonthCells(view.year, view.month, { events, selected, today }));

	// Judul bulan (mis. "Agustus 2026").
	let monthLabel = $derived(
		new Intl.DateTimeFormat(locale(), { month: 'long', year: 'numeric' }).format(new Date(view.year, view.month, 1))
	);

	// Nama hari ringkas, Senin→Minggu.
	let weekdays = $derived.by(() => {
		const fmt = new Intl.DateTimeFormat(locale(), { weekday: 'short' });
		// 2024-01-01 adalah hari Senin.
		return Array.from({ length: 7 }, (_, i) => fmt.format(new Date(2024, 0, 1 + i)));
	});

	let monthEventCount = $derived(
		cells.filter((c) => c.inMonth).reduce((sum, c) => sum + c.events.length, 0)
	);

	const MAX_DOTS = 4;
</script>

<div class="rounded-xl border bg-card p-4">
	<div class="flex items-center justify-between gap-3">
		<div class="min-w-0">
			<h3 class="font-display text-lg font-black tracking-tight text-[#0b1d3a] dark:text-white">{monthLabel}</h3>
			<p class="text-xs font-semibold text-muted-foreground">{monthEventCount} {t('agenda bulan ini')}</p>
		</div>
		<div class="flex items-center gap-1">
			<Button variant="outline" size="icon" aria-label={t('Bulan sebelumnya')} onclick={() => shiftMonth(-1)}>
				<ChevronLeftIcon class="size-4" />
			</Button>
			<Button variant="outline" size="sm" onclick={goToday}>{t('Hari ini')}</Button>
			<Button variant="outline" size="icon" aria-label={t('Bulan berikutnya')} onclick={() => shiftMonth(1)}>
				<ChevronRightIcon class="size-4" />
			</Button>
		</div>
	</div>

	<div class="mt-4 grid grid-cols-7 gap-1 text-center">
		{#each weekdays as wd}
			<span class="pb-1 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">{wd}</span>
		{/each}
	</div>

	<div class="grid grid-cols-7 gap-1">
		{#each cells as cell}
			<button
				type="button"
				onclick={() => onselect?.(cell.date)}
				aria-label={`${cell.date}${cell.events.length ? ` · ${cell.events.length} ${t('agenda')}` : ''}`}
				aria-current={cell.isToday ? 'date' : undefined}
				class="group relative flex min-h-16 flex-col items-stretch gap-1 rounded-lg border p-1.5 text-left transition-colors
					{cell.inMonth ? 'bg-background hover:bg-muted/50' : 'bg-muted/20 text-muted-foreground/60'}
					{cell.isSelected ? 'border-primary ring-2 ring-primary/40' : 'border-border/60'}"
			>
				<span
					class="inline-flex size-6 items-center justify-center rounded-full text-xs font-bold
						{cell.isToday ? 'bg-[#0b3d91] text-white dark:bg-[#5ea1ff] dark:text-[#04122b]' : 'text-foreground'}"
				>{cell.day}</span>

				{#if cell.events.length}
					<span class="flex flex-wrap items-center gap-0.5">
						{#each cell.events.slice(0, MAX_DOTS) as ev}
							<span class="size-1.5 rounded-full {dotColor(ev.type)}" title={ev.title}></span>
						{/each}
						{#if cell.events.length > MAX_DOTS}
							<span class="text-[10px] font-bold text-muted-foreground">+{cell.events.length - MAX_DOTS}</span>
						{/if}
					</span>
					<span class="mt-auto hidden truncate text-[10px] font-semibold text-muted-foreground sm:block">
						{cell.events[0].title}
					</span>
				{/if}
			</button>
		{/each}
	</div>

	<div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] font-semibold text-muted-foreground">
		{#each Object.entries(DEFAULT_COLORS) as [type, color]}
			<span class="inline-flex items-center gap-1.5"><span class="size-2 rounded-full {color}"></span>{type}</span>
		{/each}
	</div>
</div>
