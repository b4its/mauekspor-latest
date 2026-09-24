<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { statusTone } from '$lib/utils/format';
	import { updateShipmentMilestone, resolveShipmentException, updateShipment, deleteShipment } from '$lib/api/shipments';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n.svelte';

	let { data } = $props();
	let exceptionNote = $state('');
	let resolving = $state(false);
	let resolved = $state(false);
	let advanced = $state(false);
	let error = $state('');
	let message = $state('');
	let editing = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let editStatus = $state('');
	let editContainer = $state('');
	let editRoute = $state('');
	let savedStatus = $state('');
	let savedContainer = $state('');
	let savedRoute = $state('');
	let localContainer = $derived(savedContainer || data.shipment.container);
	let localRoute = $derived(savedRoute || data.shipment.route);

	let displayStatus = $derived(resolved && data.shipment.status === 'Exception' ? 'Booking Requested' : advanced ? 'In Transit' : savedStatus || data.shipment.status);
	let displayProgress = $derived(advanced ? Math.min(data.shipment.progress + 18, 100) : data.shipment.progress);

	async function resolveException() {
		error = '';
		if (exceptionNote.trim().length < 8) {
			error = t('Tambahkan catatan resolusi minimal 8 karakter.');
			return;
		}
		resolving = true;
		try {
			const res = await resolveShipmentException({
				shipmentId: data.shipment.id,
				note: exceptionNote.trim(),
				owner: 'Operations'
			});
			resolved = true;
			if (res.data?.status) savedStatus = res.data.status;
			message = t('Exception diselesaikan di backend.');
		} catch {
			error = t('Gagal menyelesaikan exception.');
		} finally {
			resolving = false;
		}
	}

	async function handleAdvance() {
		error = '';
		try {
			const res = await updateShipmentMilestone(data.shipment.id, 'In Transit');
			advanced = true;
			if (res.data?.status) savedStatus = res.data.status;
			message = t('Milestone diperbarui di backend.');
		} catch {
			error = t('Gagal memajukan milestone.');
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	function openEdit() {
		editStatus = savedStatus || data.shipment.status;
		editContainer = localContainer;
		editRoute = localRoute;
		error = '';
		editing = true;
	}

	async function handleSave() {
		error = '';
		if (!editRoute.trim()) {
			error = t('Rute wajib diisi.');
			return;
		}
		saving = true;
		try {
			const res = await updateShipment(data.shipment.id, {
				status: editStatus.trim() as (typeof data.shipment.status),
				container: editContainer.trim(),
				route: editRoute.trim()
			});
			savedStatus = res.data.status;
			savedContainer = res.data.container;
			savedRoute = res.data.route;
			message = t('Pengiriman diperbarui.');
			editing = false;
		} catch {
			error = t('Gagal menyimpan pengiriman.');
		} finally {
			saving = false;
		}
	}

	async function handleDelete() {
		error = '';
		if (!confirm(t('Hapus pengiriman ini secara permanen?'))) return;
		deleting = true;
		try {
			await deleteShipment(data.shipment.id);
			goto('/shipments');
		} catch {
			error = t('Gagal menghapus pengiriman.');
		} finally {
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>{data.shipment.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.shipment.id} eyebrow={t('Shipment tracking detail')}>
	<Card class="panel-hero p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">
					{localRoute}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.shipment.projectId} - {data.shipment.forwarder}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Shipment progress')}</span>
				<strong class="mt-1 block font-display text-4xl font-black tracking-tight text-[#0b1d3a] dark:text-white">{displayProgress}%</strong>
			</div>
		</div>
		<div class="mt-5 flex flex-wrap gap-2.5">
			<Button variant="outline" onclick={() => (editing ? (editing = false) : openEdit())}>{editing ? t('Batal') : t('Edit')}</Button>
			<Button variant="outline" class="text-destructive" disabled={deleting} onclick={handleDelete}>{deleting ? t('Menghapus...') : t('Hapus')}</Button>
		</div>
		{#if editing}
			<div class="mt-4 grid gap-3 rounded-xl border bg-muted/20 p-4">
				<div class="grid gap-2 sm:grid-cols-3">
					<label class="grid gap-1 text-sm font-semibold">
						{t('Status')}
						<Input bind:value={editStatus} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Container')}
						<Input bind:value={editContainer} />
					</label>
					<label class="grid gap-1 text-sm font-semibold">
						{t('Route')}
						<Input bind:value={editRoute} />
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
					<CardTitle>{t('Shipment Facts')}</CardTitle>
					<CardDescription>{t('Operational view for forwarder coordination, customs milestones, and exception ownership.')}</CardDescription>
				</div>
				<Button disabled={advanced} onclick={handleAdvance}>{t('Advance milestone')}</Button>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Booking')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.bookingNo}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Mode')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.mode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Container')} <strong class="mt-1 block text-sm font-bold text-foreground">{localContainer}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('ETA')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.eta}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Forwarder <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.forwarder}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Route')} <strong class="mt-1 block text-sm font-bold text-foreground">{localRoute}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Milestone Timeline')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 p-0 pt-4">
				{#each data.shipment.milestones as milestone}
					<div class="grid grid-cols-[auto_1fr] gap-3 rounded-lg border bg-muted/30 p-3.5">
						<span class={`mt-1 size-3 rounded-full ${statusTone(milestone.status) === 'green' ? 'bg-green-600' : statusTone(milestone.status) === 'orange' ? 'bg-orange-500' : statusTone(milestone.status) === 'red' ? 'bg-red-500' : 'bg-blue-600'}`}></span>
						<div>
							<div class="flex items-center justify-between gap-2.5">
								<strong class="text-sm font-bold">{milestone.label}</strong>
								<Badge variant={toneVariant(statusTone(milestone.status))}>{milestone.status}</Badge>
							</div>
							<p class="my-2 text-sm leading-relaxed text-muted-foreground">{milestone.note}</p>
							<small class="text-sm text-muted-foreground">{milestone.time}</small>
						</div>
					</div>
				{/each}
				{#if advanced}
					<div class="grid grid-cols-[auto_1fr] gap-3 rounded-lg border bg-muted/30 p-3.5">
						<span class="mt-1 size-3 rounded-full bg-green-600"></span>
						<div>
							<div class="flex items-center justify-between gap-2.5"><strong class="text-sm font-bold">{t('Milestone Advanced')}</strong><Badge>{t('Selesai')}</Badge></div>
							<p class="my-2 text-sm leading-relaxed text-muted-foreground">{t('Milestone diperbarui di backend.')}</p>
							<small class="text-sm text-muted-foreground">{t('Baru saja')}</small>
						</div>
					</div>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0">
				<Badge variant={data.shipment.exception && !resolved ? 'destructive' : 'default'} class="w-fit">
					{data.shipment.exception && !resolved ? t('Open exception') : t('No open exception')}
				</Badge>
				<CardTitle>{t('Exception Handling')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 p-0 pt-4">
				<form class="grid gap-3" onsubmit={(event) => { event.preventDefault(); resolveException(); }}>
					<p class="text-muted-foreground">{resolved ? t('Exception diselesaikan di backend.') : data.shipment.exception ?? t('No active logistics issue for this shipment.')}</p>
					<div class="grid gap-2">
						<Label>{t('Resolution note')}</Label>
						<Textarea bind:value={exceptionNote} rows={5} placeholder={t('Commercial team approved booking before rate expiry...')} disabled={!data.shipment.exception || resolved} />
					</div>
					{#if error}
						<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					<Button type="submit" class="w-fit" disabled={!data.shipment.exception || resolving || resolved}>
						{resolving ? t('Resolving...') : resolved ? t('Selesai') : t('Resolve exception')}
					</Button>
				</form>
			</CardContent>
		</Card>
	</div>
</AppShell>