<script lang="ts">
	/**
	 * Input negara dengan pencarian (search + select).
	 *
	 * Memakai daftar negara dunia dari backend `/countries/` (sinkron dengan
	 * halaman lain), jadi nama & kode negara SELALU sama di seluruh aplikasi.
	 * Mendukung mode tunggal (`multiple=false`) dan multi (dipisah koma).
	 *
	 * `value` menyimpan NAMA negara kanonik (mis. "Japan") agar konsisten dengan
	 * nilai yang sudah tersimpan di data; opsi ditampilkan sebagai nama + kode/region.
	 */
	import { onMount } from 'svelte';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';
	import { t } from '$lib/i18n.svelte';
	import {
		loadWorldCountries,
		toCountryOptions,
		type CountryListItem
	} from '$lib/data/countries';

	let {
		value = $bindable(''),
		multiple = false,
		valueMode = 'name',
		placeholder,
		disabled = false,
		class: className = '',
		id = undefined,
		labelledby = undefined,
		label = undefined
	}: {
		/** Nilai negara: nama kanonik (default) atau kode ISO bila valueMode='code'. */
		value?: string;
		/** Mode multi: banyak negara dipisah koma. */
		multiple?: boolean;
		/** 'name' menyimpan nama kanonik, 'code' menyimpan kode ISO. */
		valueMode?: 'name' | 'code';
		placeholder?: string;
		disabled?: boolean;
		class?: string;
		id?: string;
		labelledby?: string;
		label?: string;
	} = $props();

	let countries = $state<CountryListItem[]>([]);
	let loading = $state(true);
	let failed = $state(false);

	onMount(async () => {
		try {
			countries = await loadWorldCountries();
		} catch {
			failed = true;
		} finally {
			loading = false;
		}
	});

	let options = $derived(toCountryOptions(countries));

	/** Ubah nama/kode apa pun menjadi kode ISO agar cocok dengan opsi select. */
	function toCode(input: string): string {
		const raw = (input ?? '').trim();
		if (!raw) return '';
		const upper = raw.toUpperCase();
		if (countries.some((c) => c.country_code.toUpperCase() === upper)) return upper;
		const byName = countries.find((c) => c.country_name.toLowerCase() === raw.toLowerCase());
		return byName ? byName.country_code : '';
	}

	function nameOf(code: string): string {
		return countries.find((c) => c.country_code === code)?.country_name ?? code;
	}

	/** Nilai yang disimpan untuk sebuah kode, sesuai valueMode. */
	function stored(code: string): string {
		return valueMode === 'code' ? code : nameOf(code);
	}

	// Mode tunggal: kode terpilih. Select menulis ke `pickedSingle`, lalu kita
	// simpan nama/kode kanoniknya ke `value`.
	let pickedSingle = $state('');
	$effect(() => {
		pickedSingle = toCode(value);
	});

	// Mode multi: daftar kode terpilih (dari value dipisah koma).
	let multiCodes = $derived(
		value
			.split(',')
			.map((s) => toCode(s))
			.filter(Boolean)
	);

	function addMulti(code: string) {
		if (!code || multiCodes.includes(code)) return;
		value = [...multiCodes, code].map(stored).join(', ');
	}

	function removeMulti(code: string) {
		value = multiCodes
			.filter((c) => c !== code)
			.map(stored)
			.join(', ');
	}
</script>

{#if multiple}
	<div class={`grid gap-2 ${className}`}>
		{#if multiCodes.length}
			<div class="flex flex-wrap gap-1.5">
				{#each multiCodes as code}
					<span class="inline-flex items-center gap-1.5 rounded-full border bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
						{nameOf(code)}
						<button
							type="button"
							class="text-primary/70 hover:text-primary"
							aria-label={`${t('Hapus')} ${nameOf(code)}`}
							onclick={() => removeMulti(code)}
						>
							×
						</button>
					</span>
				{/each}
			</div>
		{/if}
		<SearchableSelect
			{options}
			placeholder={placeholder ?? t('Tambah negara...')}
			{disabled}
			{id}
			{labelledby}
			{label}
			value={''}
			onchange={(code) => addMulti(code)}
		/>
	</div>
{:else}
	<div class={className}>
		<SearchableSelect
			{options}
			placeholder={placeholder ?? t('Pilih negara...')}
			{disabled}
			{id}
			{labelledby}
			{label}
			bind:value={pickedSingle}
			onchange={(code) => (value = code ? stored(code) : '')}
		/>
	</div>
{/if}

{#if loading}
	<p class="mt-1 text-xs text-muted-foreground">{t('Memuat daftar negara...')}</p>
{:else if failed}
	<p class="mt-1 text-xs text-destructive">{t('Gagal memuat daftar negara.')}</p>
{/if}
