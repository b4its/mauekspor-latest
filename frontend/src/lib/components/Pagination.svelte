<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import { t } from '$lib/i18n.svelte';

	let {
		page = $bindable(1),
		totalPages = $bindable(1),
		pageSize = $bindable(20),
		totalItems = 0
	}: {
		page: number;
		totalPages: number;
		pageSize?: number;
		totalItems?: number;
	} = $props();

	const pageSizes = [5, 8, 12, 20, 50, 100];

	function goNext() { if (page < totalPages) page++; }
	function goPrev() { if (page > 1) page--; }
	function goTo(p: number) { if (p >= 1 && p <= totalPages) page = p; }

	// Generate page numbers to show (max 7)
	let pages = $derived.by(() => {
		const total = totalPages;
		const current = page;
		if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
		const out: (number | 'ellipsis')[] = [1];
		if (current > 3) out.push('ellipsis');
		const start = Math.max(2, current - 1);
		const end = Math.min(total - 1, current + 1);
		for (let i = start; i <= end; i++) out.push(i);
		if (current < total - 2) out.push('ellipsis');
		if (total > 1) out.push(total);
		return out;
	});
</script>

<div class="flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-muted/20 px-4 py-3">
	<div class="flex items-center gap-2 text-sm text-muted-foreground">
		<span>{t('Total')}: <strong class="text-foreground">{totalItems}</strong></span>
		<span class="hidden sm:inline">—</span>
		<label class="hidden items-center gap-1.5 sm:flex">
			<span class="text-xs">{t('Per halaman')}</span>
			<NativeSelect bind:value={pageSize} class="h-8 w-20 text-xs">
				{#each pageSizes as s}
					<option value={s}>{s}</option>
				{/each}
			</NativeSelect>
		</label>
	</div>

	<nav class="flex items-center gap-1" aria-label="Pagination">
		<Button variant="outline" size="sm" class="h-8 w-8 p-0" disabled={page <= 1} onclick={goPrev}>
			<ChevronLeftIcon class="size-4" />
		</Button>
		{#each pages as p}
			{#if p === 'ellipsis'}
				<span class="px-1 text-xs text-muted-foreground">…</span>
			{:else}
				<Button
					variant={p === page ? 'default' : 'outline'}
					size="sm"
					class="h-8 min-w-8 px-2"
					onclick={() => goTo(p)}
				>
					{p}
				</Button>
			{/if}
		{/each}
		<Button variant="outline" size="sm" class="h-8 w-8 p-0" disabled={page >= totalPages} onclick={goNext}>
			<ChevronRightIcon class="size-4" />
		</Button>
	</nav>
</div>