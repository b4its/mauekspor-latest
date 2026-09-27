<script lang="ts">
	import Logo from '$lib/components/Logo.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { fetchSession, getStatus } from '$lib/stores/session.svelte';
	import { t } from '$lib/i18n.svelte';

	let { children }: { children: import('svelte').Snippet } = $props();
	let authenticated = $derived(getStatus() === 'authenticated');

	$effect(() => {
		if (getStatus() === 'loading') fetchSession();
	});
</script>

<div class="landing-font min-h-svh bg-background text-foreground">
	<header class="sticky top-0 z-40 border-b border-border/70 bg-background/90 backdrop-blur-xl">
		<div class="mx-auto flex min-h-16 w-full max-w-[1440px] items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
			<a href="/" aria-label={t('MauEkspor Beranda')}><Logo variant="landscape" /></a>
			<nav class="flex items-center gap-2" aria-label={t('Navigasi publik')}>
				<Button href="/catalogs/public" variant="ghost" class="hidden sm:inline-flex">{t('Katalog')}</Button>
				<ThemeToggle />
				<Button href={authenticated ? '/dashboard' : '/login'} variant="outline">
					{authenticated ? t('Buka dashboard') : t('Masuk')}
				</Button>
				{#if !authenticated}
					<Button href="/register" class="hidden sm:inline-flex">{t('Daftar')}</Button>
				{/if}
			</nav>
		</div>
	</header>

	<main class="mx-auto flex w-full max-w-[1440px] flex-col gap-6 px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
		{@render children()}
	</main>

	<footer class="border-t border-border/70 px-4 py-6 text-center text-sm text-muted-foreground">
		<p>{t('MauEkspor - menghubungkan komoditas Indonesia dengan pasar global.')}</p>
	</footer>
</div>
