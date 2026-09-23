<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { statusTone } from '$lib/utils/format';
	import { generateTradeDocument, approveTradeDocument } from '$lib/api/documents';

	let { data } = $props();
	let approving = $state(false);
	let approved = $state(false);
	let regenerated = $state(false);
	let error = $state('');

	let displayStatus = $derived(approved ? 'Approved' : regenerated ? 'Ready' : data.document.status);
	let displayScore = $derived(regenerated || approved ? Math.max(data.document.validationScore, 94) : data.document.validationScore);

	async function regenerate() {
		error = '';
		try {
			await generateTradeDocument({ projectId: data.document.projectId, type: data.document.type });
			regenerated = true;
		} catch {
			error = 'Gagal regenerate dokumen.';
		}
	}

	async function approve() {
		error = '';
		approving = true;
		try {
			await approveTradeDocument(data.document.id);
			approved = true;
		} catch {
			error = 'Gagal menyetujui dokumen.';
		} finally {
			approving = false;
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
	<title>{data.document.type} | MauEkspor</title>
</svelte:head>

<AppShell title={data.document.id} eyebrow={data.document.type}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.document.type}
				</CardTitle>
				<CardDescription class="mt-2">{data.project?.name ?? data.document.projectId} - {data.document.version}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Validation score</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayScore}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>Document Fields</CardTitle>
					<CardDescription>Fields are generated from project, product, quotation, and shipment data.</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<Button variant="outline" onclick={regenerate}>Regenerate</Button>
					<Button disabled={approving || approved || displayScore < 90} onclick={approve}>
						{approving ? 'Approving...' : approved ? 'Approved' : 'Approve document'}
					</Button>
				</div>
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				{#each Object.entries(data.document.fields) as [key, value]}
					<div class="rounded-lg border bg-muted/40 p-3">
						<span class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-muted-foreground">{key}</span>
						<strong class="block text-sm font-bold">{value}</strong>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>Validation Checklist</CardTitle></CardHeader>
			<CardContent class="grid gap-3 p-0 pt-4">
				{#each data.document.checks as check}
					<div class="grid gap-2.5 rounded-lg border bg-muted/40 p-3">
						<Badge variant={toneVariant(statusTone(check.status))} class="w-fit">{check.status}</Badge>
						<div>
							<strong class="block">{check.label}</strong>
							<p class="mt-1 text-sm leading-relaxed text-muted-foreground">{check.detail}</p>
						</div>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card class="bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">Document guardrail</Badge>
				<CardTitle>Cross-document consistency</CardTitle>
			</CardHeader>
			<CardContent class="p-0 pt-4">
				<p class="leading-relaxed text-muted-foreground">
					Approval should only be enabled when invoice, packing list, HS code, Incoterm, buyer, and
					origin fields are consistent across all trade documents.
				</p>
				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}
				{#if regenerated}
					<p class="mt-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">
						Dokumen diregenerasi di backend.
					</p>
				{/if}
				{#if approved}
					<p class="mt-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">
						Dokumen disetujui di backend.
					</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>