<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { statusTone } from '$lib/utils/format';
	import { updateShipmentMilestone } from '$lib/api/shipments';

	let { data } = $props();
	let exceptionNote = $state('');
	let resolving = $state(false);
	let resolved = $state(false);
	let advanced = $state(false);
	let error = $state('');

	let displayStatus = $derived(resolved && data.shipment.status === 'Exception' ? 'Booking Requested' : advanced ? 'In Transit' : data.shipment.status);
	let displayProgress = $derived(advanced ? Math.min(data.shipment.progress + 18, 100) : data.shipment.progress);

	async function resolveException() {
		error = '';
		if (exceptionNote.trim().length < 8) {
			error = 'Tambahkan catatan resolusi minimal 8 karakter.';
			return;
		}
		resolving = true;
		try {
			await updateShipmentMilestone(data.shipment.id, 'Booking Requested');
			resolved = true;
		} catch {
			error = 'Gagal memperbarui milestone.';
		} finally {
			resolving = false;
		}
	}

	async function handleAdvance() {
		error = '';
		try {
			await updateShipmentMilestone(data.shipment.id, 'In Transit');
			advanced = true;
		} catch {
			error = 'Gagal memajukan milestone.';
		}
	}

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}
</script>

<svelte:head>
	<title>{data.shipment.id} | MauEkspor</title>
</svelte:head>

<AppShell title={data.shipment.id} eyebrow="Shipment tracking detail">
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.shipment.route}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.shipment.projectId} - {data.shipment.forwarder}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Shipment progress</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayProgress}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Shipment Facts</CardTitle>
					<CardDescription>Operational view for forwarder coordination, customs milestones, and exception ownership.</CardDescription>
				</div>
				<Button disabled={advanced} onclick={handleAdvance}>Advance milestone</Button>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Booking <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.bookingNo}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Mode <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.mode}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Container <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.container}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					ETA <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.eta}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Forwarder <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.forwarder}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					Route <strong class="mt-1 block text-sm font-bold text-foreground">{data.shipment.route}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>Milestone Timeline</CardTitle></CardHeader>
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
							<div class="flex items-center justify-between gap-2.5"><strong class="text-sm font-bold">Milestone Advanced</strong><Badge>Done</Badge></div>
							<p class="my-2 text-sm leading-relaxed text-muted-foreground">Milestone diperbarui di backend.</p>
							<small class="text-sm text-muted-foreground">Just now</small>
						</div>
					</div>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0">
				<Badge variant={data.shipment.exception && !resolved ? 'destructive' : 'default'} class="w-fit">
					{data.shipment.exception && !resolved ? 'Open exception' : 'No open exception'}
				</Badge>
				<CardTitle>Exception Handling</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 p-0 pt-4">
				<form class="grid gap-3" onsubmit={(event) => { event.preventDefault(); resolveException(); }}>
					<p class="text-muted-foreground">{resolved ? 'Exception diselesaikan di backend.' : data.shipment.exception ?? 'No active logistics issue for this shipment.'}</p>
					<div class="grid gap-2">
						<Label>Resolution note</Label>
						<Textarea bind:value={exceptionNote} rows={5} placeholder="Commercial team approved booking before rate expiry..." disabled={!data.shipment.exception || resolved} />
					</div>
					{#if error}
						<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					<Button type="submit" class="w-fit" disabled={!data.shipment.exception || resolving || resolved}>
						{resolving ? 'Resolving...' : resolved ? 'Resolved' : 'Resolve exception'}
					</Button>
				</form>
			</CardContent>
		</Card>
	</div>
</AppShell>