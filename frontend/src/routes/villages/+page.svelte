<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect, NativeSelectOption } from '$lib/components/ui/native-select/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import {
		listVillages,
		createVillage,
		updateVillage,
		deleteVillage,
		type Village
	} from '$lib/api/villages';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';

	import MapPinIcon from '@lucide/svelte/icons/map-pin';
	import PlusIcon from '@lucide/svelte/icons/plus';
	import PencilIcon from '@lucide/svelte/icons/pencil';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import SearchIcon from '@lucide/svelte/icons/search';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';
	import AlertCircleIcon from '@lucide/svelte/icons/alert-circle';
	import XIcon from '@lucide/svelte/icons/x';
	import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
	import PackageIcon from '@lucide/svelte/icons/package';

	// Initial seed fallback if backend is offline during hydration
	const seedVillages: Village[] = [
		{
			id: 'DES-GAYO',
			name: 'Desa Kopi Gayo',
			region: 'Lut Tawar, Aceh Tengah',
			province: 'Aceh',
			flagshipCommodity: 'Kopi Arabika Gayo',
			commodityGroup: 'pertanian',
			production: '8 ton green beans / bulan',
			organization: 'BUMDes Kopi Gayo Sejahtera',
			readiness: 86,
			status: 'Siap Ekspor'
		},
		{
			id: 'DES-VANILI-BALI',
			name: 'Desa Vanili Bali',
			region: 'Tabanan',
			province: 'Bali',
			flagshipCommodity: 'Vanili Planifolia',
			commodityGroup: 'pertanian',
			production: '50 kg curing / bulan',
			organization: 'Koperasi Vanili Bali Sejahtera',
			readiness: 77,
			status: 'Butuh Pendampingan'
		},
		{
			id: 'DES-SITUBONDO',
			name: 'Desa Manggis Situbondo',
			region: 'Banyuputih, Situbondo',
			province: 'Jawa Timur',
			flagshipCommodity: 'Manggis Premium',
			commodityGroup: 'pertanian',
			production: '600 kg / musim panen',
			organization: 'Gapoktan Manggis Lestari',
			readiness: 68,
			status: 'Butuh Pendampingan'
		},
		{
			id: 'DES-TORAJA',
			name: 'Desa Kakao Toraja',
			region: 'Rantepao, Toraja Utara',
			province: 'Sulawesi Selatan',
			flagshipCommodity: 'Kakao Fermentasi',
			commodityGroup: 'pertanian',
			production: '3 ton / bulan',
			organization: 'Koperasi Desa Kakao Toraja',
			readiness: 81,
			status: 'Siap Ekspor'
		}
	];

	let villages = createRemoteList(listVillages, seedVillages);
	$effect(() => {
		villages.load();
	});

	let query = $state('');
	let selectedReadiness = $state('All');
	let selectedProvince = $state('All');
	let selectedGroup = $state('All');
	let error = $state('');
	let successMessage = $state('');
	let actionLoading = $state(false);

	// Dialog states
	let formOpen = $state(false);
	let isEdit = $state(false);
	let editingId = $state('');
	let fName = $state('');
	let fRegion = $state('');
	let fProvince = $state('Aceh');
	let fFlagshipCommodity = $state('');
	let fCommodityGroup = $state<'pertanian' | 'perikanan' | 'kerajinan'>('pertanian');
	let fProduction = $state('');
	let fOrganization = $state('');
	let fReadiness = $state(75);

	let deleteOpen = $state(false);
	let deleteTarget = $state<Village | null>(null);

	// Derived metrics
	let totalVillages = $derived(villages.items.length);
	let readyCount = $derived(villages.items.filter((v) => (v.readiness ?? 0) >= 80).length);
	let assistanceCount = $derived(villages.items.filter((v) => (v.readiness ?? 0) < 80).length);
	let uniqueCommodities = $derived(new Set(villages.items.map((v) => v.flagshipCommodity)).size);

	// Distinct provinces
	let provinces = $derived(['All', ...Array.from(new Set(villages.items.map((v) => v.province).filter(Boolean)))]);

	// Filtered list
	let filteredVillages = $derived(
		villages.items.filter((v) => {
			const matchesReadiness =
				selectedReadiness === 'All' ||
				(selectedReadiness === 'Siap Ekspor' && (v.readiness ?? 0) >= 80) ||
				(selectedReadiness === 'Butuh Pendampingan' && (v.readiness ?? 0) < 80);

			const matchesProvince = selectedProvince === 'All' || v.province === selectedProvince;
			const matchesGroup = selectedGroup === 'All' || v.commodityGroup === selectedGroup;

			const q = query.trim().toLowerCase();
			const matchesQuery =
				!q ||
				[v.name, v.region, v.province, v.flagshipCommodity, v.organization, v.production]
					.join(' ')
					.toLowerCase()
					.includes(q);

			return matchesReadiness && matchesProvince && matchesGroup && matchesQuery;
		})
	);

	function openCreate() {
		isEdit = false;
		editingId = '';
		fName = '';
		fRegion = '';
		fProvince = 'Aceh';
		fFlagshipCommodity = '';
		fCommodityGroup = 'pertanian';
		fProduction = '';
		fOrganization = '';
		fReadiness = 75;
		error = '';
		formOpen = true;
	}

	function openEdit(v: Village) {
		isEdit = true;
		editingId = v.id;
		fName = v.name;
		fRegion = v.region;
		fProvince = v.province;
		fFlagshipCommodity = v.flagshipCommodity;
		fCommodityGroup = (v.commodityGroup as 'pertanian' | 'perikanan' | 'kerajinan') || 'pertanian';
		fProduction = v.production;
		fOrganization = v.organization;
		fReadiness = v.readiness ?? 75;
		error = '';
		formOpen = true;
	}

	async function handleSave() {
		if (!fName.trim() || !fFlagshipCommodity.trim() || !fOrganization.trim()) {
			error = t('Nama desa, komoditas utama, dan nama pengelola wajib diisi.');
			return;
		}
		error = '';
		actionLoading = true;
		try {
			const payload: Partial<Village> = {
				name: fName.trim(),
				region: fRegion.trim(),
				province: fProvince.trim(),
				flagshipCommodity: fFlagshipCommodity.trim(),
				commodityGroup: fCommodityGroup,
				production: fProduction.trim(),
				organization: fOrganization.trim(),
				readiness: Number(fReadiness)
			};

			if (isEdit && editingId) {
				await updateVillage(editingId, payload);
			} else {
				await createVillage(payload);
			}

			await villages.load();
			formOpen = false;
			successMessage = t('Desa berhasil disimpan.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
		} catch {
			error = t('Gagal menyimpan data desa.');
		} finally {
			actionLoading = false;
		}
	}

	function openDelete(v: Village) {
		deleteTarget = v;
		deleteOpen = true;
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		actionLoading = true;
		error = '';
		try {
			await deleteVillage(deleteTarget.id);
			await villages.load();
			deleteOpen = false;
			deleteTarget = null;
			successMessage = t('Desa berhasil dihapus.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
		} catch {
			error = t('Gagal menghapus desa.');
		} finally {
			actionLoading = false;
		}
	}

	let paginationPage = $state(1);
	let paginationPageSize = $state(6);
	let pagedItems = $derived(paginate(filteredVillages ?? [], paginationPage, paginationPageSize));
	let paginationTotalPages = $derived(calcTotalPages(filteredVillages?.length ?? 0, paginationPageSize));
</script>

<svelte:head>
	<title>{t('Potensi & Komoditas Desa')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Potensi & Komoditas Desa')} eyebrow={t('Kurasi komoditas unggulan desa Indonesia yang siap memasuki rantai pasok ekspor global.')}>
	<!-- Hero / KPI Header -->
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<div class="flex items-center gap-2">
				<Badge>{t('Peta Potensi Desa')}</Badge>
				<Badge variant="outline" class="text-xs">{t('Desa Siap Ekspor')}: {readyCount}</Badge>
			</div>
			<CardTitle class="mt-3 font-display text-3xl font-black tracking-tight text-[#0b1d3a] md:text-4xl dark:text-white">
				{t('Rantai Pasok Komoditas Unggulan Desa ke Pasar Global.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Membantu petani, BUMDes, dan pengrajin desa menembus pasar internasional melalui pendampingan standarisasi, pemetaan potensi, dan kurasi komoditas berkualitas tinggi.')}
			</CardDescription>
		</CardHeader>

		<div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
			<div class="rounded-lg border bg-card/60 p-3">
				<span class="text-xs font-semibold text-muted-foreground">{t('Total Desa Binaan')}</span>
				<p class="mt-1 text-2xl font-bold text-foreground">{totalVillages}</p>
			</div>
			<div class="rounded-lg border bg-card/60 p-3">
				<span class="text-xs font-semibold text-muted-foreground">{t('Desa Siap Ekspor')}</span>
				<p class="mt-1 text-2xl font-bold text-emerald-700 dark:text-emerald-400">{readyCount}</p>
			</div>
			<div class="rounded-lg border bg-card/60 p-3">
				<span class="text-xs font-semibold text-muted-foreground">{t('Butuh Pendampingan')}</span>
				<p class="mt-1 text-2xl font-bold text-amber-700 dark:text-amber-400">{assistanceCount}</p>
			</div>
			<div class="rounded-lg border bg-card/60 p-3">
				<span class="text-xs font-semibold text-muted-foreground">{t('Komoditas Unggulan')}</span>
				<p class="mt-1 text-2xl font-bold text-foreground">{uniqueCommodities}</p>
			</div>
		</div>

		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<Button onclick={openCreate}>
				<PlusIcon class="size-4" />
				<span class="ms-1.5">{t('Tambah Desa Binaan')}</span>
			</Button>
			<Button variant="outline" onclick={() => villages.load()}>
				<RefreshCwIcon class="size-4 {villages.loading ? 'animate-spin' : ''}" />
				<span class="ms-1.5">{t('Segarkan Data')}</span>
			</Button>
			<Button variant="outline" href="/products">
				<PackageIcon class="size-4" />
				<span class="ms-1.5">{t('Kembali ke produk')}</span>
			</Button>
		</CardContent>
	</Card>

	<!-- Feedback Alerts -->
	{#if error}
		<div class="flex items-center justify-between rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-semibold text-destructive">
			<div class="flex items-center gap-2">
				<AlertCircleIcon class="size-4" />
				<span>{error}</span>
			</div>
			<button onclick={() => (error = '')}><XIcon class="size-4" /></button>
		</div>
	{/if}

	{#if successMessage}
		<div class="flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
			<div class="flex items-center gap-2">
				<CheckCircle2Icon class="size-4" />
				<span>{successMessage}</span>
			</div>
			<button onclick={() => (successMessage = '')}><XIcon class="size-4" /></button>
		</div>
	{/if}

	<!-- Filter Controls -->
	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap items-center gap-2">
			<div class="flex rounded-lg border bg-muted/20 p-1 text-xs font-semibold">
				<button
					onclick={() => (selectedReadiness = 'All')}
					class="rounded-md px-3 py-1 transition-colors {selectedReadiness === 'All' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}"
				>
					{t('Semua')}
				</button>
				<button
					onclick={() => (selectedReadiness = 'Siap Ekspor')}
					class="rounded-md px-3 py-1 transition-colors {selectedReadiness === 'Siap Ekspor' ? 'bg-emerald-600 text-white shadow-sm' : 'text-muted-foreground hover:text-foreground'}"
				>
					{t('Siap Ekspor')}
				</button>
				<button
					onclick={() => (selectedReadiness = 'Butuh Pendampingan')}
					class="rounded-md px-3 py-1 transition-colors {selectedReadiness === 'Butuh Pendampingan' ? 'bg-amber-600 text-white shadow-sm' : 'text-muted-foreground hover:text-foreground'}"
				>
					{t('Butuh Pendampingan')}
				</button>
			</div>

			<NativeSelect
				bind:value={selectedProvince}
				class="h-8 text-xs font-semibold"
			>
				<NativeSelectOption value="All">{t('Semua Provinsi')}</NativeSelectOption>
				{#each provinces.filter((p) => p !== 'All') as prov}
					<NativeSelectOption value={prov}>{prov}</NativeSelectOption>
				{/each}
			</NativeSelect>

			<NativeSelect
				bind:value={selectedGroup}
				class="h-8 text-xs font-semibold"
			>
				<NativeSelectOption value="All">{t('Kelompok Komoditas')}: {t('Semua')}</NativeSelectOption>
				<NativeSelectOption value="pertanian">{t('Pertanian & Perkebunan')}</NativeSelectOption>
				<NativeSelectOption value="perikanan">{t('Perikanan & Kelautan')}</NativeSelectOption>
				<NativeSelectOption value="kerajinan">{t('Kerajinan & Kriya')}</NativeSelectOption>
			</NativeSelect>
		</div>

		<div class="flex items-center gap-1.5 rounded-md border bg-muted/20 px-2 py-1">
			<SearchIcon class="size-3.5 text-muted-foreground" />
			<input
				type="text"
				placeholder={t('Cari nama desa, komoditas, atau BUMDes...')}
				bind:value={query}
				class="w-48 bg-transparent text-xs outline-none sm:w-64"
			/>
			{#if query}
				<button onclick={() => (query = '')} class="text-muted-foreground hover:text-foreground">
					<XIcon class="size-3" />
				</button>
			{/if}
		</div>
	</div>

	<!-- Village Cards Grid -->
	{#if villages.loading}
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
			{#each [1, 2, 3, 4, 5, 6] as _}
				<Card class="p-5">
					<Skeleton class="h-6 w-3/4" />
					<Skeleton class="mt-2 h-4 w-1/2" />
					<Skeleton class="mt-4 h-2 w-full" />
					<Skeleton class="mt-4 h-16 w-full" />
				</Card>
			{/each}
		</div>
	{:else if filteredVillages.length === 0}
		<div class="rounded-xl border border-dashed p-12 text-center">
			<MapPinIcon class="mx-auto size-8 text-muted-foreground/50" />
			<p class="mt-2 text-sm font-semibold text-foreground">{t('Tidak ada data desa yang cocok dengan kriteria pencarian.')}</p>
			<Button size="sm" class="mt-4" onclick={openCreate}>
				<PlusIcon class="size-3.5" />
				<span class="ms-1.5">{t('Tambah Desa Baru')}</span>
			</Button>
		</div>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
			{#each pagedItems as village (village.id)}
				{@const isReady = (village.readiness ?? 0) >= 80}
				<Card class="flex flex-col justify-between transition-shadow hover:shadow-md">
					<CardContent class="p-5">
						<div class="flex items-start justify-between gap-3">
							<div>
								<div class="flex items-center gap-2">
									<Badge variant={isReady ? 'default' : 'secondary'} class="text-xs">
										{isReady ? t('Siap Ekspor') : t('Butuh Pendampingan')}
									</Badge>
									<Badge variant="outline" class="text-[10px] uppercase">
										{village.commodityGroup}
									</Badge>
								</div>
								<h3 class="mt-2 text-lg font-bold tracking-tight text-foreground">{village.name}</h3>
								<p class="flex items-center gap-1 text-xs text-muted-foreground">
									<MapPinIcon class="size-3 shrink-0" />
									<span>{village.region}, {village.province}</span>
								</p>
							</div>
							<div class="text-right">
								<span class="text-2xl font-black {isReady ? 'text-emerald-700 dark:text-emerald-400' : 'text-amber-700 dark:text-amber-400'}">
									{village.readiness}%
								</span>
								<span class="block text-[10px] text-muted-foreground uppercase">{t('Skor Kesiapan Ekspor')}</span>
							</div>
						</div>

						<div class="mt-3">
							<Progress value={village.readiness ?? 0} class="h-2" />
						</div>

						<div class="mt-4 space-y-2 rounded-lg border bg-muted/20 p-3 text-xs">
							<div class="flex items-center justify-between">
								<span class="text-muted-foreground">{t('Komoditas Utama')}:</span>
								<strong class="font-semibold text-foreground">{village.flagshipCommodity}</strong>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-muted-foreground">{t('Kapasitas Produksi')}:</span>
								<span class="font-medium text-foreground">{village.production}</span>
							</div>
							<div class="flex items-center justify-between border-t pt-1.5">
								<span class="text-muted-foreground">{t('Pengelola')}:</span>
								<span class="font-medium text-foreground">{village.organization}</span>
							</div>
						</div>
					</CardContent>

					<div class="flex items-center justify-between border-t bg-muted/10 px-5 py-3 text-xs">
						<Button size="sm" variant="ghost" class="h-7 text-xs" href={`/products?query=${encodeURIComponent(village.flagshipCommodity)}`}>
							<span>{t('Lihat Produk Terkait')}</span>
							<ArrowRightIcon class="ms-1 size-3" />
						</Button>
						<div class="flex items-center gap-1">
							<button
								onclick={() => openEdit(village)}
								class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
								title={t('Edit Desa')}
							>
								<PencilIcon class="size-3.5" />
							</button>
							<button
								onclick={() => openDelete(village)}
								class="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
								title={t('Hapus Desa')}
							>
								<Trash2Icon class="size-3.5" />
							</button>
						</div>
					</div>
				</Card>
			{/each}
		</div>
	{/if}

	<Pagination bind:page={paginationPage} bind:pageSize={paginationPageSize} totalPages={paginationTotalPages} totalItems={filteredVillages?.length ?? 0} />
</AppShell>

<!-- CREATE / EDIT VILLAGE DIALOG -->
{#if formOpen}
	<Dialog.Root bind:open={formOpen}>
		<Dialog.Content class="sm:max-w-lg">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base font-bold">
					<MapPinIcon class="size-5 text-primary" />
					<span>{isEdit ? t('Edit Data Desa') : t('Tambah Desa Baru')}</span>
				</Dialog.Title>
				<Dialog.Description class="text-xs">
					{t('Kurasi komoditas unggulan desa Indonesia yang siap memasuki rantai pasok ekspor global.')}
				</Dialog.Description>
			</Dialog.Header>

			<div class="grid gap-3 py-2 text-xs">
				<div>
					<label for="village-name" class="mb-1 block font-semibold text-foreground">{t('Nama Desa')}</label>
					<Input id="village-name" bind:value={fName} placeholder="Contoh: Desa Kopi Gayo" class="text-xs" />
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="village-region" class="mb-1 block font-semibold text-foreground">{t('Wilayah / Kecamatan')}</label>
						<Input id="village-region" bind:value={fRegion} placeholder="Contoh: Lut Tawar, Aceh Tengah" class="text-xs" />
					</div>
					<div>
						<label for="village-province" class="mb-1 block font-semibold text-foreground">{t('Provinsi')}</label>
						<Input id="village-province" bind:value={fProvince} placeholder="Contoh: Aceh" class="text-xs" />
					</div>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="village-commodity" class="mb-1 block font-semibold text-foreground">{t('Komoditas Utama')}</label>
						<Input id="village-commodity" bind:value={fFlagshipCommodity} placeholder="Contoh: Kopi Arabika" class="text-xs" />
					</div>
					<div>
						<label for="village-group" class="mb-1 block font-semibold text-foreground">{t('Kelompok Komoditas')}</label>
						<NativeSelect id="village-group" bind:value={fCommodityGroup} class="h-8 text-xs">
							<NativeSelectOption value="pertanian">{t('Pertanian & Perkebunan')}</NativeSelectOption>
							<NativeSelectOption value="perikanan">{t('Perikanan & Kelautan')}</NativeSelectOption>
							<NativeSelectOption value="kerajinan">{t('Kerajinan & Kriya')}</NativeSelectOption>
						</NativeSelect>
					</div>
				</div>

				<div>
					<label for="village-production" class="mb-1 block font-semibold text-foreground">{t('Kapasitas per Bulan/Musim')}</label>
					<Input id="village-production" bind:value={fProduction} placeholder="Contoh: 8 ton green beans / bulan" class="text-xs" />
				</div>

				<div>
					<label for="village-organization" class="mb-1 block font-semibold text-foreground">{t('Nama BUMDes / Koperasi / Gapoktan')}</label>
					<Input id="village-organization" bind:value={fOrganization} placeholder="Contoh: BUMDes Kopi Gayo Sejahtera" class="text-xs" />
				</div>

				<div>
					<label for="village-readiness" class="mb-1 block font-semibold text-foreground">{t('Nilai Kesiapan Ekspor (0-100)')}</label>
					<Input id="village-readiness" type="number" min="0" max="100" bind:value={fReadiness} class="text-xs" />
				</div>
			</div>

			<Dialog.Footer>
				<Button variant="outline" onclick={() => (formOpen = false)} disabled={actionLoading}>
					{t('Batal')}
				</Button>
				<Button onclick={handleSave} disabled={actionLoading}>
					{#if actionLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menyimpan...')}</span>
					{:else}
						{t('Simpan')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- DELETE VILLAGE DIALOG -->
{#if deleteOpen && deleteTarget}
	<Dialog.Root bind:open={deleteOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base text-destructive">
					<Trash2Icon class="size-4" />
					<span>{t('Hapus Desa')}</span>
				</Dialog.Title>
				<Dialog.Description class="text-xs">
					{t('Apakah Anda yakin ingin menghapus data desa ini?')}
					<div class="my-2 rounded bg-muted p-2 font-mono text-xs">
						{deleteTarget.name} ({deleteTarget.region})
					</div>
					<span class="text-destructive font-semibold">{t('Tindakan ini tidak dapat dibatalkan.')}</span>
				</Dialog.Description>
			</Dialog.Header>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (deleteOpen = false)} disabled={actionLoading}>
					{t('Batal')}
				</Button>
				<Button variant="destructive" onclick={confirmDelete} disabled={actionLoading}>
					{#if actionLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menghapus...')}</span>
					{:else}
						{t('Hapus')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}
