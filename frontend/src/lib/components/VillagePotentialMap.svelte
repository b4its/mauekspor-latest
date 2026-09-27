<script lang="ts">
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import SproutIcon from '@lucide/svelte/icons/sprout';
	import { t } from '$lib/i18n.svelte';
	import { onMount, onDestroy } from 'svelte';
	import { getVillageMapPoints } from '$lib/api/villages';

	// Import Leaflet CSS
	import 'leaflet/dist/leaflet.css';

	let mapContainer: HTMLDivElement | null = null;
	let mapInstance: any = null;
	let markers: Array<any> = [];
	let isLoading = $state(true);
	let loadFailed = $state(false);

	type VillagePoint = {
		id: string;
		name: string;
		commodity: string;
		region: string;
		production: string;
		readiness: number;
		status: 'Siap Ekspor' | 'Butuh Pendampingan' | string;
		lat: number;
		lng: number;
	};

	// Fallback offline: dipakai hanya bila API desa tidak dapat dijangkau,
	// agar peta tidak kosong. Sumber utama tetap tabel `villages`.
	const seedPoints: VillagePoint[] = [
		{ id: 'DES-GAYO', name: 'Desa Kopi Gayo', commodity: 'Kopi Arabika', region: 'Aceh Tengah, Aceh', production: '8 ton / bulan', readiness: 86, status: 'Siap Ekspor', lat: 4.5074, lng: 96.8557 },
		{ id: 'DES-VANILI-BALI', name: 'Desa Vanili Bali', commodity: 'Vanili Planifolia', region: 'Tabanan, Bali', production: '50 kg / bulan', readiness: 77, status: 'Butuh Pendampingan', lat: -8.5955, lng: 115.1121 },
		{ id: 'DES-SITUBONDO', name: 'Desa Manggis Situbondo', commodity: 'Manggis Premium', region: 'Situbondo, Jawa Timur', production: '600 kg / musim', readiness: 68, status: 'Butuh Pendampingan', lat: -7.4091, lng: 114.1161 },
		{ id: 'DES-TORAJA', name: 'Desa Kakao Toraja', commodity: 'Kakao Fermentasi', region: 'Toraja Utara, Sulawesi Selatan', production: '3 ton / bulan', readiness: 81, status: 'Siap Ekspor', lat: -2.9267, lng: 119.3334 },
		{ id: 'DES-KAHAYAN', name: 'Desa Rotan Kahayan', commodity: 'Kerajinan Rotan', region: 'Pulang Pisau, Kalimantan Tengah', production: '200 pcs / bulan', readiness: 72, status: 'Butuh Pendampingan', lat: -2.0194, lng: 114.8025 },
		{ id: 'DES-SUMBAWA', name: 'Desa Madu Sumbawa', commodity: 'Madu Hutan', region: 'Dompu, NTB', production: '480 jar / bulan', readiness: 84, status: 'Siap Ekspor', lat: -8.5932, lng: 118.4586 },
		{ id: 'DES-TERNATE', name: 'Desa Cengkeh Ternate', commodity: 'Cengkeh Grade A', region: 'Ternate, Maluku Utara', production: '2 ton / musim', readiness: 75, status: 'Butuh Pendampingan', lat: 0.7833, lng: 127.3667 },
		{ id: 'DES-MUNTOK', name: 'Desa Lada Putih Muntok', commodity: 'Lada Putih Muntok', region: 'Bangka Barat, Kep. Bangka Belitung', production: '1,5 ton / bulan', readiness: 70, status: 'Butuh Pendampingan', lat: -2.8967, lng: 105.8601 },
		{ id: 'DES-KERINCI', name: 'Desa Kayu Manis Kerinci', commodity: 'Kayu Manis (Kassia)', region: 'Kerinci, Jambi', production: '1 ton bale / bulan', readiness: 74, status: 'Butuh Pendampingan', lat: -1.5786, lng: 101.3261 },
	];

	// Daftar desa yang ditampilkan: dari API, atau fallback bila gagal.
	let villages = $state<VillagePoint[]>([]);
	let dataSource = $state<'api' | 'fallback'>('api');

	async function loadVillages() {
		try {
			const res = await getVillageMapPoints();
			const points = (res.data ?? []) as VillagePoint[];
			villages = points.length > 0 ? points : seedPoints;
			dataSource = points.length > 0 ? 'api' : 'fallback';
		} catch {
			villages = seedPoints;
			dataSource = 'fallback';
			loadFailed = true;
		}
	}

	function getStatusColor(status: string): string {
		return status === 'Siap Ekspor' ? 'bg-emerald-500 text-white' : 'bg-amber-500 text-white';
	}

	onMount(async () => {
		await loadVillages();
		if (import.meta.env.SSR) return;

		try {
			isLoading = true;

			// Ensure container exists
			if (!mapContainer) {
				return;
			}

			// Dynamically import Leaflet JS (client-only, safe for SSR)
			const L = await import('leaflet');

			// Give DOM time to render
			await new Promise(resolve => requestAnimationFrame(resolve));

			// Create map centered on Indonesia
			mapInstance = L.map(mapContainer).setView([-2.5489, 118.0149], 5);

			// Add OpenStreetMap tiles
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				maxZoom: 19,
				minZoom: 4,
				attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				subdomains: 'abc'
			}).addTo(mapInstance);

			// Custom marker icon
			const pinIcon = L.divIcon({
				className: 'village-marker custom-village-marker',
				html: '<div class="marker-inner" style="background: linear-gradient(135deg, #1e63d6, #1e40af); width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.4);"></div>',
				iconSize: [20, 20],
				iconAnchor: [10, 10],
				popupAnchor: [0, -12]
			});
			
			// Gunakan flag untuk mencegah injeksi HTML dari data backend.
			const escapeHtml = (value: unknown) =>
				String(value ?? '').replace(/[&<>"']/g, (ch) =>
					({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch] as string
				);
			function renderMarkers() {
				for (const existing of markers) existing.remove();
				markers = villages
					.filter((v) => Number.isFinite(v.lat) && Number.isFinite(v.lng))
					.map((village) => {
						const popupContent = `<div class="p-2" style="min-width:200px;">
					<h4 class="font-bold text-sm mb-1">${escapeHtml(village.name)}</h4>
					<p class="text-xs opacity-75">${escapeHtml(village.region)}</p>
					<p class="text-xs font-semibold mt-2">${escapeHtml(village.commodity)}</p>
					<p class="text-xs opacity-75">Produksi: ${escapeHtml(village.production)}</p>
					<span class="inline-block mt-2 px-2 py-1 rounded-full text-xs font-bold ${getStatusColor(village.status)}">${escapeHtml(village.status)}</span>
				</div>`;
						return L.marker([village.lat, village.lng], { icon: pinIcon })
							.bindPopup(popupContent)
							.addTo(mapInstance);
					});
				if (markers.length > 0) {
					const group = L.featureGroup(markers);
					mapInstance.fitBounds(group.getBounds(), { padding: [50, 50], maxZoom: 6 });
				}
			}
			renderMarkers();

			isLoading = false;
			
		} catch {
			isLoading = false;
		}
	});

	// Muat ulang marker setiap daftar desa berubah (mis. setelah CRUD di halaman desa).
	$effect(() => {
		const list = villages;
		if (!mapInstance || list.length === 0) return;
		if (typeof window === 'undefined') return;
		import('leaflet').then((L) => {
			const escapeHtml = (value: unknown) =>
				String(value ?? '').replace(/[&<>"']/g, (ch) =>
					({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch] as string
				);
			for (const existing of markers) existing.remove();
			const pinIcon = L.divIcon({
				className: 'village-marker custom-village-marker',
				html: '<div class="marker-inner" style="background: linear-gradient(135deg, #1e63d6, #1e40af); width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.4);"></div>',
				iconSize: [20, 20],
				iconAnchor: [10, 10],
				popupAnchor: [0, -12]
			});
			markers = list
				.filter((v) => Number.isFinite(v.lat) && Number.isFinite(v.lng))
				.map((village) =>
					L.marker([village.lat, village.lng], { icon: pinIcon })
						.bindPopup(
							`<div class="p-2"><h4 class="font-bold text-sm">${escapeHtml(village.name)}</h4>` +
								`<p class="text-xs opacity-75">${escapeHtml(village.region)}</p>` +
								`<p class="text-xs font-semibold mt-2">${escapeHtml(village.commodity)}</p></div>`
						)
						.addTo(mapInstance)
				);
			if (markers.length > 0) {
				mapInstance.fitBounds(L.featureGroup(markers).getBounds(), { padding: [50, 50], maxZoom: 6 });
			}
		});
	});

	onDestroy(() => {
		if (mapInstance) {
			mapInstance.off();
			mapInstance.remove();
			mapInstance = null;
		}
		markers = [];
	});
</script>

<Card>
	<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
		<div>
			<Badge variant="secondary" class="gap-1"><SproutIcon class="size-3" />{t('Komoditas Unggulan Desa')}</Badge>
			<CardTitle class="mt-2 text-xl font-bold tracking-tight">{t('Peta Sebaran Desa')}</CardTitle>
			<CardDescription>{t('Lokasi desa mitra di seluruh Indonesia, diambil dari data potensi desa.')}</CardDescription>
		</div>
		<div class="flex flex-col items-end gap-1">
			<span class="text-xs font-semibold text-muted-foreground">{villages.length} {t('desa mitra')}</span>
			{#if dataSource === 'fallback'}
				<span class="text-[11px] font-medium text-amber-600 dark:text-amber-400">{t('Menampilkan data contoh (API desa tidak terjangkau).')}</span>
			{/if}
		</div>
	</CardHeader>
	<CardContent class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(280px,350px)]">
		<!-- Interactive Map with Leaflet -->
		<div class="rounded-lg overflow-hidden shadow-md ring-1 ring-gray-200 dark:ring-gray-700" style="height: 400px; position: relative;">
			<div bind:this={mapContainer} id="village-map-container" class="w-full h-full"></div>
			
			{#if isLoading && !import.meta.env.SSR}
				<div class="absolute inset-0 flex items-center justify-center bg-muted" role="status" aria-live="polite">
					<p class="text-sm text-muted-foreground">{t('Memuat peta...')}</p>
				</div>
			{/if}
		</div>

		<!-- Village List -->
		<div class="flex flex-col gap-2">
			<h3 class="text-sm font-bold">{t('Daftar Desa Mitra')}</h3>
			{#each villages as village (village.id)}
				<button
					type="button"
					class="flex items-center justify-between gap-2 rounded-lg border bg-muted/20 px-3 py-2.5 text-left text-sm transition-colors hover:border-ring/40 hover:bg-muted/40 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
					disabled={isLoading}
					onclick={() => {
						if (isLoading) return;
						const idx = villages.findIndex(v => v.id === village.id);
						if (idx !== -1 && markers[idx]) {
							mapInstance?.flyTo([village.lat, village.lng], 7);
							markers[idx].openPopup();
						}
					}}
					title={`${t('Lihat di peta:')} ${village.name}`}
					aria-label={`${t('Lihat di peta:')} ${village.name}`}
				>
					<div class="min-w-0 flex-1">
						<span class="truncate font-medium">{village.name}</span>
						<p class="text-xs text-muted-foreground truncate">{village.region}</p>
					</div>
					<span class="shrink-0 rounded-full px-2 py-0.5 text-xs font-bold bg-muted text-muted-foreground">
						{village.readiness}%
					</span>
				</button>
			{:else}
				{#if isLoading}
					<p class="text-sm text-muted-foreground">{t('Memuat data desa...')}</p>
				{:else}
					<p class="text-sm text-muted-foreground">{t('Belum ada desa dengan koordinat peta.')}</p>
				{/if}
			{/each}

			<p class="mt-2 text-xs leading-snug text-muted-foreground">
				{t('Klik nama desa untuk zoom ke lokasi di peta, atau klik pin untuk detail.')}
			</p>
		</div>
	</CardContent>
</Card>

<style>
	/* Custom marker styles */
	:global(.village-marker .marker-inner) {
		animation: village-pulse 2s ease-in-out infinite;
		pointer-events: auto;
		cursor: pointer;
	}

	@keyframes village-pulse {
		0%, 100% { 
			transform: scale(1);
			box-shadow: 0 2px 5px rgba(0,0,0,0.3);
		}
		50% { 
			transform: scale(1.15);
			box-shadow: 0 4px 12px rgba(30, 99, 189, 0.4);
		}
	}

	:global(.leaflet-popup-content-wrapper) {
		border-radius: 0.5rem;
		padding: 0.5rem;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
	}

	:global(.leaflet-container) {
		background: #f8fafc;
		z-index: 0;
	}

	#village-map-container {
		width: 100%;
		height: 100%;
		min-height: 300px;
	}

	/* Loading state styling */
	.absolute.inset-0.flex {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		align-items: center;
		justify-content: center;
		background-color: rgb(243 244 246 / 0.8);
		backdrop-filter: blur(4px);
	}
</style>
