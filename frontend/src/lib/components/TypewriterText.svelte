<script lang="ts">
	import { tick } from 'svelte';
	import { MarkdownRenderer } from '$lib/components/MarkdownRenderer';

	let { text = '', speed = 25, onComplete }: {
		text?: string;
		speed?: number;
		onComplete?: () => void;
	} = $props();

	let displayed = $state('');
	let idx = $state(0);

	$effect(() => {
		// Reset saat text berubah
		displayed = '';
		idx = 0;
	});

	$effect(() => {
		if (!text || idx >= text.length) return;
		const timer = setInterval(() => {
			if (idx < text.length) {
				idx += 1;
				displayed = text.slice(0, idx);
			} else {
				clearInterval(timer);
				onComplete?.();
			}
		}, speed);
		return () => clearInterval(timer);
	});

	// Trigger tick untuk auto-scroll saat text bertambah
	$effect(() => {
		if (displayed) tick();
	});
</script>

{#if displayed}
	<MarkdownRenderer text={displayed} />
{/if}