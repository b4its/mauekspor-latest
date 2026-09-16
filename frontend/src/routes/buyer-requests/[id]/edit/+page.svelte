<script lang="ts">
	import { untrack } from 'svelte';
	import AppShell from '$lib/components/AppShell.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { updateBuyerRequest } from '$lib/api/buyer-requests';

	let { data } = $props();
	const initial = $state.snapshot(untrack(() => data.request));
	let subject = $state(initial.subject);
	let destination = $state(initial.destination);
	let quantity = $state(initial.quantity);
	let deadline = $state(initial.deadline);
	let requirements = $state((initial.requirements ?? []).join('\n'));
	let saved = $state(false);
	let saving = $state(false);
	let error = $state('');

	let valid = $derived(subject.trim().length > 4 && destination.trim().length > 1 && quantity.trim().length > 1 && deadline);

	async function save() {
		error = '';
		if (!valid) {
			error = t('Lengkapi kolom wajib sebelum menyimpan.');
			return;
		}
		saving = true;
		try {
			await updateBuyerRequest(data.request.id, {
				subject,
				destination,
				quantity,
				deadline,
				requirements: requirements.split('\n').map((r) => r.trim()).filter(Boolean)
			});
			saved = true;
		} catch {
			error = t('Gagal menyimpan request ke backend.');
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Edit {data.request.subject} | MauEkspor</title>
</svelte:head>

<AppShell title={data.request.id} eyebrow={t('Edit buyer request')}>
	<Card class="panel-hero p-6 md:p-8">
		<CardHeader class="p-0">
			<Badge variant="secondary">{t('Permintaan inbound')}</Badge>
			<CardTitle class="mt-3 font-display text-4xl font-black tracking-tight text-[#0b1d3a] md:text-5xl dark:text-white">{t('Perbarui')} {initial.subject}.</CardTitle>
			<CardDescription class="mt-2 max-w-2xl leading-relaxed">
				{t('Jaga subjek, tujuan, jumlah, dan batas waktu tetap terkini agar mesin pencocokan tetap akurat.')}
			</CardDescription>
		</CardHeader>
	</Card>

	{#if saved}
		<Card class="grid gap-4">
			<CardHeader class="p-0">
				<Badge variant="secondary">{t('Permintaan disimpan')}</Badge>
				<CardTitle class="mt-3 text-3xl font-bold tracking-tight">{subject}</CardTitle>
				<CardDescription class="mt-2 leading-relaxed">
					{quantity} {t('ke')} {destination}. {t('Perubahan tersimpan & matching diperbarui di backend.')}
				</CardDescription>
			</CardHeader>
			<CardContent class="mt-6 flex flex-wrap items-center gap-3 p-0">
				<Button href={`/buyer-requests/${data.request.id}`}>{t('Kembali ke permintaan')}</Button>
			</CardContent>
		</Card>
	{:else}
		<Card>
			<form class="grid gap-4 p-1" onsubmit={(event) => { event.preventDefault(); save(); }}>
				<div class="grid gap-2">
					<Label for="br-subject">{t('Subjek')}</Label>
					<Input id="br-subject" bind:value={subject} />
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="grid gap-2">
						<Label for="br-dest">{t('Tujuan')}</Label>
						<Input id="br-dest" bind:value={destination} />
					</div>
					<div class="grid gap-2">
						<Label for="br-deadline">{t('Batas waktu')}</Label>
						<Input id="br-deadline" bind:value={deadline} type="date" />
					</div>
				</div>
				<div class="grid gap-2">
					<Label for="br-qty">{t('Jumlah')}</Label>
					<Input id="br-qty" bind:value={quantity} />
				</div>
				<div class="grid gap-2">
					<Label for="br-req">{t('Persyaratan (satu per baris)')}</Label>
					<Textarea id="br-req" bind:value={requirements} rows={3} />
				</div>

				{#if error}<p class="rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>{/if}

				<div class="flex flex-wrap gap-3">
					<Button variant="outline" href={`/buyer-requests/${data.request.id}`}>{t('Batal')}</Button>
					<Button type="submit" disabled={saving}>{saving ? t('Menyimpan...') : t('Simpan permintaan')}</Button>
				</div>
			</form>
		</Card>
	{/if}
</AppShell>