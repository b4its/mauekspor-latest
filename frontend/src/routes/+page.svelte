<script lang="ts">
	import AosInit from '$lib/components/AosInit.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import { products, projects, buyers, exportAnalyses } from '$lib/data/trade';
	import { getStatus, getUser, logout, fetchSession } from '$lib/stores/session.svelte';
	import { t } from '$lib/i18n.svelte';

	import MenuIcon from '@lucide/svelte/icons/menu';
	import LayoutDashboardIcon from '@lucide/svelte/icons/layout-dashboard';
	import LogOutIcon from '@lucide/svelte/icons/log-out';
	import FaIcon from '$lib/components/FaIcon.svelte';

	let mobileNavOpen = $state(false);
	let loggingOut = $state(false);

	$effect(() => { fetchSession(); });
	let user = $derived(getUser());
	let userStatus = $derived(getStatus());
	let isLoggedIn = $derived(userStatus === 'authenticated' && !!user);

	async function handleLogout() {
		loggingOut = true;
		await logout();
		window.location.href = '/';
	}

	let pipelineValue = $derived(projects.reduce((sum, p) => sum + p.value, 0));
	let exportCount = $derived(products.length);
	let buyerCount = $derived(buyers.length);
	let analysisCount = $derived(exportAnalyses.length);

	const navLinks = [
		{ label: 'Fitur', href: '#features' },
		{ label: 'Peran', href: '#roles' },
		{ label: 'Alur Kerja', href: '#workflow' },
		{ label: 'Cerita', href: '#testimonials' }
	];

	const features = [
		{ fa: 'fa-solid fa-seedling', title: 'Kesiapan Produk Ekspor', text: 'Katalog terstruktur, HS code otomatis, dan standar kualitas internasional untuk menjamin komoditas desa siap diterima pasar global.' },
		{ fa: 'fa-solid fa-globe', title: 'Analisis Pasar Tujuan', text: 'Rekomendasi negara tujuan berdasarkan data permintaan, tarif bea, dan kecocokan produk desa dengan kebutuhan buyer internasional.' },
		{ fa: 'fa-solid fa-shield-halved', title: 'Kepatuhan & Sertifikasi Ekspor', text: 'Cek kepatuhan otomatis: karantina pertanian, ISPM-15, halal, HACCP — semua persyaratan ekspor terverifikasi sebelum pengiriman.' },
		{ fa: 'fa-solid fa-file-lines', title: 'Dokumen Ekspor Lengkap', text: 'Packing list, invoice, bill of lading, certificate of origin, phytosanitary — semua dokumen ekspor tersedia dalam satu workspace.' },
		{ fa: 'fa-solid fa-handshake', title: 'Koneksi Pembeli Global', text: 'Matching otomatis antara komoditas desa dengan buyer internasional berdasarkan spesifikasi, volume, dan HS code.' },
		{ fa: 'fa-solid fa-truck', title: 'Logistik & Pengiriman', text: 'Rekomendasi forwarder, kalkulasi biaya FCL/LCL, dan tracking pengiriman dari gudang desa hingga pelabuhan tujuan.' }
	];

	const steps = [
		{ n: '01', fa: 'fa-solid fa-boxes-stacked', title: 'Standardisasi', text: 'Lengkapi profil komoditas: nama, HS code, spesifikasi, sertifikasi, dan kapasitas produksi.' },
		{ n: '02', fa: 'fa-solid fa-shield-halved', title: 'Kesiapan Ekspor', text: 'Jalankan cek kepatuhan otomatis: regulasi negara tujuan, persyaratan karantina, dan standar kemasan.' },
		{ n: '03', fa: 'fa-solid fa-handshake', title: 'Koneksi & Kirim', text: 'Terima buyer request, buat quotation, siapkan dokumen, dan booking pengiriman dengan forwarder terpercaya.' }
	];

	const roles = [
		{ fa: 'fa-solid fa-wheat-awn', title: 'Petani & Kelompok Tani', text: 'Standarisasi komoditas kebun dan sawah untuk memenuhi standar ekspor internasional dan akses ke pasar premium global.' },
		{ fa: 'fa-solid fa-users', title: 'BUMDes & Koperasi', text: 'Kelola komoditas anggota secara terpusat, bangun brand bersama, dan ekspor langsung ke buyer global tanpa perantara.' },
		{ fa: 'fa-solid fa-award', title: 'Kepala Desa & Dinas', text: 'Monitor kesiapan ekspor desa, koordinasi sertifikasi massal, dan pantau nilai ekspor komoditas daerah secara real-time.' },
		{ fa: 'fa-solid fa-truck', title: 'Forwarder & Logistik', text: 'Terima RFQ dari kelompok tani dan BUMDes, berikan penawaran freight kompetitif, dan kelola dokumen ekspor.' },
		{ fa: 'fa-solid fa-magnifying-glass', title: 'Buyer Internasional', text: 'Temukan komoditas unggulan desa Indonesia yang telah memenuhi standar ekspor dengan traceability dan sertifikasi lengkap.' }
	];

	const testimonials = [
		{ quote: 'Dulu kopi Gayo kami ekspor via broker dengan harga sangat rendah. Dengan MauEkspor, kami bisa ekspor langsung ke Jepang dengan harga 3x lebih baik dan dokumen yang benar.', name: 'Rizal Fahmi', role: 'KSU Kopi Gayo Bener Meriah' },
		{ quote: 'Standarisasi produk dan cek kepatuhan otomatis membuat kami berhasil lolos inspeksi bea cukai Eropa untuk pertama kalinya tanpa biaya konsultan yang mahal.', name: 'Sinta Lestari', role: 'BUMDes Jepara Craft' },
		{ quote: 'Platform ini membantu 12 kelompok tani di kabupaten kami mempersiapkan ekspor rempah dengan dokumentasi yang benar dan terstandar dalam waktu singkat.', name: 'Dr. Bambang Santoso', role: 'Dinas Perdagangan Kabupaten' }
	];
</script>

<svelte:head>
	<title>MauEkspor — Siapkan Komoditas Desa untuk Rantai Pasok Ekspor Global</title>
	<meta name="description" content="Platform digital yang memandu petani, pengrajin, dan UMKM desa untuk mempersiapkan komoditas unggulan memasuki rantai pasok ekspor internasional — dari standarisasi hingga pembeli global." />
	<meta name="keywords" content="ekspor komoditas desa, rantai pasok ekspor, kesiapan ekspor UMKM, mauekspor, kelompok tani ekspor, BUMDes ekspor, sertifikasi ekspor desa, HS code komoditas" />
	<meta property="og:title" content="MauEkspor — Siapkan Komoditas Desa untuk Ekspor Global" />
	<meta property="og:description" content="Platform digital yang memandu petani, pengrajin, dan UMKM desa untuk mempersiapkan komoditas unggulan memasuki rantai pasok ekspor internasional." />
</svelte:head>

<AosInit />

<div class="landing-font min-h-svh bg-[#f4f8ff] text-[#0b1d3a] dark:bg-[#040d1f] dark:text-[#eaf1ff]">
	<div class="mx-auto grid max-w-7xl gap-6 p-4 sm:p-5">
		<header
			class="sticky top-3.5 z-30 flex flex-wrap items-center justify-between gap-4 rounded-full border border-[#0b3d91]/10 bg-white/80 p-3 pl-5 shadow-sm backdrop-blur-xl dark:border-white/10 dark:bg-[#0a1730]/80"
		>
			<a href="/" class="inline-flex items-center gap-1.5">
				<Logo variant="logo" class="!h-9" />
				<span class="font-display text-2xl font-black tracking-tight text-[#0b1d3a] dark:text-white">auEkspor</span>
			</a>

			<nav class="hidden gap-6 text-sm font-bold text-[#0b1d3a]/70 md:flex dark:text-white/70" aria-label={t('Navigasi laman')}>
				{#each navLinks as link}
					<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href={link.href}>{t(link.label)}</a>
				{/each}
			</nav>

			<div class="hidden items-center gap-2 md:flex">
				<ThemeToggle />
				{#if isLoggedIn}
					<Badge variant="outline" class="hidden max-w-[160px] border-[#0b3d91]/20 px-3 py-1.5 lg:inline-flex">
						<span class="truncate text-xs font-bold">{user?.name}</span>
					</Badge>
					<Button href="/dashboard" class="bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">
						<LayoutDashboardIcon class="size-4" />
						<span class="ms-1">{t('Dashboard')}</span>
					</Button>
					<Button variant="outline" onclick={handleLogout} disabled={loggingOut} class="border-[#0b3d91]/20">
						<LogOutIcon class="size-4" />
						<span class="ms-1">{loggingOut ? '...' : t('Logout')}</span>
					</Button>
				{:else}
					<Button variant="outline" href="/login" class="border-[#0b3d91]/20">{t('Masuk')}</Button>
					<Button href="/register" class="bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">{t('Mulai Ekspor')}</Button>
				{/if}
			</div>

			<div class="flex items-center gap-2 md:hidden">
				<ThemeToggle />
				<Sheet.Root bind:open={mobileNavOpen}>
					<Sheet.Trigger>
						{#snippet child({ props })}
							<Button {...props} variant="outline" size="icon" aria-label={t('Buka menu navigasi')}>
								<MenuIcon class="size-5" />
							</Button>
						{/snippet}
					</Sheet.Trigger>
					<Sheet.Content side="right" class="landing-font w-72 border-[#0b3d91]/10 bg-white dark:border-white/10 dark:bg-[#0a1730]">
						<Sheet.Header>
							<Sheet.Title class="flex items-center gap-1.5"><Logo variant="logo" class="!h-7" /><span class="font-display text-xl font-black text-[#0b1d3a] dark:text-white">auEkspor</span></Sheet.Title>
						</Sheet.Header>
						<nav class="flex flex-col gap-1 px-4" aria-label={t('Navigasi seluler')}>
							{#each navLinks as link, index}
								<a
									href={link.href}
									onclick={() => (mobileNavOpen = false)}
									data-aos="fade-left"
									data-aos-delay={index * 60}
									class="rounded-lg px-3 py-2.5 text-sm font-bold text-[#0b1d3a]/80 transition-colors hover:bg-[#0b3d91]/5 hover:text-[#0b3d91] dark:text-white/80 dark:hover:bg-white/5 dark:hover:text-white"
								>
									{t(link.label)}
								</a>
							{/each}
						</nav>
						<Sheet.Footer class="flex-col gap-2">
						{#if isLoggedIn}
							<div class="flex items-center gap-2 rounded-lg border border-[#0b3d91]/10 bg-[#0b3d91]/5 px-3 py-2.5 dark:border-white/10 dark:bg-white/5">
								<div class="grid size-9 shrink-0 place-items-center rounded-full bg-[#0b3d91] font-bold text-white">
									{(user?.name ?? 'U').charAt(0).toUpperCase()}
								</div>
								<div class="min-w-0">
									<p class="truncate text-sm font-bold">{user?.name}</p>
									<p class="truncate text-[11px] text-muted-foreground">{user?.email}</p>
								</div>
							</div>
							<Button href="/dashboard" class="w-full bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85" onclick={() => (mobileNavOpen = false)}>
								<LayoutDashboardIcon class="size-4" />
								<span class="ms-1">{t('Dashboard')}</span>
							</Button>
							<Button variant="outline" class="w-full border-[#0b3d91]/20" onclick={() => { mobileNavOpen = false; handleLogout(); }}>
								<LogOutIcon class="size-4" />
								<span class="ms-1">{loggingOut ? '...' : t('Logout')}</span>
							</Button>
						{:else}
							<Button href="/login" variant="outline" class="w-full border-[#0b3d91]/20" onclick={() => (mobileNavOpen = false)}>{t('Masuk')}</Button>
							<Button href="/register" class="w-full bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85" onclick={() => (mobileNavOpen = false)}>{t('Mulai Ekspor')}</Button>
						{/if}
					</Sheet.Footer>
					</Sheet.Content>
				</Sheet.Root>
			</div>
		</header>

		<section class="relative grid items-center gap-8 overflow-hidden rounded-3xl border border-[#0b3d91]/10 bg-gradient-to-br from-white via-[#eaf2ff] to-[#dbe9ff] p-6 shadow-sm md:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] md:p-12 dark:border-white/10 dark:from-[#0a1730] dark:via-[#0b1f42] dark:to-[#0c2450]">
			<FaIcon icon="fa-solid fa-globe" class="pointer-events-none absolute -right-16 -top-16 text-[8rem] text-[#0b3d91]/5 dark:text-white/5" />

			<div data-aos="fade-right">
				<Badge variant="secondary" class="bg-[#0b3d91]/10 text-[#0b3d91] dark:bg-white/10 dark:text-white">
					<FaIcon icon="fa-solid fa-seedling" class="text-sm" />
					{t('Platform Ekspor Komoditas Desa')}
				</Badge>
				<h1 class="mt-4 font-display text-5xl font-black leading-[0.95] tracking-tight text-[#0b1d3a] sm:text-6xl md:text-7xl dark:text-white">
					<span class="text-[#1e63d6] dark:text-[#5ea1ff]">MauEkspor</span>: {t('Siapkan Hasil Desa untuk Rantai Pasok Ekspor Global')}
				</h1>
				<p class="mt-5 max-w-2xl text-lg leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
					{t('Platform digital yang memandu petani, pengrajin, dan UMKM desa untuk mempersiapkan komoditas unggulan memasuki rantai pasok ekspor internasional — dari standarisasi komoditas hingga terhubung dengan pembeli global.')}</p>
				<div class="mt-7 flex flex-wrap gap-3">
					<Button size="lg" href="/register" class="h-11 bg-[#0b3d91] px-6 text-base text-white hover:bg-[#0b3d91]/85">
						<FaIcon icon="fa-solid fa-plane-departure" class="text-base" />
						{t('Mulai Persiapan Ekspor')}
					</Button>
					<Button variant="outline" size="lg" href="/dashboard" class="h-11 border-[#0b3d91]/20 px-6 text-base">{t('Pelajari Lebih Lanjut')}</Button>
				</div>
				<div class="mt-6 flex flex-wrap gap-x-5 gap-y-2 text-[13px] font-bold text-[#0b1d3a]/60 dark:text-white/60">
					<span>{t('Standardisasi Komoditas')}</span>
					<span>·</span>
					<span>{t('Kepatuhan Ekspor')}</span>
					<span>·</span>
					<span>{t('Koneksi Pembeli Global')}</span>
				</div>
			</div>

			<div class="relative" data-aos="fade-left" data-aos-delay="150">
				<div class="grid grid-cols-2 gap-3 rounded-2xl border border-[#0b3d91]/10 bg-white/70 p-4 backdrop-blur-sm dark:border-white/10 dark:bg-white/5">
					<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
						<strong class="block text-3xl font-bold tracking-tight text-[#0b3d91] dark:text-[#5ea1ff]">{exportCount}</strong>
						<span class="mt-1.5 block text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Produk siap ekspor')}</span>
					</div>
					<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
						<strong class="block text-3xl font-bold tracking-tight text-[#0b3d91] dark:text-[#5ea1ff]">{analysisCount}</strong>
						<span class="mt-1.5 block text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Analisis pasar')}</span>
					</div>
					<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
						<strong class="block text-3xl font-bold tracking-tight text-[#0b3d91] dark:text-[#5ea1ff]">{buyerCount}</strong>
						<span class="mt-1.5 block text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Akun pembeli')}</span>
					</div>
					<div class="rounded-xl border border-[#0b3d91]/10 bg-white p-4 dark:border-white/10 dark:bg-[#0a1730]">
						<strong class="block text-3xl font-bold tracking-tight text-[#0b3d91] dark:text-[#5ea1ff]">${(pipelineValue / 1000).toFixed(0)}k</strong>
						<span class="mt-1.5 block text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Nilai pipeline')}</span>
					</div>
				</div>

				<div class="mt-3 flex items-center justify-around rounded-2xl border border-[#0b3d91]/10 bg-gradient-to-r from-[#0b3d91] to-[#1e63d6] p-4 text-white shadow-lg">
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="200">
						<FaIcon icon="fa-solid fa-ship" class="text-3xl" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Laut')}</span>
					</div>
					<div class="h-8 w-px bg-white/20"></div>
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="300">
						<FaIcon icon="fa-solid fa-plane-departure" class="text-3xl" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Udara')}</span>
					</div>
					<div class="h-8 w-px bg-white/20"></div>
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="400">
						<FaIcon icon="fa-solid fa-boxes-stacked" class="text-3xl" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Kontainer')}</span>
					</div>
					<div class="h-8 w-px bg-white/20"></div>
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="500">
						<FaIcon icon="fa-solid fa-warehouse" class="text-3xl" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Gudang')}</span>
					</div>
				</div>
			</div>
		</section>

		<section class="grid grid-cols-2 gap-3 sm:grid-cols-4" data-aos="fade-up">
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<FaIcon icon="fa-solid fa-wheat-awn" class="text-2xl text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Komoditas Desa')}</span>
			</div>
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<FaIcon icon="fa-solid fa-shield-halved" class="text-2xl text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Kepatuhan Ekspor')}</span>
			</div>
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<FaIcon icon="fa-solid fa-handshake" class="text-2xl text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Koneksi Pembeli Global')}</span>
			</div>
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<FaIcon icon="fa-solid fa-truck" class="text-2xl text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Logistik & Pengiriman')}</span>
			</div>
</section>

	<!-- Pain Points & Solutions -->
	<section class="grid gap-6 rounded-3xl border border-[#0b3d91]/10 bg-gradient-to-br from-white to-[#f0f5ff] p-8 dark:border-white/10 dark:from-[#0a1730] dark:to-[#0c1f3d]" data-aos="fade-up">
		<div class="max-w-2xl">
			<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Hambatan & Solusi')}</Badge>
			<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Mengapa Komoditas Desa Sulit Tembus Pasar Ekspor?')}</h2>
		</div>
		<div class="grid gap-4 md:grid-cols-2">
			<div class="rounded-2xl border border-red-200 bg-red-50/60 p-6 dark:border-red-900/30 dark:bg-red-950/20" data-aos="fade-right">
				<h3 class="flex items-center gap-2 text-xl font-black tracking-tight text-red-600 dark:text-red-400">
					<FaIcon icon="fa-solid fa-circle-xmark" class="text-2xl shrink-0" /> {t('Hambatan Ekspor Desa')}
				</h3>
				<ul class="mt-4 grid gap-3">
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<FaIcon icon="fa-solid fa-circle-xmark" class="mt-0.5 shrink-0 text-lg text-red-500 dark:text-red-400" />
						{t('Komoditas berkualitas tapi tidak memiliki standar dan dokumentasi ekspor yang diakui pembeli internasional.')}</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<FaIcon icon="fa-solid fa-circle-xmark" class="mt-0.5 shrink-0 text-lg text-red-500 dark:text-red-400" />
						{t('Proses sertifikasi, karantina, dan dokumen ekspor sangat rumit dan memakan biaya besar tanpa panduan yang jelas.')}</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<FaIcon icon="fa-solid fa-circle-xmark" class="mt-0.5 shrink-0 text-lg text-red-500 dark:text-red-400" />
						{t('Ketergantungan pada calo dan broker — margin keuntungan petani sangat tipis karena panjangnya rantai perantara.')}</li>
				</ul>
			</div>
			<div class="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-6 dark:border-emerald-900/30 dark:bg-emerald-950/20" data-aos="fade-left">
				<h3 class="flex items-center gap-2 text-xl font-black tracking-tight text-emerald-600 dark:text-emerald-400">
					<FaIcon icon="fa-solid fa-circle-check" class="text-2xl shrink-0" /> {t('Solusi MauEkspor')}
				</h3>
				<ul class="mt-4 grid gap-3">
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<FaIcon icon="fa-solid fa-circle-check" class="mt-0.5 shrink-0 text-lg text-emerald-500 dark:text-emerald-400" />
						{t('Standarisasi komoditas otomatis: katalog terstruktur, HS code, profil ekspor, dan sertifikasi lengkap yang diakui buyer global.')}</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<FaIcon icon="fa-solid fa-circle-check" class="mt-0.5 shrink-0 text-lg text-emerald-500 dark:text-emerald-400" />
						{t('Panduan step-by-step untuk kepatuhan ekspor: dari karantina pertanian, sertifikasi HACCP/halal, hingga dokumen pengiriman.')}</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<FaIcon icon="fa-solid fa-circle-check" class="mt-0.5 shrink-0 text-lg text-emerald-500 dark:text-emerald-400" />
						{t('Koneksi langsung dengan buyer global — tanpa perantara. Petani dan UMKM desa menerima harga yang lebih adil dan margin lebih besar.')}</li>
				</ul>
			</div>
		</div>
	</section>

	<section id="features" class="grid gap-6 py-8">
			<div class="max-w-2xl" data-aos="fade-up">
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Fitur Rantai Pasok Ekspor')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Semua yang dibutuhkan untuk ekspor komoditas desa, dalam satu tempat.')}</h2>
				<p class="mt-3 leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">{t('Enam modul terintegrasi yang mengawal kesiapan ekspor komoditas desa — dari standardisasi produk hingga pembayaran diterima.')}</p>
			</div>
			<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
				{#each features as feature, index}
					<Card
						class="border-[#0b3d91]/10 transition-transform hover:-translate-y-1 dark:border-white/10"
						data-aos="fade-up"
						data-aos-delay={index * 80}
					>
						<CardHeader>
							<span class="grid size-10 place-items-center rounded-xl bg-[#0b3d91]/10 text-[#0b3d91] dark:bg-white/10 dark:text-[#5ea1ff]">
								<FaIcon icon={feature.fa} class="text-xl" />
							</span>
							<CardTitle class="text-xl tracking-tight">{t(feature.title)}</CardTitle>
						</CardHeader>
						<CardContent>
							<p class="leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">{t(feature.text)}</p>
						</CardContent>
					</Card>
				{/each}
			</div>
		</section>

		<section id="roles" class="grid gap-6 py-8">
			<div class="max-w-2xl" data-aos="fade-up">
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Ekosistem Rantai Pasok')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Satu platform untuk seluruh ekosistem ekspor desa.')}</h2>
				<p class="mt-3 leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
					{t('Dari petani dan kelompok tani hingga forwarder dan buyer global — setiap pemangku kepentingan mendapat peran dan akses yang relevan dalam rantai pasok ekspor.')}
				</p>
			</div>
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
				{#each roles as role, index}
					<Card
						class="border-[#0b3d91]/10 transition-transform hover:-translate-y-1 dark:border-white/10"
						data-aos="fade-up"
						data-aos-delay={index * 80}
					>
						<CardHeader>
							<FaIcon icon={role.fa} class="text-2xl text-[#0b3d91] dark:text-white" />
							<CardTitle class="mt-3 text-base">{t(role.title)}</CardTitle>
						</CardHeader>
						<CardContent>
							<p class="text-[13px] leading-relaxed text-muted-foreground">{t(role.text)}</p>
						</CardContent>
					</Card>
				{/each}
			</div>
</section>

	<!-- Use Cases -->
	<section class="grid gap-6 rounded-3xl border border-[#0b3d91]/10 bg-white p-8 dark:border-white/10 dark:bg-[#0a1730]" data-aos="fade-up">
		<div class="max-w-2xl">
			<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Kisah Sukses Ekspor Desa')}</Badge>
			<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Dari kopi Gayo, rempah Maluku, hingga kerajinan Jepara.')}</h2>
		</div>
		<div class="grid gap-4 md:grid-cols-3">
			<Card class="border-[#0b3d91]/10 dark:border-white/10" data-aos="fade-up">
				<CardContent class="grid gap-3 pt-(--card-spacing)">
					<Badge class="w-fit bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">{t('Komoditas Pertanian')}</Badge>
					<h4 class="text-lg font-bold">{t('Kelompok Tani Kopi Gayo')}</h4>
					<p class="text-sm leading-relaxed text-muted-foreground">{t('KSU Kopi Gayo Bener Meriah pertama kali ekspor langsung ke Jepang. MauEkspor memandu dari HS code, phytosanitary certificate, analisis pasar, hingga dokumen FOB — semuanya dalam 4 minggu.')}</p>
				</CardContent>
			</Card>
			<Card class="border-[#0b3d91]/10 dark:border-white/10" data-aos="fade-up" data-aos-delay="100">
				<CardContent class="grid gap-3 pt-(--card-spacing)">
					<Badge class="w-fit bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">{t('Produk Olahan Desa')}</Badge>
					<h4 class="text-lg font-bold">{t('BUMDes Produsen Rempah')}</h4>
					<p class="text-sm leading-relaxed text-muted-foreground">{t('BUMDes pengolah rempah Maluku menggunakan katalog digital, compliance check HACCP, dan buyer-matching untuk menjangkau importir di Eropa tanpa bergantung pada broker.')}</p>
				</CardContent>
			</Card>
			<Card class="border-[#0b3d91]/10 dark:border-white/10" data-aos="fade-up" data-aos-delay="200">
				<CardContent class="grid gap-3 pt-(--card-spacing)">
					<Badge class="w-fit bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">{t('Kerajinan & Anyaman')}</Badge>
					<h4 class="text-lg font-bold">{t('Pengrajin Rotan & Mebel')}</h4>
					<p class="text-sm leading-relaxed text-muted-foreground">{t('Pengrajin mebel Jepara memanfaatkan cek kepatuhan SVLK/CITES, costing FCL, dan rekomendasi forwarder untuk memenangkan order FOB kompetitif dari buyer Australia dan Eropa.')}</p>
				</CardContent>
			</Card>
		</div>
	</section>

	<section id="workflow" class="grid gap-6 rounded-3xl bg-gradient-to-br from-[#0b3d91] to-[#123b7a] p-8 text-white">
			<div class="max-w-2xl" data-aos="fade-up">
				<Badge variant="outline" class="border-white/30 text-white">{t('Alur Kesiapan Ekspor')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight md:text-5xl">{t('Tiga langkah dari komoditas desa ke pasar global.')}</h2>
			</div>
			<div class="grid gap-4 md:grid-cols-3">
				{#each steps as step, index}
					<Card
						class="border-white/15 bg-white/10 text-white transition-transform hover:-translate-y-1"
						data-aos="fade-up"
						data-aos-delay={index * 100}
					>
						<CardHeader>
							<div class="flex items-center justify-between">
								<span class="text-[13px] font-black uppercase tracking-[0.1em] text-white/70">{step.n}</span>
								<FaIcon icon={step.fa} class="text-2xl text-white/80" />
							</div>
							<CardTitle class="text-2xl tracking-tight text-white">{t(step.title)}</CardTitle>
						</CardHeader>
						<CardContent>
							<p class="leading-relaxed text-white/75">{t(step.text)}</p>
						</CardContent>
					</Card>
				{/each}
			</div>
		</section>

		<section id="testimonials" class="grid gap-6 py-8">
			<div class="max-w-2xl" data-aos="fade-up">
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Cerita Sukses Ekspor')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Petani dan UMKM desa yang berhasil menembus pasar global.')}</h2>
			</div>
			<div class="grid gap-4 md:grid-cols-3">
				{#each testimonials as item, index}
					<Card
						class="border-[#0b3d91]/10 transition-transform hover:-translate-y-1 dark:border-white/10"
						data-aos="fade-up"
						data-aos-delay={index * 100}
					>
						<CardContent class="pt-(--card-spacing)">
							<figure class="m-0 grid gap-4">
								<blockquote class="m-0 text-[17px] font-semibold leading-relaxed">"{t(item.quote)}"</blockquote>
								<figcaption class="grid gap-1">
									<strong>{item.name}</strong>
									<span class="text-[13px] text-[#0b1d3a]/60 dark:text-white/60">{t(item.role)}</span>
								</figcaption>
							</figure>
						</CardContent>
					</Card>
				{/each}
			</div>
</section>

	<!-- Vision & Mission -->
	<section class="grid gap-6 rounded-3xl bg-gradient-to-br from-[#0a1f4a] to-[#0c3060] p-8 text-white shadow-sm dark:from-[#040d1f] dark:to-[#0a1730]" data-aos="fade-up">
		<div class="grid gap-6 md:grid-cols-2">
			<div>
				<Badge variant="outline" class="border-white/30 text-white">{t('Visi')}</Badge>
				<h3 class="mt-4 font-display text-3xl font-black tracking-tight md:text-4xl">{t('Menjadi Jembatan Komoditas Desa ke Rantai Pasok Ekspor Global')}</h3>
				<p class="mt-4 leading-relaxed text-white/75">
					{t('Kami percaya bahwa kualitas komoditas Indonesia dari pelosok desa layak bersaing di pasar global. MauEkspor hadir untuk memastikan setiap petani, pengrajin, dan UMKM desa memiliki akses yang setara terhadap rantai pasok ekspor internasional — tanpa ketergantungan pada broker dan perantara.')}</p>
			</div>
			<div class="grid content-start gap-4">
				<Badge variant="outline" class="border-white/30 text-white">{t('Pilar Rantai Pasok Ekspor')}</Badge>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<FaIcon icon="fa-solid fa-seedling" class="text-2xl text-emerald-400" />
					<h4 class="mt-2 text-lg font-bold">{t('Kesiapan Produk')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Bantu setiap komoditas desa memenuhi standar mutu internasional — HS code, spesifikasi, kemasan, dan sertifikasi yang diakui buyer global.')}</p>
				</div>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<FaIcon icon="fa-solid fa-rocket" class="text-2xl text-blue-400" />
					<h4 class="mt-2 text-lg font-bold">{t('Akses Pasar Global')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Koneksikan UMKM dan kelompok tani desa langsung dengan buyer internasional — tanpa ketergantungan pada perantara, margin lebih besar untuk petani.')}</p>
				</div>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<FaIcon icon="fa-solid fa-briefcase" class="text-2xl text-amber-400" />
					<h4 class="mt-2 text-lg font-bold">{t('Nilai Tambah Ekonomi')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Tingkatkan nilai jual komoditas desa melalui standarisasi, branding, dan akses ke rantai pasok premium global yang memberikan harga lebih adil.')}</p>
				</div>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<FaIcon icon="fa-solid fa-users" class="text-2xl text-purple-400" />
					<h4 class="mt-2 text-lg font-bold">{t('Ekosistem Berkelanjutan')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Bangun ekosistem kolaboratif antara petani, koperasi, forwarder, dan buyer untuk rantai pasok ekspor yang adil dan berkelanjutan.')}</p>
				</div>
			</div>
		</div>
	</section>

	<section
		class="flex flex-wrap items-center justify-between gap-6 rounded-3xl border border-[#0b3d91]/10 bg-gradient-to-br from-white to-[#dbe9ff] p-8 dark:border-white/10 dark:from-[#0a1730] dark:to-[#0c2450]"
			data-aos="zoom-in"
		>
			<div>
				<h2 class="font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{t('Siap Ekspor Komoditas Desa ke Pasar Global?')}</h2>
				<p class="mt-3 leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">{t('Bergabunglah dengan petani, pengrajin, dan BUMDes yang telah menggunakan MauEkspor untuk mempersiapkan komoditas unggulan mereka memasuki rantai pasok ekspor internasional.')}</p>
			</div>
			<div class="flex flex-wrap gap-3">
				<Button size="lg" href="/register" class="h-11 bg-[#0b3d91] px-6 text-base text-white hover:bg-[#0b3d91]/85">{t('Mulai Persiapan Ekspor')}</Button>
				<Button variant="outline" size="lg" href="/login" class="h-11 border-[#0b3d91]/20 px-6 text-base">{t('Masuk')}</Button>
			</div>
		</section>

		<footer class="flex flex-wrap items-center justify-between gap-4 px-2 py-6 text-sm text-[#0b1d3a]/60 dark:text-white/60">
			<a href="/" class="inline-flex items-center gap-1.5">
				<Logo variant="logo" class="!h-8" />
				<span class="font-display text-xl font-black tracking-tight text-[#0b1d3a] dark:text-white">MauEkspor</span>
			</a>
			<p class="max-w-xl">{t('Platform rantai pasok ekspor komoditas desa: membantu petani, pengrajin, dan UMKM desa Indonesia menembus pasar global dengan standar ekspor yang benar.')}</p>
			<nav class="flex gap-4 text-sm font-bold text-[#0b1d3a]/60 dark:text-white/60" aria-label="Footer">
				<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href="/about">{t('Tentang')}</a>
				<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href="/login">{t('Masuk')}</a>
				<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href="/register">{t('Daftar')}</a>
			</nav>
		</footer>
	</div>
</div>
