<script lang="ts">
	import AosInit from '$lib/components/AosInit.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import { products, projects, buyers, exportAnalyses } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';

	import ShipIcon from '@lucide/svelte/icons/ship';
	import PlaneTakeoffIcon from '@lucide/svelte/icons/plane-takeoff';
	import ContainerIcon from '@lucide/svelte/icons/container';
	import PackageSearchIcon from '@lucide/svelte/icons/package-search';
	import WarehouseIcon from '@lucide/svelte/icons/warehouse';
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import AnchorIcon from '@lucide/svelte/icons/anchor';
	import FactoryIcon from '@lucide/svelte/icons/factory';
	import TruckIcon from '@lucide/svelte/icons/truck';
	import BoxesIcon from '@lucide/svelte/icons/boxes';
	import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
	import ChartLineIcon from '@lucide/svelte/icons/chart-line';
	import ReceiptTextIcon from '@lucide/svelte/icons/receipt-text';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import MenuIcon from '@lucide/svelte/icons/menu';

	let mobileNavOpen = $state(false);

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
		{ icon: PackageSearchIcon, title: 'Product readiness', text: 'Structured specs, packaging, certificates, and HS candidates that every export step reuses.' },
		{ icon: ChartLineIcon, title: 'Market intelligence', text: 'HS classification, duties, restrictions, and regulation recommendations per destination.' },
		{ icon: ShieldCheckIcon, title: 'Compliance evidence', text: 'Requirement-to-evidence tracking with confidence scores and human review gates.' },
		{ icon: ReceiptTextIcon, title: 'Commercial execution', text: 'RFQ, quotation, costing, orders, and payments in one consistent pipeline.' },
		{ icon: TruckIcon, title: 'Logistics visibility', text: 'Forwarder rates, lanes, booking milestones, and shipment exceptions at a glance.' },
		{ icon: FileTextIcon, title: 'Document control', text: 'Validated commercial invoices, packing lists, and certificates with cross-field checks.' }
	];

	const steps = [
		{ n: '01', icon: BoxesIcon, title: 'Capture', text: 'Complete business profile and structured product data.' },
		{ n: '02', icon: GlobeIcon, title: 'Analyze', text: 'Run market analysis for HS, duties, and regulations.' },
		{ n: '03', icon: ShipIcon, title: 'Execute', text: 'Quote, book freight, prepare documents, and track payment.' }
	];

	const roles = [
		{ icon: FactoryIcon, title: 'Exporter / UMKM', text: 'Siapkan produk, analisis pasar & kepatuhan, bangun katalog, dan kelola pipeline penawaran hingga pengiriman.' },
		{ icon: PackageSearchIcon, title: 'Buyer', text: 'Kirim kebutuhan (RFQ), lihat katalog UMKM yang cocok, dan hubungi langsung via WhatsApp.' },
		{ icon: ShipIcon, title: 'Forwarder', text: 'Jaga profil, dapatkan review, dan muncul di rekomendasi rute untuk mendapatkan kuotasi baru.' },
		{ icon: ShieldCheckIcon, title: 'Customs Broker', text: 'Pantau kepatuhan, bukti dokumen, dan status kepabeanan dalam satu workspace.' },
		{ icon: ReceiptTextIcon, title: 'Finance', text: 'Lacak pembayaran, milestone deposit, dan tagihan di sepanjang siklus order.' }
	];

	const testimonials = [
		{ quote: 'We went from scattered spreadsheets to a single trade workspace for coffee export to Japan.', name: 'Rizal Fahmi', role: 'PT Kopi Gayo Nusantara' },
		{ quote: 'Compliance evidence tracking finally makes sense for our EU furniture program.', name: 'Sinta Lestari', role: 'Medan Crispy Foods' },
		{ quote: 'Forwarder lanes and quote speed comparison saved us days on booking decisions.', name: 'Ayu Pratama', role: 'Operations Lead' }
	];
</script>

<svelte:head>
	<title>MauEkspor | {t('Workspace Ekspor-Impor')}</title>
	<meta
		name="description"
		content="One workspace from product readiness to shipment delivery. Indonesian exporters plan, analyze, quote, document, and ship with confidence."
	/>
</svelte:head>

<AosInit />

<div class="landing-font min-h-svh bg-[#f4f8ff] text-[#0b1d3a] dark:bg-[#040d1f] dark:text-[#eaf1ff]">
	<div class="mx-auto grid max-w-7xl gap-6 p-4 sm:p-5">
		<header
			class="sticky top-3.5 z-30 flex flex-wrap items-center justify-between gap-4 rounded-full border border-[#0b3d91]/10 bg-white/80 p-3 pl-5 shadow-sm backdrop-blur-xl dark:border-white/10 dark:bg-[#0a1730]/80"
		>
			<Logo variant="landscape" href="/" class="justify-center" />

			<nav class="hidden gap-6 text-sm font-bold text-[#0b1d3a]/70 md:flex dark:text-white/70" aria-label={t('Navigasi laman')}>
				{#each navLinks as link}
					<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href={link.href}>{t(link.label)}</a>
				{/each}
			</nav>

			<div class="hidden items-center gap-2 md:flex">
				<ThemeToggle />
				<Button variant="outline" href="/login" class="border-[#0b3d91]/20">{t('Masuk')}</Button>
				<Button href="/register" class="bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">{t('Mulai Ekspor')}</Button>
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
							<Sheet.Title class="flex items-center gap-2"><Logo variant="landscape" class="!h-7" /></Sheet.Title>
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
							<Button href="/login" variant="outline" class="w-full border-[#0b3d91]/20" onclick={() => (mobileNavOpen = false)}>{t('Masuk')}</Button>
							<Button href="/register" class="w-full bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85" onclick={() => (mobileNavOpen = false)}>{t('Mulai Ekspor')}</Button>
						</Sheet.Footer>
					</Sheet.Content>
				</Sheet.Root>
			</div>
		</header>

		<section class="relative grid items-center gap-8 overflow-hidden rounded-3xl border border-[#0b3d91]/10 bg-gradient-to-br from-white via-[#eaf2ff] to-[#dbe9ff] p-6 shadow-sm md:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] md:p-12 dark:border-white/10 dark:from-[#0a1730] dark:via-[#0b1f42] dark:to-[#0c2450]">
			<GlobeIcon class="pointer-events-none absolute -right-16 -top-16 size-72 text-[#0b3d91]/5 dark:text-white/5" />

			<div data-aos="fade-right">
				<Badge variant="secondary" class="bg-[#0b3d91]/10 text-[#0b3d91] dark:bg-white/10 dark:text-white">
					<AnchorIcon class="size-3.5" />
					{t('Dibangun untuk eksportir Indonesia')}
				</Badge>
				<h1 class="mt-4 font-display text-5xl font-black leading-[0.95] tracking-tight text-[#0b1d3a] sm:text-6xl md:text-7xl dark:text-white">
					{t('Dari kesiapan produk hingga')} <span class="text-[#1e63d6] dark:text-[#5ea1ff]">{t('kapal berlayar')}</span>.
				</h1>
				<p class="mt-5 max-w-2xl text-lg leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
					{t('MauEkspor menyatukan data produk, klasifikasi HS, bukti kepatuhan, penawaran, dokumen, dan milestone kargo — agar tim ekspor-impor Anda berlayar dengan percaya diri.')}
				</p>
				<div class="mt-7 flex flex-wrap gap-3">
					<Button size="lg" href="/register" class="h-11 bg-[#0b3d91] px-6 text-base text-white hover:bg-[#0b3d91]/85">
						<PlaneTakeoffIcon class="size-4" />
						Mulai Ekspor
					</Button>
					<Button variant="outline" size="lg" href="/dashboard" class="h-11 border-[#0b3d91]/20 px-6 text-base">{t('Jelajahi Workspace')}</Button>
				</div>
				<div class="mt-6 flex flex-wrap gap-x-5 gap-y-2 text-[13px] font-bold text-[#0b1d3a]/60 dark:text-white/60">
					<span>{t('Autentikasi siap cookie')}</span>
					<span>{t('Akses berbasis peran')}</span>
					<span>{t('Tindakan tertelusur audit')}</span>
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
						<ShipIcon class="size-7" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Laut')}</span>
					</div>
					<div class="h-8 w-px bg-white/20"></div>
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="300">
						<PlaneTakeoffIcon class="size-7" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Udara')}</span>
					</div>
					<div class="h-8 w-px bg-white/20"></div>
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="400">
						<ContainerIcon class="size-7" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Kontainer')}</span>
					</div>
					<div class="h-8 w-px bg-white/20"></div>
					<div class="flex flex-col items-center gap-1.5" data-aos="zoom-in" data-aos-delay="500">
						<WarehouseIcon class="size-7" />
						<span class="text-[11px] font-bold uppercase tracking-wide opacity-80">{t('Gudang')}</span>
					</div>
				</div>
			</div>
		</section>

		<section class="grid grid-cols-2 gap-3 sm:grid-cols-4" data-aos="fade-up">
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<FactoryIcon class="size-6 text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Produsen UMKM')}</span>
			</div>
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<BoxesIcon class="size-6 text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Barang Ekspor')}</span>
			</div>
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<TruckIcon class="size-6 text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Logistik Darat')}</span>
			</div>
			<div class="flex flex-col items-center gap-2 rounded-2xl border border-[#0b3d91]/10 bg-white p-4 text-center dark:border-white/10 dark:bg-[#0a1730]">
				<GlobeIcon class="size-6 text-[#1e63d6]" />
				<span class="text-xs font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Pasar Global')}</span>
			</div>
</section>

	<!-- Pain Points & Solutions -->
	<section class="grid gap-6 rounded-3xl border border-[#0b3d91]/10 bg-gradient-to-br from-white to-[#f0f5ff] p-8 dark:border-white/10 dark:from-[#0a1730] dark:to-[#0c1f3d]" data-aos="fade-up">
		<div class="max-w-2xl">
			<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Masalah & Solusi')}</Badge>
			<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Ekspor tidak harus serumit itu.')}</h2>
		</div>
		<div class="grid gap-4 md:grid-cols-2">
			<div class="rounded-2xl border border-red-200 bg-red-50/60 p-6 dark:border-red-900/30 dark:bg-red-950/20" data-aos="fade-right">
				<h3 class="flex items-center gap-2 text-xl font-black tracking-tight text-red-600 dark:text-red-400">
					<span class="text-2xl">✗</span> {t('Masalah')}
				</h3>
				<ul class="mt-4 grid gap-3">
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<span class="mt-0.5 size-5 shrink-0 rounded-full bg-red-100 text-center text-xs leading-5 text-red-600 dark:bg-red-900/30 dark:text-red-400">✗</span>
						{t('Data produk tercecer di spreadsheet, chat, dan email — tidak ada satu sumber kebenaran.')}
					</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<span class="mt-0.5 size-5 shrink-0 rounded-full bg-red-100 text-center text-xs leading-5 text-red-600 dark:bg-red-900/30 dark:text-red-400">✗</span>
						{t('Analisis pasar dan kepatuhan memakan waktu berminggu-minggu karena riset manual per negara.')}
					</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<span class="mt-0.5 size-5 shrink-0 rounded-full bg-red-100 text-center text-xs leading-5 text-red-600 dark:bg-red-900/30 dark:text-red-400">✗</span>
						{t('Penawaran harga tidak konsisten — kalkulasi EXW/FOB/CIF sering salah dan dokumen tidak terintegrasi.')}
					</li>
				</ul>
			</div>
			<div class="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-6 dark:border-emerald-900/30 dark:bg-emerald-950/20" data-aos="fade-left">
				<h3 class="flex items-center gap-2 text-xl font-black tracking-tight text-emerald-600 dark:text-emerald-400">
					<span class="text-2xl">✓</span> {t('Solusi MauEkspor')}
				</h3>
				<ul class="mt-4 grid gap-3">
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<span class="mt-0.5 size-5 shrink-0 rounded-full bg-emerald-100 text-center text-xs leading-5 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400">✓</span>
						{t('Satu workspace terstruktur: produk, katalog, analisis, dan dokumen dalam satu tempat sinkron.')}
					</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<span class="mt-0.5 size-5 shrink-0 rounded-full bg-emerald-100 text-center text-xs leading-5 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400">✓</span>
						{t('Analisis kepatuhan AI dengan snapshot produk, perbandingan negara, dan rekomendasi 10-bagian per tujuan.')}
					</li>
					<li class="flex items-start gap-3 text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
						<span class="mt-0.5 size-5 shrink-0 rounded-full bg-emerald-100 text-center text-xs leading-5 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400">✓</span>
						{t('Costing EXW/FOB/CIF otomatis, PDF siap kirim, dan kalkulasi kapasitas kontainer dari dimensi produk nyata.')}
					</li>
				</ul>
			</div>
		</div>
	</section>

	<section id="features" class="grid gap-6 py-8">
			<div class="max-w-2xl" data-aos="fade-up">
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Kapabilitas')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Semua yang tim ekspor butuhkan, dalam satu tempat.')}</h2>
				<p class="mt-3 leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">{t('Enam modul kerja yang berbagi data yang sama dan menggerakkan proyek dari ide hingga kargo terkirim.')}</p>
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
								<feature.icon class="size-5" />
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
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Dibuat untuk')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Satu workspace untuk semua peran dagang.')}</h2>
				<p class="mt-3 leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
					{t('Dari eksportir hingga finance, setiap peran mendapat tampilan yang relevan dengan akses sesuai perannya.')}
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
							<role.icon class="size-6 text-[#0b3d91] dark:text-white" />
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
			<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Studi Kasus')}</Badge>
			<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Dari kopi, furnitur, hingga produk olahan.')}</h2>
		</div>
		<div class="grid gap-4 md:grid-cols-3">
			<Card class="border-[#0b3d91]/10 dark:border-white/10" data-aos="fade-up">
				<CardContent class="grid gap-3 pt-(--card-spacing)">
					<Badge class="w-fit bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">{t('Pertama Kali')}</Badge>
					<h4 class="text-lg font-bold">{t('Eksportir Pemula')}</h4>
					<p class="text-sm leading-relaxed text-muted-foreground">{t('UMKM kopi Gayo pertama kali ekspor ke Jepang. MauEkspor memandu dari HS code, analisis pasar, hingga dokumen pengiriman — semuanya dalam 3 minggu.')}</p>
				</CardContent>
			</Card>
			<Card class="border-[#0b3d91]/10 dark:border-white/10" data-aos="fade-up" data-aos-delay="100">
				<CardContent class="grid gap-3 pt-(--card-spacing)">
					<Badge class="w-fit bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">{t('Skala UKM')}</Badge>
					<h4 class="text-lg font-bold">{t('Produsen Makanan Olahan')}</h4>
					<p class="text-sm leading-relaxed text-muted-foreground">{t('Produsen keripik singkong menggunakan katalog digital dan buyer-request matching untuk menjangkau buyer di Eropa dan Timur Tengah tanpa perantara.')}</p>
				</CardContent>
			</Card>
			<Card class="border-[#0b3d91]/10 dark:border-white/10" data-aos="fade-up" data-aos-delay="200">
				<CardContent class="grid gap-3 pt-(--card-spacing)">
					<Badge class="w-fit bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">{t('Kerajinan & Mebel')}</Badge>
					<h4 class="text-lg font-bold">{t('Eksportir Furnitur')}</h4>
					<p class="text-sm leading-relaxed text-muted-foreground">{t('Eksportir mebel Jepara memanfaatkan costing container dan forwarder recommendations untuk memberikan penawaran FOB yang kompetitif ke buyer Australia.')}</p>
				</CardContent>
			</Card>
		</div>
	</section>

	<section id="workflow" class="grid gap-6 rounded-3xl bg-gradient-to-br from-[#0b3d91] to-[#123b7a] p-8 text-white">
			<div class="max-w-2xl" data-aos="fade-up">
				<Badge variant="outline" class="border-white/30 text-white">{t('Cara Kerja')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight md:text-5xl">{t('Tiga langkah dari ide hingga invoice.')}</h2>
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
								<step.icon class="size-6 text-white/80" />
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
				<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{t('Cerita')}</Badge>
				<h2 class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Tim yang berlayar lebih jauh dengan MauEkspor.')}</h2>
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
				<h3 class="mt-4 font-display text-3xl font-black tracking-tight md:text-4xl">{t('Menyederhanakan ekspor untuk setiap UMKM Indonesia.')}</h3>
				<p class="mt-4 leading-relaxed text-white/75">
					{t('Kami percaya bahwa potensi ekspor UMKM Indonesia terhambat oleh kompleksitas administrasi, bukan oleh kualitas produk. MauEkspor hadir sebagai sistem operasi dagang yang menyatukan data, analisis, dan eksekusi dalam satu workspace yang terstruktur.')}
				</p>
			</div>
			<div class="grid content-start gap-4">
				<Badge variant="outline" class="border-white/30 text-white">{t('Misi')}</Badge>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<span class="text-2xl">🎯</span>
					<h4 class="mt-2 text-lg font-bold">{t('Kesiapan Produk')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Data produk terstruktur, kode HS otomatis, dan enrichment berbasis AI sebagai fondasi setiap alur ekspor.')}</p>
				</div>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<span class="text-2xl">🔍</span>
					<h4 class="mt-2 text-lg font-bold">{t('Analisis Cerdas')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Market intelligence, compliance check, dan perbandingan negara dalam hitungan detik — bukan minggu.')}</p>
				</div>
				<div class="rounded-xl border border-white/15 bg-white/10 p-5">
					<span class="text-2xl">🚀</span>
					<h4 class="mt-2 text-lg font-bold">{t('Eksekusi Terpadu')}</h4>
					<p class="mt-1 text-sm leading-relaxed text-white/70">{t('Dari costing dan katalog digital hingga dokumen dan milestone pengiriman — semua terintegrasi.')}</p>
				</div>
			</div>
		</div>
	</section>

	<section
		class="flex flex-wrap items-center justify-between gap-6 rounded-3xl border border-[#0b3d91]/10 bg-gradient-to-br from-white to-[#dbe9ff] p-8 dark:border-white/10 dark:from-[#0a1730] dark:to-[#0c2450]"
			data-aos="zoom-in"
		>
			<div>
				<h2 class="font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{t('Siap ekspor dengan percaya diri?')}</h2>
				<p class="mt-3 leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">{t('Siapkan workspace Anda dalam beberapa menit dan mulai proyek dagang pertama Anda.')}</p>
			</div>
			<div class="flex flex-wrap gap-3">
				<Button size="lg" href="/register" class="h-11 bg-[#0b3d91] px-6 text-base text-white hover:bg-[#0b3d91]/85">{t('Buat Workspace Anda')}</Button>
				<Button variant="outline" size="lg" href="/login" class="h-11 border-[#0b3d91]/20 px-6 text-base">{t('Masuk')}</Button>
			</div>
		</section>

		<footer class="flex flex-wrap items-center justify-between gap-4 px-2 py-6 text-sm text-[#0b1d3a]/60 dark:text-white/60">
			<Logo variant="landscape" class="justify-center" />
			<p class="max-w-xl">{t('Satu workspace dari kesiapan produk hingga pengiriman kargo — dibangun untuk eksportir Indonesia.')}</p>
			<nav class="flex gap-4 text-sm font-bold text-[#0b1d3a]/60 dark:text-white/60" aria-label="Footer">
				<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href="/about">{t('Tentang')}</a>
				<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href="/login">{t('Masuk')}</a>
				<a class="transition-colors hover:text-[#0b3d91] dark:hover:text-white" href="/register">{t('Daftar')}</a>
			</nav>
		</footer>
	</div>
</div>
