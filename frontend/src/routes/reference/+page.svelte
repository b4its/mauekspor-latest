<script lang="ts">
	/**
	 * Halaman Referensi Regulasi — riset faktual terkurasi (bukan tarif/clearance).
	 *
	 * Menampilkan timeline peristiwa regulasi 2026–2028, angka kunci HS 2028,
	 * status FTA Indonesia, prinsip struktur HS, dan sistem kepabeanan utama —
	 * semuanya bertanggal snapshot dari sumber resmi.
	 */
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { t } from '$lib/i18n.svelte';
	import { getReference, type ReferenceBundle } from '$lib/api/reference';

	import BookOpenCheckIcon from '@lucide/svelte/icons/book-open-check';
	import CalendarClockIcon from '@lucide/svelte/icons/calendar-clock';
	import PackageSearchIcon from '@lucide/svelte/icons/package-search';
	import HandshakeIcon from '@lucide/svelte/icons/handshake';
	import LandmarkIcon from '@lucide/svelte/icons/landmark';
	import AlertTriangleIcon from '@lucide/svelte/icons/alert-triangle';

	let loading = $state(true);
	let error = $state('');
	let ref = $state<ReferenceBundle | null>(null);

	$effect(() => {
		getReference()
			.then((res) => (ref = res.data))
			.catch(() => (error = t('Gagal memuat referensi regulasi.')))
			.finally(() => (loading = false));
	});

	const ftaTone: Record<string, string> = {
		in_force: 'border-emerald-500/40 text-emerald-700 dark:text-emerald-400',
		signed_ratifying: 'border-blue-500/40 text-blue-700 dark:text-blue-400',
		concluded: 'border-amber-500/40 text-amber-700 dark:text-amber-400',
		negotiating: 'border-orange-500/40 text-orange-700 dark:text-orange-400'
	};
	function ftaLabel(status: string) {
		return t(
			status === 'in_force' ? 'Berlaku'
				: status === 'signed_ratifying' ? 'Ditandatangani / ratifikasi'
					: status === 'concluded' ? 'Selesai dirundingkan'
						: 'Sedang dirundingkan'
		);
	}
</script>

<svelte:head>
	<title>{t('Referensi Regulasi')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Referensi Regulasi')} eyebrow={t('Riset faktual bertanggal')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">
				<BookOpenCheckIcon class="size-3.5" />
				{t('Sumber resmi terkurasi')}
			</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
				{t('Regulasi ekspor-impor global & HS Code.')}
			</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Disusun dari WCO, WTO, Komisi Eropa, USTR, CBP, JDIH Kemendag/Kemenkeu, BPK RI, dan firma hukum internasional.')}
			</CardDescription>
		</CardHeader>
		{#if ref}
			<div class="mt-4 flex flex-wrap items-center gap-2">
				<Badge variant="outline">{t('Snapshot')}: {ref.snapshotDate}</Badge>
				<Badge variant="outline">{ref.guide}</Badge>
			</div>
		{/if}
	</Card>

	{#if ref}
		<div class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm" role="note">
			<p class="flex items-start gap-2 font-semibold text-amber-800 dark:text-amber-300">
				<AlertTriangleIcon class="mt-0.5 size-4 shrink-0" />
				{ref.disclaimer}
			</p>
		</div>
	{/if}

	{#if loading}
		<div class="grid gap-4 lg:grid-cols-2">
			<Skeleton class="h-64 w-full rounded-xl" />
			<Skeleton class="h-64 w-full rounded-xl" />
		</div>
	{:else if error}
		<p role="alert" class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{:else if ref}
		<div class="grid gap-4 lg:grid-cols-2">
			<!-- Timeline -->
			<Card>
				<CardHeader class="p-4 pb-2">
					<CardTitle class="flex items-center gap-2 text-base">
						<CalendarClockIcon class="size-4 text-primary" />
						{t('Timeline regulasi 2026–2028')}
					</CardTitle>
				</CardHeader>
				<CardContent class="p-4 pt-2">
					<ol class="relative ms-3 grid max-h-[520px] gap-3 overflow-y-auto border-s border-border ps-4">
						{#each ref.timeline as item}
							<li class="relative">
								<span class="absolute -start-[21px] top-1.5 size-2.5 rounded-full bg-primary ring-2 ring-background"></span>
								<div class="flex flex-wrap items-center gap-2">
									<span class="font-mono text-xs font-bold text-primary">{item.date}</span>
									<Badge variant="secondary" class="text-[10px]">{item.scope}</Badge>
								</div>
								<p class="mt-0.5 text-[13px] leading-snug">{item.event}</p>
							</li>
						{/each}
					</ol>
				</CardContent>
			</Card>

			<div class="grid content-start gap-4">
				<!-- HS 2028 -->
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="flex items-center gap-2 text-base">
							<PackageSearchIcon class="size-4 text-primary" />
							{t('HS 2028 — berlaku')} {ref.hs2028.effective}
						</CardTitle>
					</CardHeader>
					<CardContent class="grid gap-3 p-4 pt-2">
						<div class="grid grid-cols-2 gap-2 text-[13px] sm:grid-cols-3">
							<div class="rounded-lg border bg-muted/30 p-2">
								<span class="block text-[11px] font-semibold text-muted-foreground">{t('Total pos (heading)')}</span>
								<strong class="text-lg font-black">{ref.hs2028.headings_total}</strong>
							</div>
							<div class="rounded-lg border bg-muted/30 p-2">
								<span class="block text-[11px] font-semibold text-muted-foreground">{t('Total subpos')}</span>
								<strong class="text-lg font-black">{ref.hs2028.subheadings_total}</strong>
							</div>
							<div class="rounded-lg border bg-muted/30 p-2">
								<span class="block text-[11px] font-semibold text-muted-foreground">{t('Subpos baru')}</span>
								<strong class="text-lg font-black text-emerald-600 dark:text-emerald-400">+{ref.hs2028.subheadings_new}</strong>
							</div>
							<div class="rounded-lg border bg-muted/30 p-2">
								<span class="block text-[11px] font-semibold text-muted-foreground">{t('Subpos dihapus')}</span>
								<strong class="text-lg font-black text-destructive">−{ref.hs2028.subheadings_deleted}</strong>
							</div>
							<div class="rounded-lg border bg-muted/30 p-2">
								<span class="block text-[11px] font-semibold text-muted-foreground">{t('Edisi')}</span>
								<strong class="text-lg font-black">{ref.hs2028.edition}</strong>
							</div>
							<div class="rounded-lg border bg-muted/30 p-2">
								<span class="block text-[11px] font-semibold text-muted-foreground">{t('Siklus review')}</span>
								<strong class="text-sm font-bold">{ref.hs2028.review_cycle}</strong>
							</div>
						</div>
						<p class="text-[13px] leading-snug"><strong>{t('Perubahan utama')}:</strong> {ref.hs2028.highlights}</p>
						<p class="text-[13px] leading-snug text-muted-foreground"><strong>{t('Persiapan')}:</strong> {ref.hs2028.preparation}</p>
						<p class="text-[13px] leading-snug text-muted-foreground"><strong>{t('Struktur HS')}:</strong> {ref.hsStructureNote}</p>
					</CardContent>
				</Card>

				<!-- FTA -->
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="flex items-center gap-2 text-base">
							<HandshakeIcon class="size-4 text-primary" />
							{t('Status FTA/CEPA Indonesia')}
						</CardTitle>
					</CardHeader>
					<CardContent class="grid gap-2 p-4 pt-2">
						{#each ref.indonesiaFtas as fta}
							<div class="rounded-lg border p-2.5">
								<div class="flex flex-wrap items-center justify-between gap-2">
									<span class="text-sm font-bold">{fta.name}</span>
									<Badge variant="outline" class={ftaTone[fta.status] ?? ''}>{ftaLabel(fta.status)}</Badge>
								</div>
								<p class="mt-1 text-xs text-muted-foreground">{fta.note}</p>
							</div>
						{/each}
					</CardContent>
				</Card>

				<!-- Sistem kepabeanan -->
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="flex items-center gap-2 text-base">
							<LandmarkIcon class="size-4 text-primary" />
							{t('Sistem kepabeanan & nomenklatur')}
						</CardTitle>
					</CardHeader>
					<CardContent class="grid gap-2 p-4 pt-2">
						{#each Object.entries(ref.customsSystems) as [key, sys]}
							<div class="rounded-lg border p-2.5">
								<div class="flex items-center justify-between gap-2">
									<span class="text-sm font-bold">{sys.label}</span>
									<Badge variant="secondary" class="text-[10px]">{key}</Badge>
								</div>
								<p class="mt-0.5 text-xs">{sys.nomenclature}</p>
								<p class="text-xs text-muted-foreground">{sys.note}</p>
							</div>
						{/each}
					</CardContent>
				</Card>
			</div>
		</div>
	{/if}
</AppShell>
