<script lang="ts">
	import SignupForm from '$lib/components/SignupForm.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import { t } from '$lib/i18n.svelte';
	import ShipIcon from '@lucide/svelte/icons/ship';
</script>

<svelte:head>
	<title>{t('Daftar')} | MauEkspor</title>
</svelte:head>

<div class="landing-font flex min-h-svh flex-col items-center justify-center gap-6 bg-[#eaf2ff] p-6 md:p-10 dark:bg-[#040d1f]">
	<div class="flex w-full max-w-sm flex-col gap-6">
		<div class="flex items-center justify-between">
			<a href="/" class="flex items-center gap-2 font-medium">
				<div class="flex size-8 items-center justify-center rounded-lg bg-[#0b3d91] text-white">
					<ShipIcon class="size-4" />
				</div>
				<span class="font-script text-2xl leading-none text-[#0b3d91] dark:text-[#5ea1ff]">MauEkspor</span>
			</a>
			<ThemeToggle />
		</div>
		<SignupForm />
	</div>
</div>
