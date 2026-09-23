<script lang="ts">
	import { getTheme, toggleTheme } from '$lib/stores/theme.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import SunIcon from '@lucide/svelte/icons/sun';
	import MoonIcon from '@lucide/svelte/icons/moon';

	let theme = $derived(getTheme());
</script>

<Button
	variant="ghost"
	size="icon"
	aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
	title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
	onclick={toggleTheme}
	class="bg-secondary"
>
	{#if theme === 'dark'}
		<SunIcon />
	{:else}
		<MoonIcon />
	{/if}
	<span class="sr-only">Toggle theme</span>
</Button>