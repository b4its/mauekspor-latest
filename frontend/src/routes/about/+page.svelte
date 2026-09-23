<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { t } from '$lib/i18n.svelte';

	const pillars = [
		{ title: 'Kesiapan', text: 'Data produk terstruktur, profil bisnis, dan sertifikasi sebagai fondasi setiap alur ekspor.' },
		{ title: 'Analisis', text: 'Klasifikasi HS, bea masuk, pembatasan, dan rekomendasi regulasi sebelum komitmen komersial.' },
		{ title: 'Eksekusi', text: 'RFQ, kutipan harga, costing, dokumen, pembayaran, dan tonggak pengiriman dalam satu workspace.' }
	];
</script>

<svelte:head>
	<title>About | MauEkspor</title>
</svelte:head>

<AppShell title="About" eyebrow={t('Sistem operasi dagang')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="outline">{t('Indonesia ke pasar global')}</Badge>
			<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{t('Satu workspace dari kesiapan produk hingga pengiriman.')}</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('MauEkspor menyatukan data produk, klasifikasi HS, bukti kepatuhan, RFQ, kutipan harga, validasi dokumen, tarif forwarder, dan tonggak pengiriman untuk eksportir Indonesia.')}
			</CardDescription>
		</CardHeader>
		<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
			<div class="grid justify-items-center gap-2.5">
				<div class="grid size-16 place-items-center rounded-2xl bg-gradient-to-br from-primary to-blue-950 text-xl font-black text-white tracking-tight">ME</div>
				<strong>{t('MauEkspor Trade OS')}</strong>
			</div>
		</CardContent>
	</Card>

	<div class="grid gap-4 md:grid-cols-3">
		{#each pillars as pillar}
			<Card class="grid content-start gap-3">
				<Badge variant="secondary" class="w-fit">{t(pillar.title)}</Badge>
				<h3 class="text-2xl font-bold tracking-tight">{t(pillar.title)}</h3>
				<p class="leading-relaxed text-muted-foreground">{t(pillar.text)}</p>
			</Card>
		{/each}
	</div>

	<Card>
		<h3 class="text-2xl font-bold tracking-tight">{t('Dibangun untuk alur kerja ekspor')}</h3>
		<div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/dashboard">{t('Mulai dari dashboard')}</a>
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/business-profile">{t('Lengkapi profil bisnis')}</a>
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/educational">{t('Pelajari proses ekspor')}</a>
			<a class="grid place-items-center rounded-xl border p-5 text-center font-bold no-underline transition-colors hover:border-ring/40 hover:bg-muted/40" href="/export-analysis">{t('Analisis pasar tujuan')}</a>
		</div>
	</Card>
</AppShell>
