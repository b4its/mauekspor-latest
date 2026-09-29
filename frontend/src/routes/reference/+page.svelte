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

		<!-- Incoterms® 2020 -->
		{#if ref.incoterms?.length}
			<Card class="mt-4">
				<CardHeader class="p-4 pb-2">
					<CardTitle class="flex items-center gap-2 text-base">
						<HandshakeIcon class="size-4 text-primary" />
						{t('Incoterms® 2020 (ICC)')}
					</CardTitle>
				</CardHeader>
				<CardContent class="p-4 pt-2">
					<div class="overflow-x-auto">
						<table class="w-full text-left text-[13px]">
							<thead>
								<tr class="border-b text-muted-foreground">
									<th class="py-1.5 pe-3">{t('Kode')}</th>
									<th class="py-1.5 pe-3">{t('Nama')}</th>
									<th class="py-1.5 pe-3">{t('Risiko berpindah')}</th>
									<th class="py-1.5">{t('Moda')}</th>
								</tr>
							</thead>
							<tbody>
								{#each ref.incoterms as inc}
									<tr class="border-b last:border-0">
										<td class="py-1.5 pe-3 font-mono font-bold text-primary">{inc.code}</td>
										<td class="py-1.5 pe-3 font-semibold">{inc.name}</td>
										<td class="py-1.5 pe-3">{inc.risk}</td>
										<td class="py-1.5">{inc.mode}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
					<ul class="mt-3 grid gap-1 text-xs text-muted-foreground">
						{#each ref.incotermsNotes ?? [] as note}
							<li>• {note}</li>
						{/each}
					</ul>
				</CardContent>
			</Card>
		{/if}

		<div class="mt-4 grid gap-4 lg:grid-cols-2">
			<!-- HS: panjang digit + KUMHS -->
			{#if ref.hsDigitLengths?.length}
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="flex items-center gap-2 text-base">
							<PackageSearchIcon class="size-4 text-primary" />
							{t('Panjang digit HS per negara/kawasan')}
						</CardTitle>
					</CardHeader>
					<CardContent class="grid gap-1.5 p-4 pt-2 text-[13px]">
						{#each ref.hsDigitLengths as row}
							<div class="flex items-center justify-between gap-2 rounded-lg border px-3 py-1.5">
								<span class="font-semibold">{row.name}</span>
								<span class="text-muted-foreground">{row.system} · <b class="text-foreground">{row.digits}</b> {t('digit')}</span>
							</div>
						{/each}
					</CardContent>
				</Card>
			{/if}

			{#if ref.kumhs?.length}
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="text-base">{t('KUMHS — Ketentuan Umum Menginterpretasi HS')}</CardTitle>
					</CardHeader>
					<CardContent class="grid gap-2 p-4 pt-2">
						{#each ref.kumhs as rule}
							<div class="text-[13px]">
								<span class="font-bold text-primary">{rule.rule}.</span>
								<span class="text-muted-foreground"> {rule.detail}</span>
							</div>
						{/each}
					</CardContent>
				</Card>
			{/if}
		</div>

		<!-- Indonesia -->
		{#if ref.indonesia}
			<Card class="mt-4">
				<CardHeader class="p-4 pb-2">
					<CardTitle class="flex items-center gap-2 text-base">
						<LandmarkIcon class="size-4 text-primary" />
						{t('Regulasi Ekspor-Impor Indonesia')}
					</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-4 p-4 pt-2 lg:grid-cols-2">
					<div>
						<h4 class="mb-1.5 text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Dasar hukum utama')}</h4>
						<ul class="grid gap-1 text-[13px]">
							{#each ref.indonesia.legalBasis as item}
								<li><b class="font-semibold">{item.regulation}</b> — {item.material}</li>
							{/each}
						</ul>
					</div>
					<div class="grid content-start gap-4">
						<div>
							<h4 class="mb-1.5 text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Pungutan impor')}</h4>
							<ul class="grid gap-1 text-[13px]">
								{#each ref.indonesia.importLevies as l}
									<li><b class="font-semibold">{l.levy}</b> — {l.rate}</li>
								{/each}
							</ul>
						</div>
						<div>
							<h4 class="mb-1.5 text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Perizinan & identitas')}</h4>
							<ul class="grid gap-1 text-[13px]">
								{#each ref.indonesia.licenses as l}
									<li><b class="font-semibold">{l.document}</b> — {l.note}</li>
								{/each}
							</ul>
						</div>
						<div class="rounded-lg border border-primary/30 bg-primary/5 p-3 text-[13px]">
							<h4 class="mb-1 text-xs font-bold uppercase tracking-wide text-primary">{t('DHE SDA')} · {ref.indonesia.dhe.regulation}</h4>
							<p>{t('Berlaku')} {ref.indonesia.dhe.effective} · {t('repatriasi')} <b>{ref.indonesia.dhe.repatriation}</b></p>
							<p class="text-muted-foreground">{t('Nonmigas')}: {ref.indonesia.dhe.nonmigas_placement}; {t('Migas')}: {ref.indonesia.dhe.migas_placement}</p>
							<p class="text-muted-foreground">{ref.indonesia.dhe.bank}</p>
						</div>
					</div>
				</CardContent>
			</Card>
		{/if}

		<div class="mt-4 grid gap-4 lg:grid-cols-2">
			<!-- Amerika Serikat -->
			{#if ref.unitedStates}
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="text-base">{t('Amerika Serikat — rezim tarif 2025–2026')}</CardTitle>
					</CardHeader>
					<CardContent class="p-4 pt-2">
						<ol class="relative ms-3 grid max-h-72 gap-2.5 overflow-y-auto border-s border-border ps-4 text-[13px]">
							{#each ref.unitedStates.timeline as item}
								<li class="relative">
									<span class="absolute -start-[19px] top-1.5 size-2 rounded-full bg-primary ring-2 ring-background"></span>
									<span class="font-mono text-xs font-bold text-primary">{item.date}</span>
									<p class="leading-snug">{item.event}</p>
								</li>
							{/each}
						</ol>
						<div class="mt-3 rounded-lg border border-destructive/30 bg-destructive/5 p-2.5 text-[12px]">
							<b>Section 301 Forced Labor</b> ({ref.unitedStates.section301ForcedLabor.effective}): 10%
							→ {ref.unitedStates.section301ForcedLabor.standard_10pct.join(', ')}; 12,5%
							→ {ref.unitedStates.section301ForcedLabor.standard_12_5pct.join(', ')}.
						</div>
					</CardContent>
				</Card>
			{/if}

			<!-- Uni Eropa -->
			{#if ref.europeanUnion}
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="text-base">{t('Uni Eropa — CBAM, EUDR & reformasi kepabeanan')}</CardTitle>
					</CardHeader>
					<CardContent class="grid gap-3 p-4 pt-2 text-[13px]">
						<div class="rounded-lg border p-2.5">
							<b>{t('CBAM')}</b> ({ref.europeanUnion.cbam.regulation}) — {t('definitif')} {ref.europeanUnion.cbam.definitive_start};
							{t('sektor')}: {(ref.europeanUnion.cbam.sectors as string[]).join(', ')};
							{t('de minimis')}: {ref.europeanUnion.cbam.de_minimis}.
							<p class="text-muted-foreground">{t('Dampak Indonesia')}: {ref.europeanUnion.cbam.indonesia_impact}</p>
						</div>
						<div class="rounded-lg border p-2.5">
							<b>EUDR</b> ({ref.europeanUnion.eudr.regulation}) — {t('komoditas')}:
							{(ref.europeanUnion.eudr.commodities as string[]).join(', ')}.
							{t('Berlaku')} {ref.europeanUnion.eudr.large_operators} ({t('besar/menengah')}) &amp;
							{ref.europeanUnion.eudr.micro_small} ({t('mikro/kecil')}).
						</div>
						<ul class="grid gap-1 text-xs text-muted-foreground">
							{#each ref.europeanUnion.customsReform as line}
								<li>• {line}</li>
							{/each}
						</ul>
					</CardContent>
				</Card>
			{/if}
		</div>

		<!-- Dokumen & pembayaran -->
		{#if ref.standardDocuments?.length}
			<Card class="mt-4">
				<CardHeader class="p-4 pb-2">
					<CardTitle class="text-base">{t('Dokumen ekspor-impor standar')}</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-2 p-4 pt-2 text-[13px] sm:grid-cols-2">
					{#each ref.standardDocuments as doc}
						<div class="rounded-lg border px-3 py-1.5">
							<b class="font-semibold">{doc.document}</b>
							<span class="text-muted-foreground"> — {doc.function}</span>
						</div>
					{/each}
					{#if ref.paymentMethods}
						<p class="text-xs text-muted-foreground sm:col-span-2"><b>{t('Metode pembayaran')}:</b> {ref.paymentMethods}</p>
					{/if}
				</CardContent>
			</Card>
		{/if}

		<!-- Checklist kepatuhan -->
		{#if ref.complianceChecklist?.length}
			<Card class="mt-4">
				<CardHeader class="p-4 pb-2">
					<CardTitle class="text-base">{t('Checklist kepatuhan ekspor-impor')}</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-4 p-4 pt-2 lg:grid-cols-2">
					{#each ref.complianceChecklist as group}
						<div>
							<h4 class="mb-1.5 text-xs font-bold uppercase tracking-wide text-primary">{group.section}</h4>
							<ul class="grid gap-1 text-[13px]">
								{#each group.items as item}
									<li class="flex gap-2"><span class="text-muted-foreground">☐</span><span>{item}</span></li>
								{/each}
							</ul>
						</div>
					{/each}
				</CardContent>
			</Card>
		{/if}

		<!-- Portal resmi -->
		{#if ref.officialPortals?.length || ref.globalPortals?.length}
			<Card class="mt-4">
				<CardHeader class="p-4 pb-2">
					<CardTitle class="text-base">{t('Portal resmi untuk verifikasi')}</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-2 p-4 pt-2 text-[13px] sm:grid-cols-2 lg:grid-cols-3">
					{#each ref.globalPortals ?? [] as p}
						<div class="rounded-lg border p-2.5">
							<b class="font-semibold">{p.need}</b>
							<p class="text-xs text-muted-foreground">{p.portal}</p>
						</div>
					{/each}
					{#each ref.officialPortals ?? [] as p}
						<div class="rounded-lg border p-2.5">
							<b class="font-semibold">{p.country}</b>
							<p class="text-xs text-muted-foreground">{p.portals.join(' · ')}</p>
						</div>
					{/each}
				</CardContent>
			</Card>
		{/if}

		{#if ref.primarySources?.length}
			<div class="mt-4 rounded-xl border bg-muted/30 p-4 text-xs text-muted-foreground">
				<h4 class="mb-1.5 font-bold uppercase tracking-wide">{t('Sumber rujukan utama')}</h4>
				<ul class="grid gap-1">
					{#each ref.primarySources as src}
						<li>• {src}</li>
					{/each}
				</ul>
			</div>
		{/if}
	{/if}
</AppShell>
