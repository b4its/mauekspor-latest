<script lang="ts">
	import { page } from '$app/state';
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { getCountry, type Country } from '$lib/api/export-analysis';
	import { seedCountries } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';

	import GlobeIcon from '@lucide/svelte/icons/globe';
	import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
	import ShipIcon from '@lucide/svelte/icons/ship';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import SearchIcon from '@lucide/svelte/icons/search';
	import BanknoteIcon from '@lucide/svelte/icons/banknote';
	import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
	import LandmarkIcon from '@lucide/svelte/icons/landmark';
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
	import AlertTriangleIcon from '@lucide/svelte/icons/alert-triangle';

	const code = $derived((page.params.code ?? 'ID').toUpperCase());

	let country = $state<Country | null>(null);
	let loading = $state(true);
	let error = $state('');

	let activeTab = $state<'impor' | 'ekspor' | 'dokumen'>('impor');

	$effect(() => {
		loading = true;
		error = '';
		activeTab = 'impor';
		getCountry(code)
			.then((res) => (country = res.data))
			.catch(() => {
				const seed = seedCountries.find((c) => c.country_code === code);
				if (seed) country = seed;
				else error = t('Gagal memuat data negara.');
			})
			.finally(() => (loading = false));
	});

	const riskTone = {
		Low: 'secondary',
		Moderate: 'outline',
		Elevated: 'default',
		High: 'destructive',
	} as const;

	function flagEmoji(code: string) {
		return String.fromCodePoint(...[...code.toUpperCase()].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65));
	}
</script>

<svelte:head>
	<title>{country?.country_name ?? code} | {t('Regulasi Negara')} | MauEkspor</title>
</svelte:head>

<AppShell title={country?.country_name ?? code} eyebrow={t('Regulasi ekspor & impor negara')}>
	<Button variant="outline" size="sm" href="/countries" class="-mb-2">
		<ArrowLeftIcon class="size-3.5" />
		{t('Semua negara')}
	</Button>

	{#if loading}
		<p class="py-16 text-center text-sm text-muted-foreground">{t('Memuat...')}</p>
	{:else if error}
		<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-bold text-destructive">{error}</p>
		<Button href="/countries" variant="outline" size="sm" class="mt-3">
			<ArrowLeftIcon class="size-3.5" />
			{t('Kembali')}
		</Button>
	{:else if country}
		<Card class="p-6 md:p-8">
			<div class="flex flex-wrap items-start justify-between gap-6">
				<div class="flex min-w-0 items-start gap-4">
					<span class="grid size-14 place-items-center rounded-2xl bg-secondary text-4xl">{flagEmoji(country.country_code)}</span>
					<div class="min-w-0">
						<div class="flex flex-wrap items-center gap-2">
							<Badge variant="outline" class="border-[#0b3d91]/20 text-[#0b3d91] dark:text-white">{country.customs_system || t('Sistem nasional')}</Badge>
							{#if country.risk_level}
								<Badge variant={riskTone[country.risk_level as keyof typeof riskTone] ?? 'outline'}>{t(country.risk_level)} {t('risk')}</Badge>
							{/if}
							{#if !country.has_details}
								<Badge variant="secondary">{t('Data umum / regional')}</Badge>
							{/if}
						</div>
						<h1 class="mt-2 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{country.country_name}</h1>
						<p class="mt-1 text-sm font-bold text-muted-foreground">
							{country.country_code} · {country.region}{country.subregion ? ` · ${country.subregion}` : ''}
							{#if country.currency} · {country.currency}{/if}
						</p>
					</div>
				</div>
				<div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
					<span class="font-bold text-muted-foreground">{t('Region')}</span>
					<span class="font-semibold">{country.region}</span>
					<span class="font-bold text-muted-foreground">{t('Verifikasi data')}</span>
					<span class="font-semibold">{country.verified || '2026-08-15'}</span>
					<span class="font-bold text-muted-foreground">{t('Klasifikasi')}</span>
					<span class="font-semibold">HS {country.customs_system_info?.nomenclature || t('nasional')}</span>
				</div>
			</div>

			{#if country.data_note}
				<p class="mt-5 rounded-xl border border-[#0b3d91]/20 bg-[#0b3d91]/5 px-4 py-3 text-[13px] leading-relaxed text-[#0b1d3a]/80 dark:border-white/10 dark:bg-white/5 dark:text-white/80">
					{country.data_note}
				</p>
			{/if}

			{#if country.sanctions_warning}
				<p class="mt-3 flex items-start gap-2 rounded-xl border border-amber-400/40 bg-amber-50 px-4 py-3 text-[13px] font-semibold leading-relaxed text-amber-800 dark:bg-amber-950/30 dark:text-amber-300">
					<AlertTriangleIcon class="mt-0.5 size-4 shrink-0" />
					{country.sanctions_warning}
				</p>
			{/if}

			<div class="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
				<div class="min-w-0">
					{#if country.tariff || country.customs || country.checks || country.fta}
						<Card class="rounded-xl bg-secondary/60">
							<CardHeader class="p-4 pb-2">
								<CardTitle class="text-base">{t('Ringkasan kepabeanan')}</CardTitle>
							</CardHeader>
							<CardContent class="grid gap-3 p-0">
								{#if country.customs}
									<p class="px-4 text-sm leading-relaxed"><strong>{t('Sistem')}:</strong> {country.customs}</p>
								{/if}
								{#if country.tariff}
									<p class="px-4 text-sm leading-relaxed"><strong>{t('Tarif & pajak')}:</strong> {country.tariff}</p>
								{/if}
								{#if country.checks}
									<p class="px-4 text-sm leading-relaxed"><strong>{t('Urutan pengecekan')}:</strong> {country.checks}</p>
								{/if}
								{#if country.fta}
									<p class="px-4 text-sm leading-relaxed"><strong>{t('Perjanjian dagang')}:</strong> {country.fta}</p>
								{/if}
								{#if country.customs_system_info?.tariffs}
									<span class="px-4 text-sm leading-relaxed"><strong>{t('Tarif sistem')}:</strong> {String(country.customs_system_info.tariffs)}</span>
								{/if}
								{#if country.customs_system_info?.note}
									<span class="px-4 pb-3 pt-0 text-[13px] leading-snug text-muted-foreground">{String(country.customs_system_info.note)}</span>
								{/if}
							</CardContent>
						</Card>
					{/if}

					<div class="mt-5 flex flex-wrap gap-2">
						<Button size="sm" variant={activeTab === 'impor' ? 'default' : 'outline'} onclick={() => (activeTab = 'impor')}>
							<SearchIcon class="size-3.5" />
							{t('Aturan impor')}
						</Button>
						<Button size="sm" variant={activeTab === 'ekspor' ? 'default' : 'outline'} onclick={() => (activeTab = 'ekspor')}>
							<ShipIcon class="size-3.5" />
							{t('Aturan ekspor')}
						</Button>
						<Button size="sm" variant={activeTab === 'dokumen' ? 'default' : 'outline'} onclick={() => (activeTab = 'dokumen')}>
							<FileTextIcon class="size-3.5" />
							{t('Dokumen & pajak')}
						</Button>
					</div>

					{#if activeTab === 'impor'}
						<Card class="mt-4">
							<CardContent>
								{#if country.import_rules && country.import_rules.length > 0}
									<ul class="grid gap-3">
										{#each country.import_rules as rule, i}
											<li class="flex items-start gap-3 text-sm leading-relaxed">
												<span class="mt-0.5 grid size-5 shrink-0 place-items-center rounded-full bg-[#0b3d91]/10 text-[11px] font-black text-[#0b3d91] dark:bg-white/10 dark:text-white">{i + 1}</span>
												<span>{rule}</span>
											</li>
										{/each}
									</ul>
								{:else}
									<p class="text-sm text-muted-foreground">{t('Belum ada aturan impor yang dirinci.')}</p>
								{/if}
							</CardContent>
						</Card>
					{:else if activeTab === 'ekspor'}
						<Card class="mt-4">
							<CardContent>
								{#if country.export_rules && country.export_rules.length > 0}
									<ul class="grid gap-3">
										{#each country.export_rules as rule, i}
											<li class="flex items-start gap-3 text-sm leading-relaxed">
												<span class="mt-0.5 grid size-5 shrink-0 place-items-center rounded-full bg-[#0b3d91]/10 text-[11px] font-black text-[#0b3d91] dark:bg-white/10 dark:text-white">{i + 1}</span>
												<span>{rule}</span>
											</li>
										{/each}
									</ul>
								{:else}
									<p class="text-sm text-muted-foreground">{t('Belum ada aturan ekspor yang dirinci.')}</p>
								{/if}
							</CardContent>
						</Card>
					{:else}
						<Card class="mt-4">
							<CardContent class="grid gap-5">
								<div>
									<h3 class="flex items-center gap-2 text-sm font-bold">
										<BanknoteIcon class="size-4 text-[#0b3d91]" />
										{t('Pajak impor & domestik')}
									</h3>
									{#if country.tariff}
										<p class="mt-2 text-sm leading-relaxed">{country.tariff}</p>
									{:else}
										<p class="mt-2 text-sm text-muted-foreground">{t('Belum dirinci.')}</p>
									{/if}
								</div>
								<div>
									<h3 class="flex items-center gap-2 text-sm font-bold">
										<FileTextIcon class="size-4 text-[#0b3d91]" />
										{t('Dokumen yang dibutuhkan')}
									</h3>
									{#if country.documents && country.documents.length > 0}
										<ul class="mt-2 grid gap-2">
											{#each country.documents as doc}
												<li class="flex items-start gap-2 text-sm leading-relaxed">
												<span class="mt-1.5 size-1.5 shrink-0 rounded-full bg-[#0b3d91]"></span>
												<span>{doc}</span>
												</li>
											{/each}
										</ul>
									{:else}
										<p class="mt-2 text-sm text-muted-foreground">{t('Belum dirinci.')}</p>
									{/if}
								</div>
							</CardContent>
						</Card>
					{/if}

					{#if country.regulations && country.regulations.length > 0}
						<Card class="mt-4">
							<CardHeader class="p-4 pb-2">
								<CardTitle class="flex items-center gap-2 text-base">
									<ShieldCheckIcon class="size-4 text-[#0b3d91]" />
									{t('Aturan produk per kategori')}
								</CardTitle>
							</CardHeader>
							<CardContent class="grid gap-3">
								{#each Object.entries(country.regulations_by_category ?? {}) as [category, rules]}
									<div class="rounded-xl border border-border p-4">
										<Badge variant="outline">{category}</Badge>
										{#each rules as reg}
											<div class="mt-2 grid gap-1 text-[13px] leading-snug">
												{#if reg.description_rule}<p class="font-medium">{reg.description_rule}</p>{/if}
												{#if reg.required_specs}<p><strong>{t('Wajib')}:</strong> {reg.required_specs}</p>{/if}
												{#if reg.forbidden_keywords}<p class="text-destructive"><strong>{t('Dilarang')}:</strong> {reg.forbidden_keywords}</p>{/if}
											</div>
										{/each}
									</div>
								{/each}
							</CardContent>
						</Card>
					{/if}
				</div>

				<aside class="grid content-start gap-4">
					{#if country.authorities && country.authorities.length > 0}
						<Card class="rounded-xl">
							<CardHeader class="p-4 pb-2">
								<CardTitle class="flex items-center gap-2 text-base">
									<LandmarkIcon class="size-4 text-[#0b3d91]" />
									{t('Otoritas resmi')}
								</CardTitle>
							</CardHeader>
							<CardContent class="grid gap-2 p-4 pt-2">
								{#each country.authorities as auth}
									<a href={auth.url} target="_blank" rel="noopener noreferrer" class="flex items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-[13px] font-semibold transition-colors hover:border-[#0b3d91]/40 hover:bg-secondary">
										<span>{auth.name}</span>
										<ExternalLinkIcon class="size-3.5 shrink-0 text-muted-foreground" />
									</a>
								{/each}
							</CardContent>
						</Card>
					{/if}

					{#if country.sources && country.sources.length > 0}
						<Card class="rounded-xl">
							<CardHeader class="p-4 pb-2">
								<CardTitle class="flex items-center gap-2 text-base">
									<GlobeIcon class="size-4 text-[#0b3d91]" />
									{t('Sumber referensi')}
								</CardTitle>
							</CardHeader>
							<CardContent class="grid gap-2 p-4 pt-2">
								{#each country.sources as src}
									<a href={src.url} target="_blank" rel="noopener noreferrer" class="flex items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-[13px] font-semibold transition-colors hover:border-[#0b3d91]/40 hover:bg-secondary">
										<span>{src.name}</span>
										<ExternalLinkIcon class="size-3.5 shrink-0 text-muted-foreground" />
									</a>
								{/each}
							</CardContent>
						</Card>
					{/if}

					<p class="rounded-xl border border-border bg-secondary/60 px-4 py-3 text-[11px] leading-relaxed text-muted-foreground">
						{t('Baseline regulasi: 15 Agustus 2026. Aturan berubah cepat — selalu verifikasi dengan otoritas & customs broker sebelum shipment.')}
					</p>
				</aside>
			</div>
		</Card>
	{/if}
</AppShell>
