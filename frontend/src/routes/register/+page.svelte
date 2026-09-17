<script lang="ts">
	import SignupForm from '$lib/components/SignupForm.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import { t } from '$lib/i18n.svelte';
</script>

<svelte:head>
	<title>{t('Daftar')} | MauEkspor</title>
</svelte:head>

<div class="landing-font flex min-h-svh flex-col items-center justify-center gap-6 bg-[#eaf2ff] p-6 md:p-10 dark:bg-[#040d1f]">
	<div class="flex w-full max-w-sm flex-col gap-6">
		<div class="flex items-center justify-between">
			<Logo variant="landscape" class="justify-center" />
			<ThemeToggle />
		</div>
		<SignupForm />
	</div>
</div>
