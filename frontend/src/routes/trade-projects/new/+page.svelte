<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';
	import { Input } from '$lib/components/ui/input/index.js';
	
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { createTradeProject } from '$lib/api/trade-projects';
	import { t } from '$lib/i18n.svelte';

	const projectTypes = ['Exporter-led', 'Buyer RFQ', 'Forwarder-supported'];
	const steps = ['Scope', 'Product & Buyer', 'Commercial Terms'];

	function trStep(s: string) {
		return t(s === 'Scope' ? 'Lingkup' : s === 'Product & Buyer' ? 'Produk & Pembeli' : 'Ketentuan Komersial');
	}

	let step = $state(0);
	let projectType = $state('Exporter-led');
	let projectName = $state('');
	let destination = $state('');
	let product = $state('');
	let buyer = $state('');
	let incoterm = $state('');
	let targetValue = $state('');
	let eta = $state('');
	let created = $state(false);
	let error = $state('');

	let progress = $derived(Math.round(((step + 1) / steps.length) * 100));
	let currentValid = $derived(
		step === 0
			? projectName.trim().length > 2 && destination.trim().length > 1
			: step === 1
				? product.trim().length > 2 && buyer.trim().length > 1
				: incoterm.trim().length > 2 && Number(targetValue) > 0
	);

	async function next() {
		error = '';
		if (!currentValid) {
			error = t('Lengkapi field wajib pada langkah ini sebelum lanjut.');
			return;
		}

		if (step < steps.length - 1) {
			step += 1;
			return;
		}

		try {
			await createTradeProject({
				name: projectName,
				projectType,
				product,
				buyer,
				country: destination,
				incoterm,
				targetValue: Number(targetValue),
				eta: eta || undefined
			});
			created = true;
		} catch {
			error = t('Gagal membuat proyek. Coba lagi.');
		}
	}

	function back() {
		error = '';
		step = Math.max(0, step - 1);
	}
</script>

<svelte:head>
	<title>{t('Proyek Dagang Baru')} | MauEkspor</title>
</svelte:head>

<AppShell title="New Trade Project" eyebrow={t('Create export-import workspace')}>
	<div class="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(360px,0.72fr)]">
		<div class="space-y-6">
			<Badge>{t('Panduan penyiapan')}</Badge>
			<h2 class="font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Mulai dengan tujuan komersial, lalu lampirkan data produk dan kepatuhan.')}</h2>
			<p class="leading-relaxed text-muted-foreground">
				{t('Wizard ini membuat kontrak frontend untuk alur kerja backend di masa depan: simpan proyek, buat tugas awal, dan picu pekerjaan HS/kepatuhan secara asinkron.')}
			</p>

			<div class="stepper flex flex-wrap gap-2.5" aria-label="Wizard progress">
				{#each steps as item, index}
					<Button
						variant={step === index ? 'default' : 'outline'}
						onclick={() => (step = index)}
					>
						<span class="grid size-6 place-items-center rounded-full bg-primary/10 text-xs">{index + 1}</span>{trStep(item)}
					</Button>
				{/each}
			</div>

			<Card class="p-5">
				<Badge variant="secondary">{t('Pratinjau draf')}</Badge>
				<h3 class="mt-3 text-2xl font-bold tracking-tight">{projectName || t('Proyek ekspor tanpa judul')}</h3>
				<div class="mt-4 grid grid-cols-2 gap-3">
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Tipe')}<strong class="mt-1 block text-sm font-bold text-foreground">{projectType}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Tujuan')}<strong class="mt-1 block text-sm font-bold text-foreground">{destination || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Produk')}<strong class="mt-1 block text-sm font-bold text-foreground">{product || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Pembeli')}<strong class="mt-1 block text-sm font-bold text-foreground">{buyer || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Incoterm')}<strong class="mt-1 block text-sm font-bold text-foreground">{incoterm || '-'}</strong></div>
					<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">{t('Target')}<strong class="mt-1 block text-sm font-bold text-foreground">{targetValue ? `$${Number(targetValue).toLocaleString('en-US')}` : '-'}</strong></div>
				</div>
			</Card>
		</div>

		<Card class="h-fit">
			<form class="grid gap-4 p-6" onsubmit={(event) => { event.preventDefault(); next(); }}>
				<div class="progress-head flex items-center justify-between gap-3">
					<div>
						<span class="text-xs font-bold text-muted-foreground">{t('Langkah')} {step + 1} {t('dari')} {steps.length}</span>
						<strong class="mt-0.5 block text-xl font-bold tracking-tight">{trStep(steps[step])}</strong>
					</div>
					<b class="text-xl font-bold tracking-tight">{progress}%</b>
				</div>
				<Progress value={progress} />

				{#if created}
					<div class="rounded-xl border bg-muted/30 p-5">
						<Badge>{t('Draf dibuat')}</Badge>
						<h3 class="mt-3 text-2xl font-bold tracking-tight">{projectName}</h3>
						<p class="mt-1 leading-relaxed text-muted-foreground">
							{t('Proyek berhasil disimpan di backend. Selanjutnya timeline & compliance jobs akan menempel ke proyek ini secara asinkron.')}
						</p>
						<Button href="/trade-projects" class="mt-3 w-fit">{t('Kembali ke proyek')}</Button>
					</div>
				{:else}
					{#if step === 0}
						<div class="field grid gap-2">
							<Label>{t('Tipe proyek')}</Label>
							<SearchableSelect bind:value={projectType} options={[{value:'Exporter-led',label:'Exporter-led'},{value:'Buyer-led',label:'Buyer-led'},{value:'Joint',label:'Joint'}]} />
						</div>
						<div class="field grid gap-2">
							<Label>{t('Nama proyek')}</Label>
							<Input bind:value={projectName} placeholder="Japan Coffee Trial Shipment" />
						</div>
						<div class="field grid gap-2">
							<Label>{t('Negara tujuan')}</Label>
							<Input bind:value={destination} placeholder="Japan" />
						</div>
					{:else if step === 1}
						<div class="field grid gap-2">
							<Label>{t('Produk')}</Label>
							<Input bind:value={product} placeholder="Gayo Arabica Coffee Beans" />
						</div>
						<div class="field grid gap-2">
							<Label>{t('Pembeli atau prospek')}</Label>
							<Input bind:value={buyer} placeholder="Hikari Foods Co." />
						</div>
					{:else}
						<div class="field grid gap-2">
							<Label>{t('Incoterm target')}</Label>
							<Input bind:value={incoterm} placeholder="FOB Tanjung Priok" />
						</div>
						<div class="field grid gap-2">
							<Label>{t('Nilai target')}</Label>
							<Input bind:value={targetValue} inputmode="decimal" placeholder="42800" />
						</div>
						<div class="field grid gap-2">
							<Label>{t('Perkiraan tanggal pengiriman')}</Label>
							<Input bind:value={eta} type="date" />
						</div>
					{/if}

					{#if error}
						<p class="form-alert rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}

					<div class="wizard-actions flex flex-wrap items-center justify-between gap-3">
						<Button variant="outline" disabled={step === 0} type="button" onclick={back}>{t('Kembali')}</Button>
						<Button type="submit">{step === steps.length - 1 ? t('Buat draf proyek') : t('Lanjutkan')}</Button>
					</div>
				{/if}
			</form>
		</Card>
	</div>
</AppShell>
