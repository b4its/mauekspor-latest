<script lang="ts">
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { t } from '$lib/i18n.svelte';

	import MapPinIcon from '@lucide/svelte/icons/map-pin';
	import SproutIcon from '@lucide/svelte/icons/sprout';

	type VillagePotensi = {
		id: string;
		name: string;
		commodity: string;
		region: string;
		production: string;
		readiness: number;
		x: number;
		y: number;
	};

	// Desa fiktif untuk demo — posisi pin dalam koordinat viewBox peta.
	const villages: VillagePotensi[] = [
		{ id: 'DES-GAYO', name: 'Desa Kopi Gayo', commodity: 'Kopi Arabika', region: 'Aceh Tengah, Aceh', production: '8.000 bag / bulan', readiness: 86, x: 104, y: 64 },
		{ id: 'DES-KAHAYAN', name: 'Desa Rotan Kahayan', commodity: 'Kerajinan Rotan', region: 'Kalimantan Tengah', production: '200 pcs / bulan', readiness: 72, x: 306, y: 106 },
		{ id: 'DES-TORAJA', name: 'Desa Kakao Toraja', commodity: 'Kakao Fermentasi', region: 'Sulawesi Selatan', production: '3 ton / bulan', readiness: 81, x: 442, y: 148 },
		{ id: 'DES-VANILI-BALI', name: 'Desa Vanili Bali', commodity: 'Vanili Planifolia', region: 'Tabanan, Bali', production: '50 kg / bulan', readiness: 77, x: 428, y: 222 },
		{ id: 'DES-SITUBONDO', name: 'Desa Manggis Situbondo', commodity: 'Manggis Premium', region: 'Situbondo, Jawa Timur', production: '600 kg / musim', readiness: 68, x: 382, y: 199 }
	];

	let selectedId = $state(villages[0].id);
	let selected = $derived(villages.find((v) => v.id === selectedId) ?? villages[0]);

	function readinessColor(score: number) {
		if (score >= 80) return 'bg-emerald-500';
		if (score >= 70) return 'bg-amber-500';
		return 'bg-orange-500';
	}

	function readinessFill(score: number) {
		if (score >= 80) return 'fill-emerald-500';
		if (score >= 70) return 'fill-amber-500';
		return 'fill-orange-500';
	}
</script>

<Card>
	<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
		<div>
			<Badge variant="secondary" class="gap-1"><SproutIcon class="size-3" />{t('Komoditas Unggulan Desa')}</Badge>
			<CardTitle class="mt-2 text-xl font-bold tracking-tight">{t('Peta Potensi Desa')}</CardTitle>
			<CardDescription>{t('Sebaran desa mitra dan komoditas unggulannya.')}</CardDescription>
		</div>
		<span class="text-xs font-semibold text-muted-foreground">{villages.length} {t('desa mitra')}</span>
	</CardHeader>
	<CardContent class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(220px,280px)]">
		<!-- Peta Indonesia bergaya (SVG sederhana, tanpa dependensi eksternal) -->
		<div class="overflow-hidden rounded-xl border bg-gradient-to-br from-sky-50 to-blue-100 dark:from-[#0a1730] dark:to-[#0c2145]">
			<svg viewBox="0 0 560 250" class="h-auto w-full" role="img" aria-label={t('Peta Potensi Desa')}>
				<g class="fill-[#1e63d6]/20 stroke-[#0b3d91]/40 dark:fill-white/10 dark:stroke-white/25" stroke-width="1">
					<!-- Sumatra -->
					<path d="M38 28 Q52 22 66 34 Q84 50 96 72 Q108 94 122 112 Q132 124 128 134 Q120 142 108 136 Q92 128 78 110 Q60 88 48 66 Q38 48 34 38 Q34 32 38 28 Z" />
					<!-- Jawa -->
					<path d="M268 192 Q290 186 316 190 Q346 194 372 198 Q396 202 414 206 Q424 209 420 216 Q412 222 394 220 Q368 218 342 214 Q310 210 284 204 Q270 200 268 196 Z" />
					<!-- Kalimantan -->
					<path d="M276 58 Q296 44 320 50 Q344 56 356 76 Q366 96 360 118 Q352 140 332 148 Q310 154 294 142 Q278 130 272 108 Q266 84 276 58 Z" />
					<!-- Sulawesi -->
					<path d="M436 84 Q452 74 464 84 Q472 92 464 102 Q456 110 452 122 Q450 138 458 150 Q464 162 456 172 Q446 180 438 170 Q430 158 432 140 Q434 122 430 106 Q428 92 436 84 Z" />
					<path d="M452 128 Q470 122 484 130 Q494 138 488 148 Q480 156 466 152 Q454 148 450 140 Z" />
					<!-- Nusa Tenggara -->
					<path d="M430 216 Q446 212 462 216 Q476 220 492 218 Q504 217 512 222 Q514 228 504 230 Q486 232 468 228 Q448 226 434 226 Q426 224 430 216 Z" />
					<!-- Maluku & Papua (potongan) -->
					<path d="M508 96 Q522 88 534 98 Q542 108 536 120 Q528 130 516 126 Q506 120 506 108 Z" />
					<path d="M540 60 Q554 54 560 62 L560 130 Q550 132 542 122 Q534 108 536 88 Q537 70 540 60 Z" />
				</g>

				{#each villages as village (village.id)}
					{@const isSelected = village.id === selectedId}
					<g
						class="cursor-pointer"
						role="button"
						tabindex="0"
						onclick={() => (selectedId = village.id)}
						onkeydown={(e) => e.key === 'Enter' && (selectedId = village.id)}
					>
						<!-- halo pulse -->
						<circle cx={village.x} cy={village.y} r="10" class="fill-emerald-500/20 animate-pulse" />
						<circle
							cx={village.x}
							cy={village.y}
							r={isSelected ? 6 : 4.5}
							class={`fill-current ${readinessFill(village.readiness)} stroke-white transition-all`}
							stroke-width={isSelected ? 2 : 1.5}
						/>
						<text
							x={village.x}
							y={village.y - 11}
							text-anchor="middle"
							class={`pointer-events-none text-[9px] font-bold ${isSelected ? 'fill-[#0b1d3a] dark:fill-white' : 'fill-[#0b1d3a]/60 dark:fill-white/60'}`}
						>
							{village.name}
						</text>
					</g>
				{/each}
			</svg>
		</div>

		<!-- Detail desa terpilih -->
		<div class="flex flex-col gap-2.5">
			<div class="rounded-xl border bg-muted/30 p-4">
				<div class="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-muted-foreground">
					<MapPinIcon class="size-3.5" />
					{selected.region}
				</div>
				<h3 class="mt-1 text-lg font-black tracking-tight">{selected.name}</h3>
				<div class="mt-0.5">
					<Badge variant={selected.status === "Siap Ekspor" ? "default" : "secondary"} class="gap-1 border-transparent bg-emerald-500 text-white dark:bg-emerald-600">
						<span>{selected.status === "Siap Ekspor" ? "✓" : "!"} {selected.status}</span>
					</Badge>
				</div>
				<p class="mt-0.5 flex items-center gap-1.5 text-sm font-semibold text-emerald-700 dark:text-emerald-400">
					<SproutIcon class="size-4" />
					{selected.commodity}
				</p>
				<dl class="mt-3 grid gap-1.5 text-sm">
					<div class="flex items-center justify-between gap-2">
						<dt class="text-muted-foreground">{t('Estimasi produksi')}</dt>
						<dd class="font-bold">{selected.production}</dd>
					</div>
					<div class="flex items-center justify-between gap-2">
						<dt class="text-muted-foreground">{t('Kesiapan ekspor')}</dt>
						<dd class="font-bold">{selected.readiness}%</dd>
					</div>
				</dl>
				<div class="mt-2.5 h-2 overflow-hidden rounded-full bg-muted">
					<div class={`h-full rounded-full ${readinessColor(selected.readiness)}`} style={`width:${selected.readiness}%`}></div>
				</div>
			</div>
			<div class="grid gap-1.5">
				{#each villages as village (village.id)}
					<button
						type="button"
						onclick={() => (selectedId = village.id)}
						class={`flex items-center justify-between gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
							village.id === selectedId
								? 'border-ring/60 bg-accent font-bold'
								: 'bg-muted/20 hover:border-ring/40 hover:bg-muted/40'
						}`}
					>
						<span class="truncate">{village.name}</span>
						<span class="shrink-0 text-xs text-muted-foreground">{village.commodity}</span>
					</button>
				{/each}
			</div>
			<p class="text-xs leading-snug text-muted-foreground">{t('Data demo — klik pin pada peta atau pilih desa untuk melihat detail.')}</p>
		</div>
	</CardContent>
</Card>
