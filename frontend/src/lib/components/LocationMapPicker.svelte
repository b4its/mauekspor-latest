<script lang="ts">
	/**
	 * Pemilih lokasi berbasis peta asli (Leaflet + OpenStreetMap).
	 *
	 * Pengguna cukup mengklik titik di peta (atau menggeser pin, atau mencari
	 * tempat), lalu `latitude` & `longitude` tergenerate otomatis. Alamat, jalan,
	 * kota, provinsi, dan negara juga terisi otomatis lewat reverse geocoding
	 * (Nominatim/OSM) sesuai titik yang dipilih.
	 *
	 * Komponen ini client-only (dynamic import Leaflet) sehingga aman untuk SSR.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { t } from '$lib/i18n.svelte';
	import { reverseGeocode, searchPlaces, type PlaceInfo, type PlaceSuggestion } from '$lib/utils/geocode';

	import 'leaflet/dist/leaflet.css';
	import MapPinIcon from '@lucide/svelte/icons/map-pin';
	import LocateFixedIcon from '@lucide/svelte/icons/locate-fixed';
	import SearchIcon from '@lucide/svelte/icons/search';
	import LoaderCircleIcon from '@lucide/svelte/icons/loader-circle';

	let {
		latitude = $bindable<number | null>(null),
		longitude = $bindable<number | null>(null),
		address = $bindable(''),
		place = $bindable<PlaceInfo | null>(null),
		height = '320px',
		/** Koordinat awal saat belum ada nilai (default: tengah Indonesia). */
		defaultCenter = [-2.5489, 118.0149] as [number, number],
		defaultZoom = 5,
		showSearch = true,
		labelledby = undefined
	}: {
		latitude?: number | null;
		longitude?: number | null;
		address?: string;
		place?: PlaceInfo | null;
		height?: string;
		defaultCenter?: [number, number];
		defaultZoom?: number;
		showSearch?: boolean;
		labelledby?: string;
	} = $props();

	let mapContainer: HTMLDivElement | null = null;
	let mapInstance: any = null;
	let marker: any = null;
	let LRef: any = null;

	let resolving = $state(false);
	let locating = $state(false);
	let geocodeError = $state('');

	// Pencarian tempat
	let query = $state('');
	let suggestions = $state<PlaceSuggestion[]>([]);
	let searching = $state(false);
	let showSuggestions = $state(false);
	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	let reverseAbort: AbortController | null = null;

	const pinIcon = (L: any) =>
		L.divIcon({
			className: 'location-picker-marker',
			html: '<div style="background: linear-gradient(135deg,#1e63d6,#1e40af);width:20px;height:20px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid white;box-shadow:0 3px 8px rgba(0,0,0,.4)"></div>',
			iconSize: [24, 24],
			iconAnchor: [12, 24],
			popupAnchor: [0, -20]
		});

	function syncMarker(lat: number, lng: number) {
		if (!mapInstance || !LRef) return;
		if (marker) {
			marker.setLatLng([lat, lng]);
		} else {
			marker = LRef.marker([lat, lng], { icon: pinIcon(LRef), draggable: true }).addTo(mapInstance);
			marker.on('dragend', () => {
				const p = marker.getLatLng();
				void pickPoint(p.lat, p.lng, false);
			});
		}
	}

	/** Tetapkan titik terpilih + resolve alamat. `recenter` menggeser peta. */
	async function pickPoint(lat: number, lng: number, recenter = true) {
		latitude = lat;
		longitude = lng;
		if (mapInstance) {
			syncMarker(lat, lng);
			if (recenter) mapInstance.panTo([lat, lng]);
		}
		await resolveAddress(lat, lng);
	}

	async function resolveAddress(lat: number, lng: number) {
		geocodeError = '';
		resolving = true;
		reverseAbort?.abort();
		reverseAbort = new AbortController();
		try {
			const info = await reverseGeocode(lat, lng, reverseAbort.signal);
			if (info) {
				place = info;
				address = info.displayName;
			} else {
				geocodeError = t('Alamat tidak dapat ditemukan otomatis. Isi manual bila perlu.');
			}
		} finally {
			resolving = false;
		}
	}

	function onMapClick(e: any) {
		void pickPoint(e.latlng.lat, e.latlng.lng, false);
	}

	async function useMyLocation() {
		if (typeof navigator === 'undefined' || !navigator.geolocation) {
			geocodeError = t('Perangkat tidak mendukung lokasi otomatis.');
			return;
		}
		locating = true;
		geocodeError = '';
		navigator.geolocation.getCurrentPosition(
			async (pos) => {
				const { latitude: la, longitude: lo } = pos.coords;
				mapInstance?.setView([la, lo], 14);
				await pickPoint(la, lo, false);
				locating = false;
			},
			() => {
				geocodeError = t('Tidak dapat mengakses lokasi Anda.');
				locating = false;
			},
			{ enableHighAccuracy: true, timeout: 10000 }
		);
	}

	function onSearchInput() {
		clearTimeout(searchTimer);
		const q = query;
		if (q.trim().length < 3) {
			suggestions = [];
			return;
		}
		searchTimer = setTimeout(async () => {
			searching = true;
			suggestions = await searchPlaces(q);
			showSuggestions = true;
			searching = false;
		}, 350);
	}

	async function chooseSuggestion(s: PlaceSuggestion) {
		showSuggestions = false;
		query = s.label;
		mapInstance?.setView([s.lat, s.lng], 13);
		await pickPoint(s.lat, s.lng, false);
	}

	onMount(async () => {
		if (import.meta.env.SSR || !mapContainer) return;
		try {
			const L = await import('leaflet');
			LRef = L;
			const hasPoint = Number.isFinite(latitude) && Number.isFinite(longitude);
			const center: [number, number] = hasPoint ? [latitude as number, longitude as number] : defaultCenter;
			mapInstance = L.map(mapContainer).setView(center, hasPoint ? 12 : defaultZoom);
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				maxZoom: 19,
				attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				subdomains: 'abc'
			}).addTo(mapInstance);
			mapInstance.on('click', onMapClick);
			if (hasPoint) syncMarker(latitude as number, longitude as number);
			// Pastikan ukuran benar setelah container tampil.
			setTimeout(() => mapInstance?.invalidateSize(), 120);
		} catch {
			geocodeError = t('Peta gagal dimuat.');
		}
	});

	onDestroy(() => {
		clearTimeout(searchTimer);
		reverseAbort?.abort();
		if (mapInstance) {
			mapInstance.off();
			mapInstance.remove();
			mapInstance = null;
		}
		marker = null;
	});
</script>

<div class="grid gap-2">
	{#if showSearch}
		<div class="relative">
			<div class="flex items-center gap-2 rounded-md border bg-background px-3 py-2">
				<SearchIcon class="size-4 shrink-0 text-muted-foreground" />
				<input
					type="text"
					bind:value={query}
					oninput={onSearchInput}
					onfocus={() => (showSuggestions = suggestions.length > 0)}
					placeholder={t('Cari tempat, jalan, atau kota...')}
					aria-label={t('Cari tempat')}
					class="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
				/>
				{#if searching}
					<LoaderCircleIcon class="size-4 shrink-0 animate-spin text-muted-foreground" />
				{/if}
			</div>
			{#if showSuggestions && suggestions.length > 0}
				<ul class="absolute inset-x-0 top-full z-[1000] mt-1 max-h-56 overflow-y-auto rounded-lg border bg-background shadow-xl">
					{#each suggestions as s}
						<li>
							<button
								type="button"
								class="w-full px-3 py-2 text-left text-sm hover:bg-accent"
								onclick={() => chooseSuggestion(s)}
							>
								<span class="block truncate font-medium">{s.label}</span>
								<span class="block truncate text-xs text-muted-foreground">{s.displayName}</span>
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}

	<div class="relative overflow-hidden rounded-lg border shadow-sm ring-1 ring-gray-200 dark:ring-gray-700" style={`height:${height}`}>
		<div bind:this={mapContainer} class="size-full" aria-label={labelledby ? undefined : t('Peta pemilih lokasi')}></div>
		{#if resolving}
			<div class="pointer-events-none absolute inset-x-0 bottom-0 flex items-center gap-2 bg-background/85 px-3 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur">
				<LoaderCircleIcon class="size-3.5 animate-spin" />
				{t('Mendeteksi alamat dari titik...')}
			</div>
		{/if}
	</div>

	<div class="flex flex-wrap items-center gap-2">
		<Button type="button" variant="outline" size="sm" onclick={useMyLocation} disabled={locating}>
			{#if locating}
				<LoaderCircleIcon class="size-3.5 animate-spin" />
			{:else}
				<LocateFixedIcon class="size-3.5" />
			{/if}
			<span class="ms-1.5">{t('Gunakan lokasi saya')}</span>
		</Button>
		<span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
			<MapPinIcon class="size-3.5" />
			{#if Number.isFinite(latitude) && Number.isFinite(longitude)}
				{latitude?.toFixed(5)}, {longitude?.toFixed(5)}
			{:else}
				{t('Klik peta untuk memilih titik.')}
			{/if}
		</span>
	</div>

	{#if geocodeError}
		<p class="text-xs font-medium text-orange-600 dark:text-orange-400">{geocodeError}</p>
	{/if}

	<div class="grid gap-2 sm:grid-cols-2">
		<div class="grid gap-1.5">
			<label for="loc-lat" class="text-xs font-semibold text-muted-foreground">{t('Latitude')}</label>
			<Input
				id="loc-lat"
				type="number"
				step="0.00001"
				min="-90"
				max="90"
				value={latitude ?? ''}
				oninput={(e) => {
					const v = (e.currentTarget as HTMLInputElement).valueAsNumber;
					latitude = Number.isFinite(v) ? v : null;
				}}
				onchange={() => {
					if (Number.isFinite(latitude) && Number.isFinite(longitude)) pickPoint(latitude as number, longitude as number);
				}}
			/>
		</div>
		<div class="grid gap-1.5">
			<label for="loc-lng" class="text-xs font-semibold text-muted-foreground">{t('Longitude')}</label>
			<Input
				id="loc-lng"
				type="number"
				step="0.00001"
				min="-180"
				max="180"
				value={longitude ?? ''}
				oninput={(e) => {
					const v = (e.currentTarget as HTMLInputElement).valueAsNumber;
					longitude = Number.isFinite(v) ? v : null;
				}}
				onchange={() => {
					if (Number.isFinite(latitude) && Number.isFinite(longitude)) pickPoint(latitude as number, longitude as number);
				}}
			/>
		</div>
	</div>
</div>

<style>
	:global(.location-picker-marker) {
		background: transparent;
		border: none;
	}
	:global(.leaflet-container) {
		background: #f8fafc;
		z-index: 0;
	}
</style>
