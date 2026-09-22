<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { createQuotation } from '$lib/api/quotations';
	import { shortlistRFQMatch, updateRFQ, deleteRFQ } from '$lib/api/rfq';
	import { goto } from '$app/navigation';

	let { data } = $props();
	let shortlisted = $state('');
	let shortlisting = $state('');
	let quoteCreated = $state(false);
	let creatingQuote = $state(false);
	let error = $state('');
	let message = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let editIncoterm = $state('');
	let editQuantity = $state('');
	let editDeadline = $state('');
	let editStatus = $state('');
	let savedIncoterm = $state('');
	let savedQuantity = $state('');
	let savedDeadline = $state('');
	let savedStatus = $state('');
	let localIncoterm = $derived(savedIncoterm || data.rfq.incoterm);
	let localQuantity = $derived(savedQuantity || data.rfq.quantity);
	let localDeadline = $derived(savedDeadline || data.rfq.deadline);
	let localStatus = $derived(savedStatus || data.rfq.status);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleShortlist(supplier: string) {
		error = '';
		shortlisting = supplier;
		try {
			const res = await shortlistRFQMatch(data.rfq.id, supplier);
			data.rfq = res.data;
			shortlisted = supplier;
		} catch {
			error = t('Gagal menambahkan supplier ke shortlist.');
		} finally {
			shortlisting = '';
		}
	}

	async function handleCreateQuote() {
		error = '';
		creatingQuote = true;
		try {
			await createQuotation({
				rfqId: data.rfq.id,
				incoterm: data.rfq.incoterm,
				value: 42800,
				currency: 'IDR',
				validUntil: '2026-09-30'
			});
			quoteCreated = true;
		} catch {
			error = 'Gagal membuat quotation draft.';
		} finally {
			creatingQuote = false;
		}
	}

	function openEdit() {
		editIncoterm = localIncoterm;
		editQuantity = localQuantity;
		editDeadline = localDeadline;
		editStatus = localStatus;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editQuantity.trim()) {
			error = t('Jumlah wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await updateRFQ(data.rfq.id, {
				incoterm: editIncoterm.trim(),
				quantity: editQuantity.trim(),
				deadline: editDeadline.trim(),
				status: editStatus.trim() as typeof data.rfq.status
			});
			savedIncoterm = res.data.incoterm;
			savedQuantity = res.data.quantity;
			savedDeadline = res.data.deadline;
			savedStatus = res.data.status;
			message = t('RFQ diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan RFQ.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus RFQ ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteRFQ(data.rfq.id);
			goto('/rfq');
		} catch {
			error = t('Gagal menghapus RFQ.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.rfq.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.rfq.id} eyebrow="RFQ detail">
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(localStatus))}>{localStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.rfq.product}
				</CardTitle>
				<CardDescription class="mt-2">{data.rfq.buyer} - {data.rfq.destination}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Best match')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{data.rfq.matchScore}%</strong>
			</div>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-2">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Incoterm')}
						<Input bind:value={editIncoterm} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Quantity')}
						<Input bind:value={editQuantity} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Deadline')}
						<Input bind:value={editDeadline} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
				</div>
				<Button class="w-fit" disabled={saving} onclick={handleSave}>{saving ? t('Menyimpan...') : t('Simpan perubahan')}</Button>
			</div>
		{/if}
		{#if message}
			<p class="mt-4 rounded-lg bg-emerald-500/10 px-3 py-2 text-sm font-bold text-emerald-600">{message}</p>
		{/if}
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="p-0"><CardTitle>{t('RFQ Requirements')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Proyek')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.project?.name ?? data.rfq.projectId}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Quantity')} <strong class="mt-1 block text-sm font-bold text-foreground">{localQuantity}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Incoterm')} <strong class="mt-1 block text-sm font-bold text-foreground">{localIncoterm}</strong>
					</div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
						{t('Deadline')} <strong class="mt-1 block text-sm font-bold text-foreground">{localDeadline}</strong>
					</div>
				</div>
				<div class="flex flex-wrap gap-2.5">
					{#each data.rfq.requirements as requirement}
						<Badge variant="outline">{requirement}</Badge>
					{/each}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Supplier Matches')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 pt-4">
				{#each data.rfq.matches as match}
					<div class="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-muted/30 p-3.5">
						<div>
							<strong class="block text-sm font-bold">{match.supplier}</strong>
							<p class="my-1 text-sm text-muted-foreground">{match.catalog}</p>
							<small class="text-xs text-muted-foreground">{match.reason}</small>
						</div>
						<div class="grid justify-items-end gap-2">
							<b class="text-2xl font-bold tracking-tight">{match.score}%</b>
							<Button variant="outline" size="sm" disabled={shortlisting !== ''} onclick={() => handleShortlist(match.supplier)}>{shortlisting === match.supplier ? t('Shortlisting...') : t('Shortlist')}</Button>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Commercial action')}</Badge>
				<CardTitle>{t('Create quotation')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<p class="text-muted-foreground">{shortlisted ? t('{} is shortlisted for quotation.').replace('{}', shortlisted) : t('Shortlist a supplier match before creating quotation.')}</p>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
				{#if quoteCreated}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Quotation draft tersimpan di backend.')}</p>
				{/if}
				<Button class="w-fit" disabled={!shortlisted || quoteCreated} onclick={handleCreateQuote}>{quoteCreated ? 'Draft created' : creatingQuote ? 'Creating...' : 'Create quotation draft'}</Button>
			</CardContent>
		</Card>
	</div>
</AppShell>