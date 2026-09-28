<script lang="ts">
	/**
	 * Kontrol pengurutan daftar yang bisa dipakai ulang.
	 *
	 * Menyediakan dua binding:
	 *  - `key`  : nama field yang diurutkan ('' = tanpa pengurutan).
	 *  - `dir`  : 'asc' | 'desc'.
	 *
	 * Halaman list memakai helper `sortBy()` dari `$lib/utils/sort` untuk
	 * menerapkan nilai ini. Saat pengguna memilih field baru, arah direset ke
	 * 'asc' agar hasil dapat diprediksi.
	 */
	import { NativeSelect, NativeSelectOption } from '$lib/components/ui/native-select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import ArrowUpIcon from '@lucide/svelte/icons/arrow-up';
	import ArrowDownIcon from '@lucide/svelte/icons/arrow-down';
	import { t } from '$lib/i18n.svelte';
	import type { SortDir, SortOption } from '$lib/utils/sort';

	let {
		key = $bindable<string>(''),
		dir = $bindable<SortDir>('asc'),
		options,
		placeholder = t('Urutkan'),
		class: className = ''
	}: {
		key?: string;
		dir?: SortDir;
		options: SortOption[];
		placeholder?: string;
		class?: string;
	} = $props();

	const id = $props.id();

	function handleChange(event: Event) {
		const value = (event.currentTarget as HTMLSelectElement).value;
		if (value !== key) dir = 'asc';
		key = value;
	}

	function flip() {
		dir = dir === 'asc' ? 'desc' : 'asc';
	}
</script>

<div class={`flex items-center gap-1.5 ${className}`} data-slot="sort-select">
	<label class="sr-only" for="sort-select-{id}">{placeholder}</label>
	<NativeSelect id="sort-select-{id}" value={key} onchange={handleChange} class="min-w-[10rem]" aria-label={placeholder}>
		<NativeSelectOption value="">{placeholder}</NativeSelectOption>
		{#each options as option (option.value)}
			<NativeSelectOption value={option.value}>{option.label}</NativeSelectOption>
		{/each}
	</NativeSelect>
	<Button
		variant="outline"
		size="sm"
		class="h-8 w-8 p-0"
		disabled={!key}
		aria-label={dir === 'asc' ? t('Urutan menaik') : t('Urutan menurun')}
		title={dir === 'asc' ? t('Urutan menaik') : t('Urutan menurun')}
		onclick={flip}
	>
		{#if dir === 'asc'}
			<ArrowUpIcon class="size-3.5" />
		{:else}
			<ArrowDownIcon class="size-3.5" />
		{/if}
	</Button>
</div>
