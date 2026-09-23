<script lang="ts">
	import { getTheme, toggleTheme } from '$lib/stores/theme.svelte';
	import { t } from '$lib/i18n.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import SunIcon from '@lucide/svelte/icons/sun';
	import MoonIcon from '@lucide/svelte/icons/moon';

	let theme = $derived(getTheme());
</script>

<Button
	variant="ghost"
	size="icon"
	aria-label={theme === 'dark' ? t('Beralih ke tema terang') : t('Beralih ke tema gelap')}
	title={theme === 'dark' ? t('Beralih ke tema terang') : t('Beralih ke tema gelap')}
	onclick={toggleTheme}
	class="bg-secondary"
>
	{#if theme === 'dark'}
		<SunIcon />
	{:else}
		<MoonIcon />
	{/if}
	<span class="sr-only">{t('Beralih tema')}</span>
</Button>