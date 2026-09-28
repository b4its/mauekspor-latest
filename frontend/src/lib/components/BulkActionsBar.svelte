<script lang="ts">
	/**
	 * Bar aksi massal yang muncul saat ada baris terpilih.
	 *
	 * Halaman list cukup mengoper jumlah terpilih dan aksi yang tersedia.
	 * Bar ini menangani: label jumlah, tombol hapus (destruktif) dengan status
	 * sibuk, tombol bersihkan pilihan, serta menyembunyikan dirinya saat tidak
	 * ada pilihan.
	 */
	import { Button } from '$lib/components/ui/button/index.js';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import XIcon from '@lucide/svelte/icons/x';
	import { t } from '$lib/i18n.svelte';

	let {
		count,
		busy = false,
		ondelete,
		onclear,
		/** Kata benda subjek, mis. "produk" untuk "3 produk dipilih". */
		noun = t('item')
	}: {
		count: number;
		busy?: boolean;
		ondelete: () => void;
		onclear: () => void;
		noun?: string;
	} = $props();
</script>

{#if count > 0}
	<div
		class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-primary/30 bg-primary/5 px-3 py-2"
		role="region"
		aria-label={t('Aksi massal')}
	>
		<span class="text-sm font-semibold text-foreground">{count} {noun} {t('dipilih')}</span>
		<div class="flex flex-wrap items-center gap-2">
			<Button size="sm" variant="destructive" disabled={busy} onclick={ondelete}>
				<Trash2Icon class="size-3.5 me-1" />
				{busy ? t('Menghapus...') : `${t('Hapus terpilih')} (${count})`}
			</Button>
			<Button size="sm" variant="ghost" disabled={busy} onclick={onclear}>
				<XIcon class="size-3.5 me-1" />
				{t('Bersihkan')}
			</Button>
		</div>
	</div>
{/if}
