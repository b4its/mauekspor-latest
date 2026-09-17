<script lang="ts">
	import { getTheme } from '$lib/stores/theme.svelte';

	// variant: 'landscape' (logo + text) atau 'logo' (ikon saja)
	let {
		variant = 'landscape',
		class: className = '',
		href = '/'
	}: { variant?: 'landscape' | 'logo'; class?: string; href?: string } = $props();

	let theme = $derived(getTheme());
	let src = $derived(
		variant === 'landscape'
			? theme === 'dark'
				? '/images/logo/logoDarklscape.png'
				: '/images/logo/logoLightlscape.png'
			: theme === 'dark'
				? '/images/logo/logoDark.png'
				: '/images/logo/logoLight.png'
	);
	let alt = $derived('MauEkspor');
</script>

{#if href}
	<a href={href} class={`inline-flex items-center ${className}`} aria-label={alt}>
		<img
			src={src}
			alt={alt}
			class={variant === 'landscape' ? 'h-8 w-auto sm:h-9 md:h-10' : 'h-8 w-auto sm:h-9'}
			draggable="false"
		/>
	</a>
{:else}
	<img src={src} alt={alt} class={variant === 'landscape' ? 'h-8 w-auto sm:h-9 md:h-10' : 'h-8 w-auto sm:h-9'} draggable="false" />
{/if}