<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import { businessProfiles as seedProfiles } from '$lib/data/trade';
	import { listBusinessProfiles, getBusinessProfile, updateCertifications } from '$lib/api/business-profile';
	import { createRemoteList } from '$lib/api/remote-list.svelte';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';

	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import SearchIcon from '@lucide/svelte/icons/search';
	import XIcon from '@lucide/svelte/icons/x';
	import CheckIcon from '@lucide/svelte/icons/check';

	let profiles = createRemoteList(listBusinessProfiles, seedProfiles);
	$effect(() => {
		profiles.load();
	});
	let selectedId = $state('');
	let profile = $derived(profiles.items.find((p) => p.id === selectedId) ?? profiles.items[0] ?? seedProfiles[0]);
	$effect(() => {
		if (!selectedId && (profiles.items[0]?.id ?? '')) selectedId = profiles.items[0].id;
	});

	// ── Searchable profile dropdown ──
	let searchQuery = $state('');
	let dropdownOpen = $state(false);
	let expandedGroup = $state<string | null>(null);

	// Filter berdasarkan pencarian
	let searchedProfiles = $derived(
		searchQuery.trim()
			? profiles.items.filter((p) =>
					(p.companyName ?? '').toLowerCase().includes(searchQuery.toLowerCase())
				)
			: profiles.items
	);

	// Group berdasarkan nama perusahaan (untuk duplikat)
	let groupedProfiles = $derived.by(() => {
		const map = new Map<string, typeof profiles.items>();
		for (const p of searchedProfiles) {
			const key = p.companyName ?? 'Tanpa nama';
			if (!map.has(key)) map.set(key, []);
			map.get(key)!.push(p);
		}
		return [...map.entries()].map(([name, items]) => ({ name, items }));
	});

	function toggleGroup(name: string) {
		expandedGroup = expandedGroup === name ? null : name;
	}

	function selectFromDropdown(id: string) {
		selectProfile(id);
		dropdownOpen = false;
		expandedGroup = null;
		searchQuery = '';
	}

	// Tutup dropdown saat klik di luar
	import { onMount } from 'svelte';
	let dropdownEl = $state<HTMLDivElement | null>(null);
	onMount(() => {
		function handleClick(e: MouseEvent) {
			if (dropdownEl && !dropdownEl.contains(e.target as Node)) {
				dropdownOpen = false;
				expandedGroup = null;
				searchQuery = '';
			}
		}
		document.addEventListener('click', handleClick);
		return () => document.removeEventListener('click', handleClick);
	});

	// Selected label
	let selectedLabel = $derived(profile?.companyName ?? t('Pilih profil...'));

	const certOptions = ['Halal', 'ISO 22000', 'HACCP', 'SVLK', 'Organic', 'Origin declaration', 'Nutrition facts'];
	let saving = $state(false);
	let certSaved = $state(false);
	let certError = $state('');

	async function saveCerts() {
		saving = true;
		certError = '';
		certSaved = false;
		try {
			await updateCertifications(profile.id, profile.certifications);
			certSaved = true;
		} catch {
			certError = t('Gagal menyimpan sertifikasi.');
		} finally {
			saving = false;
		}
	}

	function trCert(c: string) {
		return t(c === 'Organic' ? 'Organik' : c === 'Origin declaration' ? 'Deklarasi asal' : c === 'Nutrition facts' ? 'Informasi nilai gizi' : c);
	}

	function trStatus(s: string) {
		return t(s === 'Verified' ? 'Terverifikasi' : s === 'Archived' ? 'Diarsipkan' : 'Menunggu');
	}

	function toggleCert(cert: string) {
		profile.certifications = profile.certifications.includes(cert)
			? profile.certifications.filter((item) => item !== cert)
			: [...profile.certifications, cert];
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	let detailLoading = $state(false);
	let detailError = $state('');

	async function selectProfile(id: string) {
		selectedId = id;
		detailError = '';
		detailLoading = true;
		try {
			const res = await getBusinessProfile(id);
			const fresh = res.data as (typeof seedProfiles)[number] & { certifications?: string[] };
			const idx = profiles.items.findIndex((p) => p.id === id);
			if (idx >= 0) profiles.items[idx] = fresh;
		} catch {
			detailError = t('Gagal memuat detail profil.');
		} finally {
			detailLoading = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Profil Bisnis')} | MauEkspor</title>
</svelte:head>

<AppShell title="Business Profile" eyebrow={t('Identitas UMKM dan sertifikasi')}>
	{#if profiles.items.length > 1}
		<div bind:this={dropdownEl} class="relative z-20 mb-4 max-w-md">
			<!-- Trigger / selected -->
			<button
				type="button"
				onclick={() => (dropdownOpen = !dropdownOpen)}
				class="flex w-full items-center justify-between gap-2 rounded-lg border border-border bg-card px-3 py-2.5 text-left text-sm shadow-sm transition-colors hover:bg-accent/50"
			>
				<span class="truncate font-semibold">{selectedLabel}</span>
				<span class="flex items-center gap-2">
					{#if detailLoading}
						<span class="text-xs text-muted-foreground">{t('Memuat...')}</span>
					{/if}
					<ChevronDownIcon class="size-4 shrink-0 text-muted-foreground transition-transform {dropdownOpen ? 'rotate-180' : ''}" />
				</span>
			</button>

			<!-- Dropdown -->
			{#if dropdownOpen}
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div class="absolute inset-x-0 top-full z-30 mt-1.5 overflow-hidden rounded-lg border border-border bg-card shadow-xl" role="presentation">
					<!-- Search -->
					<div class="flex items-center gap-2 border-b bg-muted/30 px-3 py-2">
						<SearchIcon class="size-4 shrink-0 text-muted-foreground" />
						<input
							type="text"
							placeholder={t('Cari profil...')}
							bind:value={searchQuery}
							class="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
						/>
						{#if searchQuery}
							<button onclick={() => (searchQuery = '')} class="text-muted-foreground hover:text-foreground"><XIcon class="size-3.5" /></button>
						{/if}
					</div>

					<!-- List (max height + scroll) -->
					<div class="max-h-64 overflow-y-auto p-1">
						{#if groupedProfiles.length === 0}
							<p class="px-3 py-4 text-center text-sm text-muted-foreground">{t('Tidak ada profil ditemukan.')}</p>
						{:else}
							{#each groupedProfiles as group}
								{#if group.items.length === 1}
									<!-- Tunggal: langsung pilih -->
									<button
										type="button"
										onclick={() => selectFromDropdown(group.items[0].id)}
										class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent {group.items[0].id === selectedId ? 'bg-accent font-semibold' : ''}"
									>
										<span class="truncate">{group.name}</span>
										{#if group.items[0].id === selectedId}
											<CheckIcon class="size-4 shrink-0 text-primary" />
										{/if}
									</button>
								{:else}
									<!-- Duplikat: grup yang bisa di-expand -->
									<div class="rounded-md">
										<button
											type="button"
											onclick={() => toggleGroup(group.name)}
											class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent"
										>
											<span class="flex min-w-0 items-center gap-2">
												<span class="truncate">{group.name}</span>
												<Badge variant="outline" class="shrink-0">{group.items.length}</Badge>
											</span>
											<ChevronRightIcon class="size-4 shrink-0 text-muted-foreground transition-transform {expandedGroup === group.name ? 'rotate-90' : ''}" />
										</button>
										{#if expandedGroup === group.name}
											<div class="ml-3 border-l border-border pl-2">
												{#each group.items as item}
													<button
														type="button"
														onclick={() => selectFromDropdown(item.id)}
														class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-1.5 text-left text-sm transition-colors hover:bg-accent {item.id === selectedId ? 'bg-accent font-semibold' : ''}"
													>
														<span class="truncate">{item.id}</span>
														{#if item.id === selectedId}
															<CheckIcon class="size-4 shrink-0 text-primary" />
														{/if}
													</button>
												{/each}
											</div>
										{/if}
									</div>
								{/if}
							{/each}
						{/if}
					</div>
				</div>
			{/if}
		</div>
		{#if detailError}
			<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{detailError}</p>
		{/if}
	{/if}

	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(profile.status))}>{trStatus(profile.status)}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{profile.companyName}
				</CardTitle>
				<CardDescription class="mt-2">{profile.address}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Kesiapan ekspor')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{profile.readiness}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Detail perusahaan')}</CardTitle>
					<CardDescription class="mt-1.5">{t('Identitas inti yang digunakan di seluruh alur kerja produk, kepatuhan, dan kutipan harga.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" href="/business-profile/edit">{t('Edit profil')}</Button>
					<Button href="/business-profile/certifications">{t('Kelola sertifikasi')}</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kapasitas produksi')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.productionCapacity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tahun berdiri')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.yearEstablished}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Sertifikasi')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.certifications.length}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{profile.owner}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>{t('Kelola sertifikasi')}</CardTitle>
				<CardDescription>{t('Centang kotak untuk menambah atau menghapus klaim sertifikasi pada profil bisnis.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-2.5 sm:grid-cols-2">
				{#each certOptions as cert}
					<label class="flex cursor-pointer items-center gap-2.5 rounded-lg border bg-muted/30 p-3">
						<Checkbox
							checked={profile.certifications.includes(cert)}
							onCheckedChange={() => toggleCert(cert)}
						/>
						<span class="text-sm font-bold">{trCert(cert)}</span>
					</label>
				{/each}
				<div class="sm:col-span-2 mt-1">
					<Button size="sm" onclick={saveCerts} disabled={saving}>
						{saving ? t('Menyimpan...') : t('Simpan sertifikasi')}
					</Button>
					{#if certSaved}
						<span class="ml-2 text-xs font-bold text-emerald-600">{t('Tersimpan')} ✓</span>
					{/if}
					{#if certError}
						<span class="ml-2 text-xs font-bold text-destructive">{certError}</span>
					{/if}
				</div>
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">{t('Wawasan kesiapan')}</Badge>
				<CardTitle>{t('Tingkatkan sisa')} {100 - profile.readiness}%</CardTitle>
			</CardHeader>
			<CardContent>
				<p class="leading-relaxed text-muted-foreground">
					{t('Sertifikasi berbasis bukti, data produk yang konsisten, dan berkas kepatuhan yang lengkap adalah jalur tercepat menuju skor kesiapan profil yang lebih tinggi.')}
				</p>
			</CardContent>
		</Card>
	</div>
</AppShell>