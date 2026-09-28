<script lang="ts">
	/**
	 * Banner status data (PRD §5.11 G-09 "Truth in UI").
	 *
	 * Dipakai halaman list/detail untuk menampilkan dengan jelas ketika data
	 * berasal dari seed demo (mock) atau ketika server gagal dimuat — sehingga
	 * staf tidak salah mengira data lokal/fiktif sebagai data bisnis valid.
	 */
	import AlertTriangleIcon from '@lucide/svelte/icons/alert-triangle';
	import { t } from '$lib/i18n.svelte';

	let {
		usingFallback = false,
		error = '',
		class: className = ''
	}: {
		usingFallback?: boolean;
		error?: string;
		class?: string;
	} = $props();
</script>

{#if usingFallback}
	<div
		class={`flex items-start gap-2 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm font-semibold text-amber-800 dark:text-amber-300 ${className}`}
		role="alert"
		aria-live="polite"
	>
		<AlertTriangleIcon class="mt-0.5 size-4 shrink-0" />
		<span>{t('Mode demo: data di bawah berasal dari contoh lokal, bukan server. Jangan pakai untuk keputusan nyata.')}</span>
	</div>
{:else if error}
	<div class={`rounded-lg bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive ${className}`} role="alert">
		{error}
	</div>
{/if}
