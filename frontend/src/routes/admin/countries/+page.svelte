<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import AdminSidebar from '$lib/components/AdminSidebar.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Pagination from '$lib/components/Pagination.svelte';
	import { paginate, calcTotalPages } from '$lib/utils/pagination';
	import {
		listAdminCountries,
		createAdminCountry,
		updateAdminCountry,
		deleteAdminCountry,
		listAdminRegulations,
		createAdminRegulation,
		updateAdminRegulation,
		deleteAdminRegulation,
		importAdminRegulations,
		type AdminCountry,
		type AdminRegulation,
		type RegulationPayload
	} from '$lib/api/admin-countries';
	import { t } from '$lib/i18n.svelte';
	import { getStatus, getUser } from '$lib/stores/session.svelte';

	import GlobeIcon from '@lucide/svelte/icons/globe';
	import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
	import PlusIcon from '@lucide/svelte/icons/plus';
	import PencilIcon from '@lucide/svelte/icons/pencil';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import UploadIcon from '@lucide/svelte/icons/upload';
	import SearchIcon from '@lucide/svelte/icons/search';
	import ShieldAlertIcon from '@lucide/svelte/icons/shield-alert';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';
	import DownloadIcon from '@lucide/svelte/icons/download';
	import CopyIcon from '@lucide/svelte/icons/copy';
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';

	let isAdmin = $derived(getStatus() === 'authenticated' && getUser()?.role === 'Admin');

	// Countries list state
	let countries = $state<AdminCountry[]>([]);
	let countriesLoading = $state(true);
	let countrySearch = $state('');
	let selectedRegion = $state('');
	let activeCountryCode = $state('');
	let countryPage = $state(1);
	let countryPageSize = $state(20);

	// Regulations state
	let regulations = $state<AdminRegulation[]>([]);
	let regulationsLoading = $state(false);
	let selectedCategory = $state('');

	// Toast / message feedback
	let noticeMessage = $state('');
	let errorMessage = $state('');

	// Country modals
	let createCountryOpen = $state(false);
	let cCode = $state('');
	let cName = $state('');
	let cRegion = $state('Asia');
	let cSaving = $state(false);
	let cError = $state('');

	let editCountryOpen = $state(false);
	let editCountryTarget = $state<AdminCountry | null>(null);
	let eName = $state('');
	let eRegion = $state('Asia');
	let eSaving = $state(false);
	let eError = $state('');

	let deleteCountryOpen = $state(false);
	let deleteCountryTarget = $state<AdminCountry | null>(null);
	let deleteCountrySaving = $state(false);
	let deleteCountryError = $state('');

	// Regulation modals
	let createRegOpen = $state(false);
	let rCategory = $state('Labeling');
	let rForbidden = $state('');
	let rRequired = $state('');
	let rDescription = $state('');
	let rSaving = $state(false);
	let rError = $state('');

	let editRegOpen = $state(false);
	let editRegTarget = $state<AdminRegulation | null>(null);
	let erCategory = $state('Labeling');
	let erForbidden = $state('');
	let erRequired = $state('');
	let erDescription = $state('');
	let erSaving = $state(false);
	let erError = $state('');

	let deleteRegOpen = $state(false);
	let deleteRegTarget = $state<AdminRegulation | null>(null);
	let deleteRegSaving = $state(false);
	let deleteRegError = $state('');

	// CSV import modal
	let importCsvOpen = $state(false);
	let selectedCsvFile = $state<File | null>(null);
	let importing = $state(false);
	let importResult = $state('');
	let importError = $state('');

	const regions = ['Asia', 'Europe', 'Americas', 'Africa', 'Oceania', 'Antarctic'];
	const ruleCategories = ['Labeling', 'Customs', 'Sanitary', 'Packaging', 'Standards', 'Documentation', 'Tariff'];

	function flagEmoji(code: string) {
		if (!code || code.length !== 2) return '🌐';
		return String.fromCodePoint(...[...code.toUpperCase()].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65));
	}

	function showNotice(msg: string) {
		noticeMessage = msg;
		errorMessage = '';
		setTimeout(() => {
			if (noticeMessage === msg) noticeMessage = '';
		}, 4000);
	}

	function showError(msg: string) {
		errorMessage = msg;
		noticeMessage = '';
		setTimeout(() => {
			if (errorMessage === msg) errorMessage = '';
		}, 6000);
	}

	async function loadCountries() {
		countriesLoading = true;
		try {
			const res = await listAdminCountries();
			countries = res.data;
			if (!activeCountryCode && countries.length > 0) {
				const idCountry = countries.find((c) => c.country_code === 'ID');
				activeCountryCode = idCountry ? idCountry.country_code : countries[0].country_code;
			}
		} catch {
			showError(t('Gagal memuat data negara.'));
		} finally {
			countriesLoading = false;
		}
	}

	async function loadRegulations(code: string, category = '') {
		if (!code) return;
		regulationsLoading = true;
		try {
			const res = await listAdminRegulations(code, category);
			regulations = res.data;
		} catch {
			showError(t('Gagal memuat daftar regulasi.'));
			regulations = [];
		} finally {
			regulationsLoading = false;
		}
	}

	$effect(() => {
		loadCountries();
	});

	$effect(() => {
		if (activeCountryCode) {
			loadRegulations(activeCountryCode, selectedCategory);
		}
	});

	let filteredCountries = $derived.by(() => {
		let list = countries;
		if (selectedRegion) {
			list = list.filter((c) => (c.region || '').toLowerCase() === selectedRegion.toLowerCase());
		}
		if (countrySearch.trim()) {
			const q = countrySearch.trim().toLowerCase();
			list = list.filter((c) => c.country_code.toLowerCase().includes(q) || c.country_name.toLowerCase().includes(q));
		}
		return list;
	});

	let pagedCountries = $derived(paginate(filteredCountries, countryPage, countryPageSize));
	let totalCountryPages = $derived(calcTotalPages(filteredCountries.length, countryPageSize));

	let selectedCountry = $derived(countries.find((c) => c.country_code === activeCountryCode));

	// Stats
	let customCountriesCount = $derived(countries.filter((c) => c.id && c.id.startsWith('CTY-')).length);
	let uniqueRegions = $derived(new Set(countries.map((c) => c.region).filter(Boolean)).size);

	function selectCountry(code: string) {
		activeCountryCode = code;
		selectedCategory = '';
	}

	// Create country handlers
	function openCreateCountry() {
		cCode = '';
		cName = '';
		cRegion = 'Asia';
		cError = '';
		createCountryOpen = true;
	}

	async function handleCreateCountry() {
		cError = '';
		const code = cCode.trim().toUpperCase();
		const name = cName.trim();
		if (!code || code.length !== 2) {
			cError = t('Kode negara harus 2 huruf kapital (contoh: ID, JP, US).');
			return;
		}
		if (!name) {
			cError = t('Nama negara wajib diisi.');
			return;
		}
		cSaving = true;
		try {
			await createAdminCountry({ country_code: code, country_name: name, region: cRegion });
			createCountryOpen = false;
			showNotice(t('Berhasil menambahkan negara baru.'));
			await loadCountries();
			activeCountryCode = code;
		} catch (err: unknown) {
			cError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			cSaving = false;
		}
	}

	// Edit country handlers
	function openEditCountry(c: AdminCountry) {
		editCountryTarget = c;
		eName = c.country_name;
		eRegion = c.region || 'Asia';
		eError = '';
		editCountryOpen = true;
	}

	async function handleUpdateCountry() {
		if (!editCountryTarget) return;
		eError = '';
		const name = eName.trim();
		if (!name) {
			eError = t('Nama negara wajib diisi.');
			return;
		}
		eSaving = true;
		try {
			await updateAdminCountry(editCountryTarget.country_code, { country_name: name, region: eRegion });
			editCountryOpen = false;
			showNotice(t('Berhasil memperbarui data negara.'));
			await loadCountries();
		} catch (err: unknown) {
			eError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			eSaving = false;
		}
	}

	// Delete country handlers
	function openDeleteCountry(c: AdminCountry) {
		deleteCountryTarget = c;
		deleteCountryError = '';
		deleteCountryOpen = true;
	}

	async function handleDeleteCountry() {
		if (!deleteCountryTarget) return;
		deleteCountrySaving = true;
		deleteCountryError = '';
		try {
			await deleteAdminCountry(deleteCountryTarget.country_code);
			deleteCountryOpen = false;
			showNotice(t('Berhasil menghapus negara.'));
			if (activeCountryCode === deleteCountryTarget.country_code) {
				activeCountryCode = '';
			}
			await loadCountries();
		} catch (err: unknown) {
			deleteCountryError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			deleteCountrySaving = false;
		}
	}

	// Regulation handlers
	function openCreateRegulation() {
		rCategory = 'Labeling';
		rForbidden = '';
		rRequired = '';
		rDescription = '';
		rError = '';
		createRegOpen = true;
	}

	async function handleCreateRegulation() {
		if (!activeCountryCode) return;
		rError = '';
		if (!rDescription.trim()) {
			rError = t('Deskripsi aturan regulasi wajib diisi.');
			return;
		}
		rSaving = true;
		try {
			const payload: RegulationPayload = {
				rule_category: rCategory,
				forbidden_keywords: rForbidden.trim(),
				required_specs: rRequired.trim(),
				description_rule: rDescription.trim()
			};
			await createAdminRegulation(activeCountryCode, payload);
			createRegOpen = false;
			showNotice(t('Berhasil menambahkan regulasi.'));
			await loadRegulations(activeCountryCode, selectedCategory);
		} catch (err: unknown) {
			rError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			rSaving = false;
		}
	}

	function openEditRegulation(reg: AdminRegulation) {
		editRegTarget = reg;
		erCategory = reg.rule_category;
		erForbidden = reg.forbidden_keywords;
		erRequired = reg.required_specs;
		erDescription = reg.description_rule;
		erError = '';
		editRegOpen = true;
	}

	async function handleUpdateRegulation() {
		if (!editRegTarget) return;
		erError = '';
		if (!erDescription.trim()) {
			erError = t('Deskripsi aturan regulasi wajib diisi.');
			return;
		}
		erSaving = true;
		try {
			const payload: RegulationPayload = {
				rule_category: erCategory,
				forbidden_keywords: erForbidden.trim(),
				required_specs: erRequired.trim(),
				description_rule: erDescription.trim()
			};
			await updateAdminRegulation(editRegTarget.id, payload);
			editRegOpen = false;
			showNotice(t('Berhasil memperbarui regulasi.'));
			await loadRegulations(activeCountryCode, selectedCategory);
		} catch (err: unknown) {
			erError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			erSaving = false;
		}
	}

	function openDeleteRegulation(reg: AdminRegulation) {
		deleteRegTarget = reg;
		deleteRegError = '';
		deleteRegOpen = true;
	}

	async function handleDeleteRegulation() {
		if (!deleteRegTarget) return;
		deleteRegSaving = true;
		deleteRegError = '';
		try {
			await deleteAdminRegulation(deleteRegTarget.id);
			deleteRegOpen = false;
			showNotice(t('Berhasil menghapus regulasi.'));
			await loadRegulations(activeCountryCode, selectedCategory);
		} catch (err: unknown) {
			deleteRegError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			deleteRegSaving = false;
		}
	}

	function cloneToCustom(reg: AdminRegulation) {
		rCategory = reg.rule_category;
		rForbidden = reg.forbidden_keywords;
		rRequired = reg.required_specs;
		rDescription = reg.description_rule;
		rError = '';
		createRegOpen = true;
	}

	// CSV import
	function openImportCsv() {
		selectedCsvFile = null;
		importResult = '';
		importError = '';
		importCsvOpen = true;
	}

	function handleFileSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			selectedCsvFile = target.files[0];
			importError = '';
		}
	}

	async function handleImportCsv() {
		if (!selectedCsvFile) {
			importError = t('Pilih file CSV terlebih dahulu.');
			return;
		}
		importing = true;
		importError = '';
		try {
			const res = await importAdminRegulations(selectedCsvFile);
			const count = res.data?.imported ?? 0;
			importResult = `${t('Berhasil mengimpor')} ${count} ${t('regulasi.')}`;
			showNotice(`${t('Berhasil mengimpor')} ${count} ${t('regulasi.')}`);
			await loadCountries();
			if (activeCountryCode) {
				await loadRegulations(activeCountryCode, selectedCategory);
			}
			setTimeout(() => {
				importCsvOpen = false;
			}, 1500);
		} catch (err: unknown) {
			importError = err instanceof Error ? err.message : t('Gagal menyimpan.');
		} finally {
			importing = false;
		}
	}

	function downloadSampleCsv() {
		const header = 'country_code,rule_category,forbidden_keywords,required_specs,description_rule\n';
		const row1 = 'JP,Sanitary,boraks;formalin,JAS Certificate;Pesticide residue test,Standar residu pertanian Jepang MHLW dan sertifikasi JAS.\n';
		const row2 = 'US,Labeling,none,FDA registration;Nutrition facts,Kemasan harus memenuhi format FDA 21 CFR bagian 101.\n';
		const row3 = 'DE,Packaging,non-recyclable plastic,Lucid Register;CE Marking,Kepatuhan Verpackungsgesetz (VerpackG) dan registrasi LUCID Jerman.\n';
		const blob = new Blob([header + row1 + row2 + row3], { type: 'text/csv;charset=utf-8;' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.setAttribute('href', url);
		link.setAttribute('download', 'template_regulasi_ekspor.csv');
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		URL.revokeObjectURL(url);
	}

	function getCategoryColor(cat: string) {
		switch (cat.toLowerCase()) {
			case 'sanitary':
				return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/20';
			case 'labeling':
				return 'bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/20';
			case 'customs':
				return 'bg-purple-500/15 text-purple-700 dark:text-purple-400 border-purple-500/20';
			case 'packaging':
				return 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/20';
			case 'standards':
				return 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border-cyan-500/20';
			default:
				return 'bg-slate-500/15 text-slate-700 dark:text-slate-300 border-slate-500/20';
		}
	}
</script>

<svelte:head>
	<title>{t('Kelola Negara & Regulasi')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Countries & Regulations')} eyebrow={t('Admin Intelijen & Regulasi')}>
	{#snippet sidebar()}
		<AdminSidebar />
	{/snippet}
	{#if !isAdmin}
		<div class="grid place-items-center gap-4 rounded-xl border border-destructive/30 bg-destructive/5 p-12 text-center">
			<ShieldAlertIcon class="size-12 text-destructive/60" />
			<div>
				<h2 class="text-xl font-bold">{t('Akses Ditolak')}</h2>
				<p class="mt-1 text-sm text-muted-foreground">{t('Halaman ini khusus Admin.')}</p>
			</div>
			<div class="flex gap-3">
				<Button href="/dashboard" variant="outline">{t('Kembali ke Dashboard')}</Button>
				<Button href="/countries" variant="default">{t('Lihat Direktori Publik')}</Button>
			</div>
		</div>
	{:else}
		<!-- Toast notifications -->
		{#if noticeMessage}
			<div class="mb-4 flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
				<div class="flex items-center gap-2">
					<CheckCircle2Icon class="size-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
					<span>{noticeMessage}</span>
				</div>
				<button onclick={() => (noticeMessage = '')} class="text-xs opacity-70 hover:opacity-100">{t('Tutup')}</button>
			</div>
		{/if}
		{#if errorMessage}
			<div class="mb-4 flex items-center justify-between rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-semibold text-destructive">
				<div class="flex items-center gap-2">
					<ShieldAlertIcon class="size-4 shrink-0" />
					<span>{errorMessage}</span>
				</div>
				<button onclick={() => (errorMessage = '')} class="text-xs opacity-70 hover:opacity-100">{t('Tutup')}</button>
			</div>
		{/if}

		<!-- Hero card & Actions -->
		<Card class="mb-6 p-6 md:p-8">
			<div class="flex flex-wrap items-end justify-between gap-6">
				<div class="max-w-2xl">
					<div class="flex items-center gap-2">
						<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">
							<ShieldCheckIcon class="size-3.5" />
							{t('Master Intelijen Kepatuhan')}
						</Badge>
						<Badge variant="secondary">
							{t('Akses Administrator')}
						</Badge>
					</div>
					<h1 class="mt-3 font-display text-3xl font-black tracking-tight text-[#0b1d3a] md:text-4xl dark:text-white">
						{t('Kelola Negara & Regulasi')}
					</h1>
					<CardDescription class="mt-2 max-w-xl leading-relaxed">
						{t('Konfigurasi database negara tujuan, aturan kepabeanan, parameter larangan/pembatasan, dan spesifikasi wajib per komoditas.')}
					</CardDescription>
				</div>
				<div class="flex flex-wrap items-center gap-2.5">
					<Button onclick={openCreateCountry} variant="default">
						<PlusIcon class="size-4" />
						{t('Tambah Negara')}
					</Button>
					<Button onclick={openImportCsv} variant="outline">
						<UploadIcon class="size-4" />
						{t('Import CSV')}
					</Button>
					<Button href="/countries" variant="outline">
						<GlobeIcon class="size-4" />
						{t('Lihat Direktori Publik')}
					</Button>
					<Button href="/admin" variant="ghost">
						{t('Admin Panel')}
					</Button>
				</div>
			</div>

			<!-- Stat counters -->
			<div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
				<div class="rounded-xl border bg-muted/40 p-4">
					<span class="text-xs font-semibold text-muted-foreground">{t('Total Negara')}</span>
					<div class="mt-1 text-2xl font-black text-foreground">{countries.length}</div>
				</div>
				<div class="rounded-xl border bg-muted/40 p-4">
					<span class="text-xs font-semibold text-muted-foreground">{t('Negara Kustom')}</span>
					<div class="mt-1 text-2xl font-black text-primary">{customCountriesCount}</div>
				</div>
				<div class="rounded-xl border bg-muted/40 p-4">
					<span class="text-xs font-semibold text-muted-foreground">{t('Regulasi Terdaftar')}</span>
					<div class="mt-1 text-2xl font-black text-foreground">{regulations.length}</div>
				</div>
				<div class="rounded-xl border bg-muted/40 p-4">
					<span class="text-xs font-semibold text-muted-foreground">{t('Kawasan Terdaftar')}</span>
					<div class="mt-1 text-2xl font-black text-foreground">{uniqueRegions}</div>
				</div>
			</div>
		</Card>

		<!-- Horizontal Country Selector Panel -->
		<Card class="mb-6">
			<CardHeader class="flex flex-wrap items-center justify-between gap-3 p-4 pb-3 border-b">
				<div class="flex items-center gap-2">
					<GlobeIcon class="size-4 text-primary" />
					<CardTitle class="text-sm font-bold">
						{t('Pilih Negara')} ({filteredCountries.length})
					</CardTitle>
					{#if activeCountryCode}
						<Badge variant="outline" class="font-mono text-xs">
							{flagEmoji(activeCountryCode)} {activeCountryCode}
						</Badge>
					{/if}
				</div>
				<div class="flex flex-wrap items-center gap-2">
					<div class="relative w-48 sm:w-64">
						<SearchIcon class="absolute top-1/2 left-2.5 size-3.5 -translate-y-1/2 text-muted-foreground" />
						<Input
							type="search"
							bind:value={countrySearch}
							placeholder={t('Cari kode atau nama negara...')}
							class="h-8 pl-8 text-xs"
						/>
					</div>
					<button
						onclick={loadCountries}
						class="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
						title={t('Segarkan')}
					>
						<RefreshCwIcon class="size-3.5 {countriesLoading ? 'animate-spin' : ''}" />
					</button>
				</div>
			</CardHeader>
			<CardContent class="p-4 space-y-3">
				<!-- Region Filter Pills -->
				<div class="flex flex-wrap gap-1">
					<button
						type="button"
						onclick={() => { selectedRegion = ''; countryPage = 1; }}
						class="rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors {selectedRegion === '' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
					>
						{t('Semua Kawasan')}
					</button>
					{#each regions as r}
						<button
							type="button"
							onclick={() => { selectedRegion = selectedRegion === r ? '' : r; countryPage = 1; }}
							class="rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors {selectedRegion === r ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
						>
							{r}
						</button>
					{/each}
				</div>

				<!-- Countries Chips -->
				{#if countriesLoading}
					<div class="flex flex-wrap gap-1.5">
						{#each Array(10) as _}
							<div class="h-7 w-24 animate-pulse rounded-full bg-muted/60"></div>
						{/each}
					</div>
				{:else if filteredCountries.length === 0}
					<div class="p-4 text-center text-xs text-muted-foreground">
						{t('Tidak ada negara yang sesuai.')}
					</div>
				{:else}
					<div class="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto p-1">
						{#each pagedCountries as c (c.country_code)}
							<button
								type="button"
								onclick={() => selectCountry(c.country_code)}
								class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs transition-colors hover:bg-accent {activeCountryCode === c.country_code ? 'border-primary bg-primary font-bold text-primary-foreground shadow-xs' : 'text-muted-foreground hover:text-foreground'}"
							>
								<span>{flagEmoji(c.country_code)}</span>
								<span class="truncate font-medium">{c.country_name}</span>
								<span class="text-[10px] font-mono opacity-80">({c.country_code})</span>
								{#if c.regulationsCount !== undefined && c.regulationsCount > 0}
									<Badge variant={activeCountryCode === c.country_code ? 'secondary' : 'outline'} class="h-4 shrink-0 px-1 text-[10px]">
										{c.regulationsCount}
									</Badge>
								{/if}
								{#if c.id && c.id.startsWith('CTY-')}
									<span class="size-1.5 rounded-full bg-emerald-500" title={t('Kustom')}></span>
								{/if}
							</button>
						{/each}
					</div>
					<div class="pt-2 border-t">
						<Pagination
							bind:page={countryPage}
							bind:pageSize={countryPageSize}
							totalPages={totalCountryPages}
							totalItems={filteredCountries.length}
						/>
					</div>
				{/if}
			</CardContent>
		</Card>

		<!-- Full-width Country Regulations Panel -->
		<div class="space-y-4">
			{#if !selectedCountry}
				<Card class="p-12 text-center text-muted-foreground">
					<GlobeIcon class="mx-auto size-12 opacity-30" />
					<h3 class="mt-3 text-lg font-bold">{t('Pilih Negara')}</h3>
					<p class="mt-1 text-sm">{t('Pilih negara di atas untuk melihat dan mengelola regulasinya.')}</p>
				</Card>
			{:else}
				<!-- Selected Country Details Banner -->
				<Card class="p-5">
					<div class="flex flex-wrap items-center justify-between gap-4">
						<div class="flex items-center gap-3">
							<span class="text-3xl select-none">{flagEmoji(selectedCountry.country_code)}</span>
							<div>
								<div class="flex items-center gap-2">
									<h2 class="text-xl font-bold tracking-tight text-foreground">
										{selectedCountry.country_name}
									</h2>
									<Badge variant="secondary" class="font-mono text-xs">{selectedCountry.country_code}</Badge>
									{#if selectedCountry.id && selectedCountry.id.startsWith('CTY-')}
										<Badge variant="default" class="text-xs">{t('Negara Kustom')}</Badge>
									{:else}
										<Badge variant="outline" class="text-xs">{t('Master Data')}</Badge>
									{/if}
								</div>
								<p class="text-xs text-muted-foreground mt-0.5">
									{selectedCountry.region || '—'} • {regulations.length} {t('aturan tercatat')}
								</p>
							</div>
						</div>
						<div class="flex flex-wrap items-center gap-2">
							<Button onclick={openCreateRegulation} size="sm" variant="default">
								<PlusIcon class="size-4" />
								{t('Tambah Regulasi')}
							</Button>
							{#if selectedCountry.id && selectedCountry.id.startsWith('CTY-')}
								<Button onclick={() => openEditCountry(selectedCountry)} size="sm" variant="outline">
									<PencilIcon class="size-3.5" />
									{t('Edit Negara')}
								</Button>
								<Button onclick={() => openDeleteCountry(selectedCountry)} size="sm" variant="outline" class="text-destructive hover:bg-destructive/10">
									<Trash2Icon class="size-3.5" />
									{t('Hapus Negara')}
								</Button>
							{/if}
							<Button
								href={`/countries/${selectedCountry.country_code}`}
								target="_blank"
								size="sm"
								variant="outline"
							>
								<ExternalLinkIcon class="size-3.5" />
								{t('Lihat Direktori Publik')}
							</Button>
						</div>
					</div>

						<!-- Category Filter Pills -->
						<div class="mt-4 flex flex-wrap items-center gap-1.5 border-t pt-3">
							<span class="mr-1 text-xs font-semibold text-muted-foreground">{t('Kategori Aturan')}:</span>
							<button
								type="button"
								onclick={() => (selectedCategory = '')}
								class="rounded-full px-2.5 py-1 text-xs font-semibold transition-colors {selectedCategory === '' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
							>
								{t('Semua Kategori')}
							</button>
							{#each ruleCategories as cat}
								<button
									type="button"
									onclick={() => (selectedCategory = selectedCategory === cat ? '' : cat)}
									class="rounded-full px-2.5 py-1 text-xs font-semibold transition-colors {selectedCategory === cat ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
								>
									{cat}
								</button>
							{/each}
						</div>
					</Card>

					<!-- Regulations List -->
					{#if regulationsLoading}
						<div class="space-y-3">
							{#each Array(4) as _}
								<Card class="p-5">
									<div class="h-5 w-24 animate-pulse rounded bg-muted/60"></div>
									<div class="mt-3 h-12 w-full animate-pulse rounded bg-muted/40"></div>
								</Card>
							{/each}
						</div>
					{:else if regulations.length === 0}
						<Card class="p-10 text-center">
							<FileTextIcon class="mx-auto size-10 opacity-30 text-muted-foreground" />
							<h4 class="mt-3 text-base font-bold">{t('Belum ada regulasi untuk negara ini.')}</h4>
							<p class="mt-1 text-xs text-muted-foreground">
								{t('Tambahkan regulasi impor/ekspor khusus untuk membantu verifikasi kepatuhan produk.')}
							</p>
							<div class="mt-4">
								<Button onclick={openCreateRegulation} size="sm">
									<PlusIcon class="size-4" />
									{t('Tambah Regulasi Pertama')}
								</Button>
							</div>
						</Card>
					{:else}
						<div class="space-y-3">
							{#each regulations as reg (reg.id)}
								<Card class="p-5 transition-shadow hover:shadow-xs">
									<div class="flex flex-wrap items-start justify-between gap-3">
										<div class="flex items-center gap-2">
											<span class={`rounded-full border px-2.5 py-0.5 text-xs font-bold ${getCategoryColor(reg.rule_category)}`}>
												{reg.rule_category}
											</span>
											{#if reg.id.startsWith('static-')}
												<Badge variant="outline" class="text-[10px] text-muted-foreground">
													{t('Master Data (Read-only)')}
												</Badge>
											{:else}
												<Badge variant="secondary" class="text-[10px]">
													{t('Kustom')}
												</Badge>
											{/if}
										</div>
										<div class="flex items-center gap-1.5">
											{#if reg.id.startsWith('static-')}
												<Button
													onclick={() => cloneToCustom(reg)}
													variant="ghost"
													size="sm"
													class="h-7 gap-1 text-xs"
													title={t('Klon & Sesuaikan')}
												>
													<CopyIcon class="size-3" />
													{t('Klon & Sesuaikan')}
												</Button>
											{:else}
												<Button
													onclick={() => openEditRegulation(reg)}
													variant="outline"
													size="sm"
													class="h-7 gap-1 text-xs"
												>
													<PencilIcon class="size-3" />
													{t('Edit')}
												</Button>
												<Button
													onclick={() => openDeleteRegulation(reg)}
													variant="outline"
													size="sm"
													class="h-7 gap-1 text-xs text-destructive hover:bg-destructive/10"
												>
													<Trash2Icon class="size-3" />
													{t('Hapus')}
												</Button>
											{/if}
										</div>
									</div>

									<p class="mt-3 text-sm leading-relaxed text-foreground font-medium">
										{reg.description_rule}
									</p>

									<div class="mt-4 grid gap-3 sm:grid-cols-2">
										<!-- Forbidden keywords -->
										<div class="rounded-lg border bg-muted/20 p-3">
											<span class="text-xs font-bold uppercase tracking-wider text-destructive">
												{t('Kata Kunci Dilarang')}
											</span>
											<div class="mt-1.5 flex flex-wrap gap-1.5">
												{#if reg.forbidden_keywords && reg.forbidden_keywords.trim()}
													{#each reg.forbidden_keywords.split(/[,;]+/) as kw}
														{#if kw.trim()}
															<span class="inline-flex items-center rounded bg-destructive/10 px-2 py-0.5 text-xs font-semibold text-destructive">
																{kw.trim()}
															</span>
														{/if}
													{/each}
												{:else}
													<span class="text-xs italic text-muted-foreground">{t('Tidak ada pembatasan khusus')}</span>
												{/if}
											</div>
										</div>

										<!-- Required specs -->
										<div class="rounded-lg border bg-muted/20 p-3">
											<span class="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
												{t('Spesifikasi Wajib')}
											</span>
											<div class="mt-1.5 flex flex-wrap gap-1.5">
												{#if reg.required_specs && reg.required_specs.trim()}
													{#each reg.required_specs.split(/[,;]+/) as req}
														{#if req.trim()}
															<span class="inline-flex items-center rounded bg-emerald-500/10 px-2 py-0.5 text-xs font-semibold text-emerald-800 dark:text-emerald-300">
																{req.trim()}
															</span>
														{/if}
													{/each}
												{:else}
													<span class="text-xs italic text-muted-foreground">{t('Tidak ada spesifikasi wajib')}</span>
												{/if}
											</div>
										</div>
									</div>
								</Card>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
	{/if}
</AppShell>

<!-- Create Country Dialog -->
{#if createCountryOpen}
	<Dialog.Root bind:open={createCountryOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Tambah Negara Baru')}</Dialog.Title>
				<Dialog.Description>
					{t('Tambahkan yurisdiksi baru ke dalam database intelijen kepabeanan.')}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-3 py-3">
				{#if cError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{cError}</p>
				{/if}
				<div class="grid gap-1">
					<label for="c-code" class="text-xs font-bold text-muted-foreground">{t('Kode Negara (ISO-2)')}</label>
					<Input
						id="c-code"
						bind:value={cCode}
						placeholder="contoh: VN, BR, EG"
						maxlength={2}
						class="uppercase font-mono"
					/>
				</div>
				<div class="grid gap-1">
					<label for="c-name" class="text-xs font-bold text-muted-foreground">{t('Nama Negara')}</label>
					<Input
						id="c-name"
						bind:value={cName}
						placeholder="contoh: Vietnam, Brazil"
					/>
				</div>
				<div class="grid gap-1">
					<label for="c-region" class="text-xs font-bold text-muted-foreground">{t('Kawasan / Region')}</label>
					<NativeSelect id="c-region" bind:value={cRegion} class="w-full">
						{#each regions as r}
							<option value={r}>{r}</option>
						{/each}
					</NativeSelect>
				</div>
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (createCountryOpen = false)}>{t('Batal')}</Button>
				<Button disabled={cSaving} onclick={handleCreateCountry}>
					{cSaving ? t('Menyimpan...') : t('Simpan Negara')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Edit Country Dialog -->
{#if editCountryOpen}
	<Dialog.Root bind:open={editCountryOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Edit Negara')} — {editCountryTarget?.country_code}</Dialog.Title>
				<Dialog.Description>
					{t('Perbarui informasi master data negara.')}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-3 py-3">
				{#if eError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{eError}</p>
				{/if}
				<div class="grid gap-1">
					<label for="e-name" class="text-xs font-bold text-muted-foreground">{t('Nama Negara')}</label>
					<Input id="e-name" bind:value={eName} />
				</div>
				<div class="grid gap-1">
					<label for="e-region" class="text-xs font-bold text-muted-foreground">{t('Kawasan / Region')}</label>
					<NativeSelect id="e-region" bind:value={eRegion} class="w-full">
						{#each regions as r}
							<option value={r}>{r}</option>
						{/each}
					</NativeSelect>
				</div>
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (editCountryOpen = false)}>{t('Batal')}</Button>
				<Button disabled={eSaving} onclick={handleUpdateCountry}>
					{eSaving ? t('Menyimpan...') : t('Simpan')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Delete Country Dialog -->
{#if deleteCountryOpen}
	<Dialog.Root bind:open={deleteCountryOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Hapus Negara')}</Dialog.Title>
				<Dialog.Description>
					{t('Apakah Anda yakin ingin menghapus negara ini? Tindakan ini tidak dapat dibatalkan.')}
					<strong class="block mt-2 font-mono text-sm text-foreground">
						{deleteCountryTarget?.country_name} ({deleteCountryTarget?.country_code})
					</strong>
				</Dialog.Description>
			</Dialog.Header>
			{#if deleteCountryError}
				<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{deleteCountryError}</p>
			{/if}
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (deleteCountryOpen = false)}>{t('Batal')}</Button>
				<Button variant="destructive" disabled={deleteCountrySaving} onclick={handleDeleteCountry}>
					{deleteCountrySaving ? t('Menghapus...') : t('Hapus')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Create Regulation Dialog -->
{#if createRegOpen}
	<Dialog.Root bind:open={createRegOpen}>
		<Dialog.Content class="sm:max-w-xl">
			<Dialog.Header>
				<Dialog.Title>
					{t('Tambah Regulasi Baru')} — {selectedCountry?.country_name} ({activeCountryCode})
				</Dialog.Title>
				<Dialog.Description>
					{t('Konfigurasi parameter aturan impor atau ekspor khusus untuk yurisdiksi ini.')}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-3 py-3">
				{#if rError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{rError}</p>
				{/if}
				<div class="grid gap-1">
					<label for="r-cat" class="text-xs font-bold text-muted-foreground">{t('Kategori Aturan')}</label>
					<NativeSelect id="r-cat" bind:value={rCategory} class="w-full">
						{#each ruleCategories as cat}
							<option value={cat}>{cat}</option>
						{/each}
					</NativeSelect>
				</div>
				<div class="grid gap-1">
					<label for="r-desc" class="text-xs font-bold text-muted-foreground">{t('Deskripsi Aturan')}</label>
					<Textarea
						id="r-desc"
						bind:value={rDescription}
						rows={3}
						placeholder="contoh: Produk kosmetik wajib memiliki notifikasi BPOM/FDA setempat dan daftar bahan baku INCI..."
					/>
				</div>
				<div class="grid gap-1">
					<label for="r-forbid" class="text-xs font-bold text-muted-foreground">{t('Kata Kunci Dilarang (pisahkan koma/titik koma)')}</label>
					<Input
						id="r-forbid"
						bind:value={rForbidden}
						placeholder="contoh: hidrokuinon, merkuri, formalin"
					/>
				</div>
				<div class="grid gap-1">
					<label for="r-req" class="text-xs font-bold text-muted-foreground">{t('Spesifikasi Wajib (pisahkan koma/titik koma)')}</label>
					<Input
						id="r-req"
						bind:value={rRequired}
						placeholder="contoh: Uji Laboratorium Akreditasi, Sertifikat Analisis (CoA)"
					/>
				</div>
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (createRegOpen = false)}>{t('Batal')}</Button>
				<Button disabled={rSaving} onclick={handleCreateRegulation}>
					{rSaving ? t('Menyimpan...') : t('Simpan Regulasi')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Edit Regulation Dialog -->
{#if editRegOpen}
	<Dialog.Root bind:open={editRegOpen}>
		<Dialog.Content class="sm:max-w-xl">
			<Dialog.Header>
				<Dialog.Title>{t('Edit Regulasi')} — {editRegTarget?.id}</Dialog.Title>
				<Dialog.Description>
					{t('Perbarui parameter aturan regulasi.')}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-3 py-3">
				{#if erError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{erError}</p>
				{/if}
				<div class="grid gap-1">
					<label for="er-cat" class="text-xs font-bold text-muted-foreground">{t('Kategori Aturan')}</label>
					<NativeSelect id="er-cat" bind:value={erCategory} class="w-full">
						{#each ruleCategories as cat}
							<option value={cat}>{cat}</option>
						{/each}
					</NativeSelect>
				</div>
				<div class="grid gap-1">
					<label for="er-desc" class="text-xs font-bold text-muted-foreground">{t('Deskripsi Aturan')}</label>
					<Textarea id="er-desc" bind:value={erDescription} rows={3} />
				</div>
				<div class="grid gap-1">
					<label for="er-forbid" class="text-xs font-bold text-muted-foreground">{t('Kata Kunci Dilarang (pisahkan koma/titik koma)')}</label>
					<Input id="er-forbid" bind:value={erForbidden} />
				</div>
				<div class="grid gap-1">
					<label for="er-req" class="text-xs font-bold text-muted-foreground">{t('Spesifikasi Wajib (pisahkan koma/titik koma)')}</label>
					<Input id="er-req" bind:value={erRequired} />
				</div>
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (editRegOpen = false)}>{t('Batal')}</Button>
				<Button disabled={erSaving} onclick={handleUpdateRegulation}>
					{erSaving ? t('Menyimpan...') : t('Simpan')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Delete Regulation Dialog -->
{#if deleteRegOpen}
	<Dialog.Root bind:open={deleteRegOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title>{t('Hapus Regulasi')}</Dialog.Title>
				<Dialog.Description>
					{t('Apakah Anda yakin ingin menghapus regulasi ini?')}
					<strong class="block mt-2 text-xs font-mono text-foreground">
						{deleteRegTarget?.id} • {deleteRegTarget?.rule_category}
					</strong>
				</Dialog.Description>
			</Dialog.Header>
			{#if deleteRegError}
				<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{deleteRegError}</p>
			{/if}
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (deleteRegOpen = false)}>{t('Batal')}</Button>
				<Button variant="destructive" disabled={deleteRegSaving} onclick={handleDeleteRegulation}>
					{deleteRegSaving ? t('Menghapus...') : t('Hapus')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Import CSV Dialog -->
{#if importCsvOpen}
	<Dialog.Root bind:open={importCsvOpen}>
		<Dialog.Content class="sm:max-w-lg">
			<Dialog.Header>
				<Dialog.Title>{t('Import Regulasi dari File CSV')}</Dialog.Title>
				<Dialog.Description>
					{t('Unggah file CSV berisi aturan regulasi kepabeanan dalam batch.')}
				</Dialog.Description>
			</Dialog.Header>
			<div class="grid gap-4 py-3">
				{#if importError}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">{importError}</p>
				{/if}
				{#if importResult}
					<p class="rounded-lg bg-emerald-500/10 px-3 py-2 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
						{importResult}
					</p>
				{/if}

				<div class="rounded-lg border bg-muted/40 p-3 text-xs leading-relaxed text-muted-foreground">
					<span class="font-bold text-foreground">{t('Format Kolom CSV Wajib')}:</span>
					<code class="mt-1 block font-mono text-[11px] bg-background p-1.5 rounded border">
						country_code,rule_category,forbidden_keywords,required_specs,description_rule
					</code>
					<p class="mt-1 text-[11px]">
						{t('Contoh baris')}: <code>JP,Sanitary,boraks;formalin,JAS Certificate,Standar residu MHLW</code>
					</p>
				</div>

				<div class="flex items-center justify-between gap-3">
					<Button onclick={downloadSampleCsv} variant="outline" size="sm" class="gap-1.5 text-xs">
						<DownloadIcon class="size-3.5" />
						{t('Unduh Contoh Template CSV')}
					</Button>
				</div>

				<div class="grid gap-1">
					<label for="csv-file-input" class="text-xs font-bold text-muted-foreground">{t('Pilih File CSV')}</label>
					<input
						id="csv-file-input"
						type="file"
						accept=".csv"
						onchange={handleFileSelect}
						class="block w-full text-xs text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-xs file:font-semibold file:text-primary-foreground hover:file:bg-primary/90"
					/>
				</div>
			</div>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (importCsvOpen = false)}>{t('Batal')}</Button>
				<Button disabled={!selectedCsvFile || importing} onclick={handleImportCsv}>
					{importing ? t('Mengunggah...') : t('Upload & Terapkan')}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}
