<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { matchBuyerRequest, getMatchedCatalogs, getMatchedUmkm, updateBuyerRequestStatus } from '$lib/api/buyer-requests';
	import type { MatchedItem } from '$lib/api/buyer-requests';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let matches = $state<MatchedItem[]>([]);
	let matching = $state(false);
	let error = $state('');

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleMatch() {
		error = '';
		matching = true;
		try {
			const res = await matchBuyerRequest(data.request.id);
			data.request.status = res.data.status;
			matches = (await getMatchedCatalogs(data.request.id)).data;
		} catch {
			error = t('Gagal mencocokkan permintaan.');
		} finally {
			matching = false;
		}
	}

	async function handleClose() {
		error = '';
		try {
			await updateBuyerRequestStatus(data.request.id, { status: 'Closed' });
			data.request.status = 'Closed';
		} catch {
			error = t('Gagal menutup permintaan.');
		}
	}

	// Pilih katalog/UMKM lalu tutup request (alur Buyer -> UMKM terpilih)
	let selectingId = $state('');
	async function handleSelect(match: MatchedItem) {
		if (!match.catalogId) return;
		error = '';
		selectingId = String(match.catalogId);
		try {
			await updateBuyerRequestStatus(data.request.id, {
				status: 'Closed',
				selected_catalog: String(match.catalogId),
				umkm: String(match.umkm_id ?? '')
			});
			data.request.status = 'Closed';
			data.request.selectedCatalogId = String(match.catalogId);
		} catch {
			error = t('Gagal menutup permintaan.');
		} finally {
			selectingId = '';
		}
	}

	$effect(() => {
		// matched-umkm memperkaya data (contactInfo, catalogTitle) untuk peran Buyer
		getMatchedUmkm(data.request.id)
			.then((res) => (matches = res.data))
			.catch(() =>
				getMatchedCatalogs(data.request.id)
					.then((res) => (matches = res.data))
					.catch(() => {})
			);
	});

	function scoreTone(score: number) {
		if (score >= 80) return 'default';
		if (score >= 60) return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.request.subject} | MauEkspor</title>
</svelte:head>

<AppShell title={data.request.id} eyebrow={t('Buyer request detail')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.request.status))}>{data.request.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.request.subject}
				</CardTitle>
				<CardDescription class="mt-2">{data.buyer?.name ?? t('Pembeli tidak diketahui')} {t('menginginkan')} {data.request.quantity} {t('untuk')} {data.request.destination}.</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<Button variant="outline" href={`/buyer-requests/${data.request.id}/edit`}>{t('Edit permintaan')}</Button>
				<Button disabled={matching} onclick={handleMatch}>{matching ? t('Mencocokkan...') : t('Jalankan pencocokan')}</Button>
				{#if data.request.status !== 'Closed'}
					<Button variant="outline" onclick={handleClose}>{t('Tutup permintaan')}</Button>
				{/if}
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader><CardTitle>{t('Ketentuan Permintaan')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Pembeli')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer?.name ?? t('Tidak diketahui')}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Produk')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.product?.name ?? '—'}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Jumlah')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.quantity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tujuan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.destination}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Batas waktu')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.deadline}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Status')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.request.status}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>{t('Persyaratan')}</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2">
				{#each data.request.requirements ?? [] as requirement}
					<span class="rounded-full border bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">{requirement}</span>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader>
				<Badge variant="secondary">{t('Pencocokan')}</Badge>
				<CardTitle>{t('Katalog yang cocok')} ({matches.length})</CardTitle>
				<CardDescription>{t('Skor akhir = kategori (35%) + HS code (30%) + spesifikasi (25%) + kapabilitas (5%) + volume (5%).')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-2.5">
				{#if matches.length === 0}
					<p class="text-sm font-semibold text-muted-foreground">{t('Belum ada kecocokan. Jalankan matching.')}</p>
				{/if}
				{#each matches as match}
					<div class="rounded-lg border bg-muted/30 p-3.5">
						<div class="flex items-center justify-between gap-3">
							<strong class="text-sm">{match.product ?? match.catalogTitle}</strong>
							<Badge variant={scoreTone(match.match_score)}>{match.match_score}</Badge>
						</div>
						{#if match.match_reasons && match.match_reasons.length > 0}
							<div class="mt-1.5 flex flex-wrap gap-1.5">
								{#each match.match_reasons as reason}
									<span class="rounded-full border bg-background/60 px-2 py-0.5 text-[10px] font-bold text-muted-foreground">{reason}</span>
								{/each}
							</div>
						{/if}
						{#if match.umkm_name}
							<p class="mt-1.5 text-xs text-muted-foreground">{t('UMKM:')} {match.umkm_name}</p>
						{/if}
						{#if match.contactInfo && (match.contactInfo.phone || match.contactInfo.email)}
							<p class="mt-1 text-xs text-muted-foreground">{t('Kontak:')} {match.contactInfo.phone || match.contactInfo.email}</p>
						{/if}
						{#if data.request.status !== 'Closed'}
							<div class="mt-2.5">
								<Button size="sm" variant="outline" onclick={() => handleSelect(match)} disabled={selectingId !== ''}>
									{selectingId === String(match.catalogId) ? t('Memilih...') : t('Pilih katalog ini')}
								</Button>
							</div>
						{:else if data.request.selectedCatalogId === String(match.catalogId)}
							<p class="mt-2 text-xs font-bold text-primary">✓ {t('Katalog terpilih')}</p>
						{/if}
					</div>
				{/each}
			</CardContent>
		</Card>
	</div>
</AppShell>
