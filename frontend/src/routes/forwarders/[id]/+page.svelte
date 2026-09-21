<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { t } from '$lib/i18n.svelte';
import { requestForwarderQuote, getForwarderStatistics, createForwarderReview, updateForwarderReview, deleteForwarderReview } from '$lib/api/forwarders';
import type { ForwarderStatistics, ForwarderReview } from '$lib/api/forwarders';
import WhatsAppDialog from '$lib/components/WhatsAppDialog.svelte';

	let { data } = $props();
	let quoteRequested = $state(false);
	let requesting = $state(false);
	let error = $state('');
	let stats = $state<ForwarderStatistics | null>(null);
	let rating = $state(5);
	let reviewText = $state('');
	let submitting = $state(false);
	let submitted = $state(false);
	let editingId = $state('');
	let editingRating = $state(5);
	let editingText = $state('');
	let savingEdit = $state(false);
	let editError = $state('');
	let deletingId = $state('');

	$effect(() => {
		getForwarderStatistics(data.forwarder.id)
			.then((res) => (stats = res.data))
			.catch((e) => console.error("API error:", e));
	});

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleQuote() {
		error = '';
		requesting = true;
		try {
			await requestForwarderQuote(data.forwarder.id);
			quoteRequested = true;
		} catch {
			error = t('Gagal meminta kuotasi forwarder.');
		} finally {
			requesting = false;
		}
	}

	async function handleReview() {
		error = '';
		submitting = true;
		try {
			await createForwarderReview(data.forwarder.id, { rating, review_text: reviewText });
			submitted = true;
			reviewText = '';
			stats = (await getForwarderStatistics(data.forwarder.id)).data;
		} catch {
			error = t('Gagal mengirim review.');
		} finally {
			submitting = false;
		}
	}

	async function handleEditReview(review: ForwarderReview) {
		editError = '';
		if (!Number.isFinite(editingRating) || editingRating < 1 || editingRating > 5) {
			editError = t('Rating harus antara 1 dan 5.');
			return;
		}
		savingEdit = true;
		try {
			await updateForwarderReview(data.forwarder.id, review.id!, { rating: editingRating, review_text: editingText });
			editingId = '';
			submitted = true;
			stats = (await getForwarderStatistics(data.forwarder.id)).data;
		} catch {
			editError = t('Gagal memperbarui review.');
		} finally {
			savingEdit = false;
		}
	}

	async function handleDeleteReview(review: ForwarderReview) {
		editError = '';
		deletingId = review.id ?? '';
		try {
			await deleteForwarderReview(data.forwarder.id, review.id!);
			stats = (await getForwarderStatistics(data.forwarder.id)).data;
		} catch {
			editError = t('Gagal menghapus review.');
		} finally {
			deletingId = '';
		}
	}
</script>

<svelte:head>
	<title>{data.forwarder.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.forwarder.id} eyebrow={t('Forwarder detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.forwarder.status))}>{data.forwarder.status}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.forwarder.name}
				</CardTitle>
				<CardDescription class="mt-2">{data.forwarder.coverage} - {data.forwarder.mode}</CardDescription>
			</div>
			<div class="grid gap-2.5 md:min-w-[200px]">
				<WhatsAppDialog
					phone={data.forwarder.contact ?? ''}
					contactName={data.forwarder.name}
					company={data.forwarder.name}
				/>
				<Button disabled={quoteRequested || requesting} onclick={handleQuote}>
					{quoteRequested ? t('Kuotasi diminta') : requesting ? t('Meminta...') : t('Minta kuotasi')}
				</Button>
				<Button variant="outline" href="/forwarders/catalogs">{t('Lihat katalog')}</Button>
				<Button variant="outline" href="/shipments">{t('Buka pengiriman')}</Button>
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if quoteRequested}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">{t('Kuotasi diminta.')}</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				{t('Permintaan kuotasi dikirim ke')} {data.forwarder.contact} {t('di backend.')}
			</span>
		</div>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader><CardTitle>{t('Profil freight')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Cakupan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.coverage}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Mode')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.mode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tingkat tepat waktu')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.onTimeRate}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kecepatan kuotasi')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.quoteSpeed}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.contact}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Rating')} <strong class="mt-1 block text-sm font-bold text-foreground">
						{data.forwarder.averageRating ?? 0} ⭐ ({data.forwarder.totalReviews ?? 0} {t('ulasan')})
					</strong>
				</div>
			</CardContent>
		</Card>

		{#if stats}
			<Card>
				<CardHeader><CardTitle>{t('Statistik rating')}</CardTitle></CardHeader>
				<CardContent class="grid gap-2.5">
					<div class="grid gap-1.5">
						{#each Object.entries(stats.ratingDistribution ?? {}) as [star, percent]}
							<div class="flex items-center gap-2 text-xs">
								<span class="w-4 font-bold">{star}★</span>
								<div class="h-2 flex-1 overflow-hidden rounded-full bg-muted">
									<div class="h-full bg-primary" style={`width:${percent}%`}></div>
								</div>
								<span class="w-8 text-right text-muted-foreground">{percent}%</span>
							</div>
						{/each}
					</div>
					<p class="mt-2 text-xs text-muted-foreground">
						{stats.uniquePartnerships} {t('kemitraan unik')} · {stats.totalReviews} {t('total review')}
					</p>
				</CardContent>
			</Card>

			{#if (stats.recentReviews ?? []).length > 0}
				<Card>
					<CardHeader><CardTitle>{t('Ulasan terbaru')}</CardTitle></CardHeader>
					<CardContent class="grid gap-2.5">
						{#each stats.recentReviews ?? [] as review}
							<div class="rounded-lg border bg-muted/30 p-3.5">
								<div class="flex items-center justify-between gap-2">
									<strong class="text-sm font-bold">
										{review.rating} ★
										<span class="ml-1 font-normal text-muted-foreground">{review.reviewerName ?? t('Anonim')} · {review.createdAt ?? '—'}</span>
									</strong>
									<div class="flex gap-2">
										<Button size="sm" variant="outline" onclick={() => {
											editingId = review.id ?? '';
											editingRating = review.rating;
											editingText = review.reviewText ?? '';
										}}>{t('Ubah')}</Button>
										<Button size="sm" variant="outline" class="text-destructive hover:text-destructive" disabled={deletingId !== ''} onclick={() => handleDeleteReview(review)}>
											{deletingId === review.id ? t('Menghapus...') : t('Hapus')}
										</Button>
									</div>
								</div>
								{#if editingId === review.id}
									<div class="mt-3 grid gap-2">
										<select class="h-9 rounded-md border bg-background px-2 text-sm" bind:value={editingRating}>
											{#each [5, 4, 3, 2, 1] as r}<option value={r}>{r} ★</option>{/each}
										</select>
										<Input placeholder={t('Tulis ulasan...')} bind:value={editingText} />
										{#if editError}
											<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{editError}</p>
										{/if}
										<div class="flex gap-2">
											<Button size="sm" disabled={savingEdit} onclick={() => handleEditReview(review)}>{savingEdit ? t('Menyimpan...') : t('Simpan')}</Button>
											<Button size="sm" variant="ghost" onclick={() => (editingId = '')}>{t('Batal')}</Button>
										</div>
									</div>
								{:else if review.reviewText}
									<p class="mt-1.5 text-sm text-muted-foreground">{review.reviewText}</p>
								{/if}
							</div>
						{/each}
					</CardContent>
				</Card>
			{/if}
		{/if}

		<Card>
			<CardHeader>
				<CardTitle>{t('Tambah ulasan')}</CardTitle>
				<CardDescription>{t('Rating 1-5 + ulasan untuk forwarder ini.')}</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if submitted}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Review terkirim. Rating diperbarui.')}</p>
				{/if}
				<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
					{t('Rating')}
					<select class="h-10 rounded-md border bg-background px-3 text-sm" bind:value={rating}>
						{#each [5, 4, 3, 2, 1] as r}<option value={r}>{r} ★</option>{/each}
					</select>
				</label>
				<Input placeholder={t('Tulis ulasan...')} bind:value={reviewText} />
				<Button onclick={handleReview} disabled={submitting}>{submitting ? t('Mengirim...') : t('Kirim review')}</Button>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>{t('Jalur yang dicakup')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each data.forwarder.lanes ?? [] as lane}
					<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">{t('Route')}</Badge><strong class="text-sm">{lane}</strong></div>
				{/each}
			</CardContent>
		</Card>
	</div>
</AppShell>