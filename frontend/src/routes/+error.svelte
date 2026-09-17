<script lang="ts">
	import { page } from '$app/state';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import { t } from '$lib/i18n.svelte';
	import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';

	const status = $derived(page.status);
	const is404 = $derived(status === 404);
</script>

<svelte:head>
	<title>{status} | MauEkspor</title>
</svelte:head>

<div class="landing-font flex min-h-svh flex-col items-center justify-center gap-6 bg-[#eaf2ff] p-6 dark:bg-[#040d1f]">
	<div class="flex w-full max-w-md flex-col items-center gap-6 text-center">
		<Logo variant="landscape" href="/dashboard" />

		<div class="space-y-2">
			<h1 class="text-7xl font-black tracking-tight text-[#0b3d91] dark:text-[#5ea1ff]">{status}</h1>
			<h2 class="text-2xl font-bold tracking-tight text-[#0b1d3a] dark:text-white">
				{is404 ? t('Halaman tidak ditemukan') : t('Terjadi kesalahan')}
			</h2>
			<p class="text-sm leading-relaxed text-[#0b1d3a]/70 dark:text-white/70">
				{is404
					? t('Halaman yang Anda cari tidak ada atau telah dipindahkan.')
					: t('Maaf, terjadi kesalahan. Silakan coba lagi atau hubungi dukungan.')}
			</p>
		</div>

		<div class="flex flex-wrap items-center gap-3">
			<a
				href="/dashboard"
				class="inline-flex h-10 items-center gap-2 rounded-lg bg-[#0b3d91] px-5 text-sm font-bold text-white transition-colors hover:bg-[#0b3d91]/85"
			>
				<ArrowLeftIcon class="size-4" />
				{t('Kembali ke Dashboard')}
			</a>
			<ThemeToggle />
		</div>

		{#if !is404 && page.error?.message}
			<details class="w-full rounded-lg border border-[#0b3d91]/10 bg-white/70 p-3 text-left text-xs dark:border-white/10 dark:bg-[#0a1730]">
				<summary class="cursor-pointer font-bold text-[#0b1d3a]/60 dark:text-white/60">{t('Detail kesalahan')}</summary>
				<pre class="mt-2 overflow-x-auto text-[#0b1d3a]/70 dark:text-white/70">{page.error.message}</pre>
			</details>
		{/if}
	</div>
</div>