<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { verifySupplier, requestSupplierEvidence, updateSupplier, deleteSupplier } from '$lib/api/suppliers';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let verified = $state(false);
	let evidenceRequested = $state(false);
	let error = $state('');
	let message = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let editName = $state('');
	let editLocation = $state('');
	let editContact = $state('');
	let savedName = $state('');
	let savedLocation = $state('');
	let serverStatus = $state('');
	let serverScore = $state<number | null>(null);
	let localName = $derived(savedName || data.supplier.name);
	let localLocation = $derived(savedLocation || data.supplier.location);
	let displayStatus = $derived(serverStatus || (verified ? 'Verified' : data.supplier.status));
	let displayScore = $derived(serverScore ?? (verified ? Math.max(data.supplier.capabilityScore, 95) : data.supplier.capabilityScore));

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleVerify() {
		error = '';
		try {
			const res = await verifySupplier(data.supplier.id);
			verified = true;
			if (res.data) {
				serverStatus = res.data.status;
				if (typeof res.data.capabilityScore === 'number') serverScore = res.data.capabilityScore;
			}
			message = t('Supplier diverifikasi.');
		} catch {
			error = t('Gagal memverifikasi supplier.');
		}
	}

	async function handleRequestEvidence() {
		error = '';
		try {
			const res = await requestSupplierEvidence(data.supplier.id);
			evidenceRequested = true;
			if (res.data) serverStatus = res.data.status;
			message = t('Permintaan bukti dikirim.');
		} catch {
			error = t('Gagal meminta evidence.');
		}
	}

	function openEdit() {
		editName = localName;
		editLocation = localLocation;
		editContact = data.supplier.contact ?? '';
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editName.trim()) {
			error = t('Nama supplier wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await updateSupplier(data.supplier.id, {
				name: editName.trim(),
				location: editLocation.trim(),
				contact: editContact.trim()
			});
			savedName = res.data.name;
			savedLocation = res.data.location ?? '';
			message = t('Supplier diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan supplier.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus supplier ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteSupplier(data.supplier.id);
			goto('/suppliers');
		} catch {
			error = t('Gagal menghapus supplier.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.supplier.name} | MauEkspor</title>
</svelte:head>

<AppShell title={localName} eyebrow={t('Supplier detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{data.supplier.category}
				</CardTitle>
				<CardDescription class="mt-2">{localLocation} · {data.supplier.contact}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Kapabilitas')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{displayScore}%</strong>
			</div>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit supplier')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus supplier')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Nama')}
						<Input bind:value={editName} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Lokasi')}
						<Input bind:value={editLocation} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Kontak')}
						<Input bind:value={editContact} />
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
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Profil Operasional')}</CardTitle>
					<CardDescription>{t('Kesiapan supplier untuk pencocokan ekspor, costing, perencanaan produksi, dan pengumpulan bukti kepatuhan.')}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" onclick={handleRequestEvidence}>{evidenceRequested ? t('Bukti diminta') : t('Minta bukti')}</Button>
					<Button onclick={handleVerify}>{verified ? t('Terverifikasi') : t('Verifikasi supplier')}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kapasitas')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.supplier.capacity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Waktu tunggu')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.supplier.leadTime}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Skor kualitas')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.supplier.qualityScore}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Skor kepatuhan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.supplier.complianceScore}%</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Audit berikutnya')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.supplier.nextAudit}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.supplier.contact}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Sertifikat')}</CardTitle></CardHeader>
			<CardContent class="flex flex-wrap gap-2.5 p-0 pt-4">
				{#each data.supplier.certificates as certificate}
					<Badge variant="outline">{certificate}</Badge>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Risks')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2 p-0 pt-4">
				<ul class="list-disc space-y-1.5 pl-5 text-sm text-muted-foreground">
					{#each data.supplier.risks ?? [] as risk}
						<li>{risk}</li>
					{/each}
				</ul>
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Produk terkait')}</Badge>
				<CardTitle>{t('Kapabilitas Produk')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.linkedProducts as product}
						<a href={`/products/${product.id}`} class="grid gap-1.5 rounded-lg border bg-muted/30 p-3.5 no-underline transition-colors hover:border-ring/40">
							<Badge variant={toneVariant(statusTone(product.status))} class="w-fit">{product.status}</Badge>
							<strong class="text-sm font-bold text-foreground">{product.name}</strong>
							<small class="text-sm text-muted-foreground">{product.packaging} · {product.readiness}% {t('siap')}</small>
						</a>
					{/each}
				</div>
				{#if evidenceRequested}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Permintaan bukti dikirim ke backend.')}</p>
				{/if}
				{#if verified}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Supplier diverifikasi di backend.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>