<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { statusTone } from '$lib/utils/format';
	import { uploadComplianceEvidence } from '$lib/api/compliance';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let evidenceNote = $state('');
	let fileName = $state('');
	let uploaded = $state(false);
	let verifying = $state(false);
	let verified = $state(false);
	let error = $state('');

	let displayStatus = $derived(verified ? 'Verified' : uploaded ? 'Evidence Uploaded' : data.requirement.status);

	async function uploadEvidence() {
		error = '';
		if (evidenceNote.trim().length < 8) {
			error = t('Tambahkan catatan evidence minimal 8 karakter.');
			return;
		}
		uploaded = true;
		try {
			await uploadComplianceEvidence({
				requirementId: data.requirement.id,
				note: evidenceNote.trim(),
				fileName: fileName.trim() || undefined
			});
		} catch {
			error = t('Gagal menyimpan bukti ke backend.');
			uploaded = false;
		}
	}

	function verifyEvidence() {
		verifying = true;
		window.setTimeout(() => {
			verifying = false;
			verified = true;
		}, 650);
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.requirement.title} | MauEkspor</title>
</svelte:head>

<AppShell title={data.requirement.id} eyebrow={t('Compliance requirement detail')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.requirement.title}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.requirement.projectId} - {data.product?.name ?? data.requirement.productId}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('AI confidence')}</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{data.requirement.confidence}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="p-0"><CardTitle>{t('Requirement Context')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 pt-4 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kategori')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.category}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tingkat keparahan')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.severity}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Pemilik')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.owner}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Jatuh tempo')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.due}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Sumber')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.source}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Tanggal sumber')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.requirement.sourceDate}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Required Evidence')}</CardTitle></CardHeader>
			<CardContent class="grid gap-3 p-0 pt-4">
				<p class="text-muted-foreground">{data.requirement.requiredEvidence}</p>
				<div class="rounded-lg border bg-muted/30 p-3.5">
					<span class="block text-xs font-bold uppercase tracking-wide text-muted-foreground">{t('Status saat ini')}</span>
					<strong class="mt-1 block text-sm font-bold">{uploaded ? evidenceNote : data.requirement.currentEvidence}</strong>
					{#if fileName}
						<small class="mt-1 block text-sm text-muted-foreground">{t('File terlampir:')} {fileName}</small>
					{/if}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Demo Unggah Bukti')}</CardTitle></CardHeader>
			<CardContent class="p-0 pt-4">
				<form class="grid gap-3.5" onsubmit={(event) => { event.preventDefault(); uploadEvidence(); }}>
					<div class="grid gap-2">
						<Label>{t('Catatan bukti')}</Label>
						<Textarea bind:value={evidenceNote} placeholder={t('Label artwork Jepang diunggah, ditinjau oleh importir...')} rows={5} />
					</div>
					<div class="grid gap-2">
						<Label>{t('Nama file')}</Label>
						<Input bind:value={fileName} placeholder="jp-label-artwork-v2.pdf" />
					</div>
					{#if error}
						<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					<div class="flex flex-wrap gap-2.5">
						<Button variant="outline" type="submit">{t('Simpan bukti')}</Button>
						<Button disabled={!uploaded || verifying || verified} onclick={verifyEvidence}>
							{verifying ? t('Memverifikasi...') : verified ? t('Terverifikasi') : t('Tandai terverifikasi')}
						</Button>
					</div>
				</form>
			</CardContent>
		</Card>
	</div>
</AppShell>