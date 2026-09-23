<script lang="ts">
	import { onMount } from 'svelte';

	onMount(async () => {
		const AOS = (await import('aos')).default;
		AOS.init({
			duration: 700,
			easing: 'ease-out-cubic',
			once: true,
			offset: 60
		});
	});
</script>
