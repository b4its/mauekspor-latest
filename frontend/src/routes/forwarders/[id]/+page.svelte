<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
import { requestForwarderQuote, getForwarderStatistics, createForwarderReview } from '$lib/api/forwarders';
import type { ForwarderStatistics } from '$lib/api/forwarders';
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

	$effect(() => {
		getForwarderStatistics(data.forwarder.id)
			.then((res) => (stats = res.data))
			.catch(() => {});
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
			error = 'Gagal meminta kuotasi forwarder.';
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
			stats = (await getForwarderStatistics(data.forwarder.id)).data;
		} catch {
			error = 'Gagal mengirim review.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.forwarder.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.forwarder.id} eyebrow="Forwarder detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(data.forwarder.status))}>{data.forwarder.status}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
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
					{quoteRequested ? 'Quote requested' : requesting ? 'Requesting...' : 'Request quote'}
				</Button>
				<Button variant="outline" href="/forwarders/catalogs">View catalogs</Button>
				<Button variant="outline" href="/shipments">Open shipments</Button>
			</div>
		</div>
	</Card>

	{#if error}
		<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
	{/if}

	{#if quoteRequested}
		<div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-4">
			<strong class="block">Quote requested.</strong>
			<span class="mt-1 block text-sm text-muted-foreground">
				Permintaan kuotasi dikirim ke {data.forwarder.contact} di backend.
			</span>
		</div>
	{/if}

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader><CardTitle>Freight profile</CardTitle></CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Coverage <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.coverage}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Mode <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.mode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					On-time rate <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.onTimeRate}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Quote speed <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.quoteSpeed}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Contact <strong class="mt-1 block text-sm font-bold text-foreground">{data.forwarder.contact}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Rating <strong class="mt-1 block text-sm font-bold text-foreground">
						{data.forwarder.averageRating ?? 0} ⭐ ({data.forwarder.totalReviews ?? 0} review)
					</strong>
				</div>
			</CardContent>
		</Card>

		{#if stats}
			<Card>
				<CardHeader><CardTitle>Rating statistics</CardTitle></CardHeader>
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
						{stats.uniquePartnerships} kemitraan unik · {stats.totalReviews} total review
					</p>
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader>
				<CardTitle>Add review</CardTitle>
				<CardDescription>Rating 1-5 + ulasan untuk forwarder ini.</CardDescription>
			</CardHeader>
			<CardContent class="grid gap-3">
				{#if submitted}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">Review terkirim. Rating diperbarui.</p>
				{/if}
				<label class="grid gap-1.5 text-xs font-bold text-muted-foreground">
					Rating
					<select class="h-10 rounded-md border bg-background px-3 text-sm" bind:value={rating}>
						{#each [5, 4, 3, 2, 1] as r}<option value={r}>{r} ★</option>{/each}
					</select>
				</label>
				<Input placeholder="Tulis ulasan..." bind:value={reviewText} />
				<Button onclick={handleReview} disabled={submitting}>{submitting ? 'Mengirim...' : 'Kirim review'}</Button>
			</CardContent>
		</Card>

		<Card>
			<CardHeader><CardTitle>Covered lanes</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5">
				{#each data.forwarder.lanes ?? [] as lane}
					<div class="flex items-center gap-3 rounded-lg border bg-muted/30 p-3.5"><Badge variant="outline">Route</Badge><strong class="text-sm">{lane}</strong></div>
				{/each}
			</CardContent>
		</Card>
	</div>
</AppShell>