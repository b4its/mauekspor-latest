<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { currency, statusTone } from '$lib/utils/format';
	import { qualifyBuyer, logBuyerContact } from '$lib/api/buyers';
	import { t } from '$lib/i18n.svelte';
	import WhatsAppDialog from '$lib/components/WhatsAppDialog.svelte';

	let { data } = $props();
	let qualified = $state(false);
	let logged = $state(false);
	let error = $state('');
	let displayStatus = $derived(qualified && data.buyer.status === 'Lead' ? 'Qualified' : data.buyer.status);
	let displayScore = $derived(qualified ? Math.min(data.buyer.fitScore + 9, 100) : data.buyer.fitScore);

	function toneVariant(tone: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		if (tone === 'green') return 'default';
		if (tone === 'red') return 'destructive';
		if (tone === 'orange') return 'outline';
		return 'secondary';
	}

	async function handleQualify() {
		error = '';
		try {
			await qualifyBuyer(data.buyer.id);
			qualified = true;
		} catch {
			error = t('Gagal mengkualifikasi buyer.');
		}
	}

	async function handleLogContact() {
		error = '';
		try {
			await logBuyerContact(data.buyer.id, `Follow-up call recorded (${new Date().toISOString().slice(0, 10)})`);
			logged = true;
		} catch {
			error = t('Gagal mencatat kontak.');
		}
	}
</script>

<svelte:head>
	<title>{data.buyer.name} | MauEkspor</title>
</svelte:head>

<AppShell title={data.buyer.name} eyebrow={t('Buyer account')}>
	<Card class="bg-gradient-to-br from-background to-secondary/40 shadow-sm p-6 md:p-8">
		<div class="flex flex-wrap items-end justify-between gap-6">
			<div class="min-w-0">
				<Badge variant={toneVariant(statusTone(displayStatus))}>{displayStatus}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
					{data.buyer.segment}
				</CardTitle>
				<CardDescription class="mt-2">{data.buyer.country} · {data.buyer.paymentProfile}</CardDescription>
			</div>
			<div class="shrink-0 rounded-xl border bg-muted/30 px-5 py-4 text-right">
				<span class="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('Buyer fit')}</span>
				<strong class="mt-1 block text-4xl font-bold tracking-tight">{displayScore}%</strong>
			</div>
		</div>
	</Card>

	<div class="grid gap-4 md:grid-cols-2">
		<Card class="md:col-span-2">
			<CardHeader class="flex-row flex-wrap items-start justify-between gap-3">
				<div>
					<CardTitle>{t('Relationship Command')}</CardTitle>
					<CardDescription>{data.buyer.nextStep}</CardDescription>
				</div>
				<div class="flex flex-wrap gap-2.5">
					<WhatsAppDialog
						phone={data.buyer.contact?.phone ?? ''}
						contactName={data.buyer.contact?.name ?? data.buyer.name}
						company={data.buyer.name}
					/>
					<Button variant="outline" onclick={handleLogContact}>{logged ? t('Logged') : t('Log contact')}</Button>
					<Button onclick={handleQualify}>{qualified ? t('Qualified') : t('Qualify buyer')}</Button>
				</div>
				{#if error}
					<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
				{/if}
			</CardHeader>
			<CardContent class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Annual potential')} <strong class="mt-1 block text-sm font-bold text-foreground">{currency.format(data.buyer.estimatedAnnualValue)}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Last contact')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer.lastContact}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Kontak')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer.contact.name}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Role')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer.contact.role}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Email')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer.contact.email}</strong>
				</div>
				<div class="rounded-lg border bg-muted/40 p-3 text-xs font-bold text-muted-foreground">
					{t('Phone')} <strong class="mt-1 block text-sm font-bold text-foreground">{data.buyer.contact.phone}</strong>
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Buyer Signals')}</CardTitle></CardHeader>
			<CardContent class="grid gap-2.5 p-0 pt-4">
				{#each data.buyer.signals as signal}
					<div class="relative rounded-lg border bg-muted/30 p-3.5 pl-10">
						<span class={`absolute left-3.5 top-4 size-3 rounded-full ${signal.tone === 'green' ? 'bg-green-600' : signal.tone === 'orange' ? 'bg-orange-500' : signal.tone === 'red' ? 'bg-red-500' : 'bg-blue-600'}`}></span>
						<strong class="block text-sm font-bold">{signal.label}</strong>
						<p class="mt-1.5 text-sm text-muted-foreground">{signal.detail}</p>
					</div>
				{/each}
			</CardContent>
		</Card>

		<Card>
			<CardHeader class="p-0"><CardTitle>{t('Interested Products')}</CardTitle></CardHeader>
			<CardContent class="p-0 pt-4">
				<div class="flex flex-wrap gap-2.5">
					{#each data.buyer.interestedProducts as product}
						<Badge variant="outline">{product}</Badge>
					{/each}
				</div>
				<h3 class="mt-5 mb-2 text-lg font-bold tracking-tight">{t('Account Notes')}</h3>
				<ul class="list-disc space-y-1.5 pl-5 text-sm text-muted-foreground">
					{#each data.buyer.notes as note}<li>{note}</li>{/each}
				</ul>
			</CardContent>
		</Card>

		<Card class="md:col-span-2 bg-gradient-to-br from-primary/10 to-background">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Linked export work')}</Badge>
				<CardTitle>{t('Proyek')}</CardTitle>
			</CardHeader>
			<CardContent class="grid gap-3 pt-4">
				<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.linkedProjects as project}
						<a href={`/trade-projects/${project.id}`} class="grid gap-1.5 rounded-lg border bg-muted/30 p-3.5 no-underline transition-colors hover:border-ring/40">
							<span class="text-xs font-bold uppercase tracking-wide text-muted-foreground">{project.stage}</span>
							<strong class="text-sm font-bold text-foreground">{project.name}</strong>
							<small class="text-sm text-muted-foreground">{project.product} · {currency.format(project.value)}</small>
						</a>
					{/each}
				</div>
				{#if logged}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Aktivitas kontak dicatat ke backend.')}</p>
				{/if}
				{#if qualified}
					<p class="rounded-lg bg-primary/10 px-3 py-2 text-sm font-bold text-primary">{t('Kualifikasi buyer diperbarui di backend.')}</p>
				{/if}
			</CardContent>
		</Card>
	</div>
</AppShell>