<script lang="ts">
	/**
	 * Dialog konfirmasi aksi destruktif yang aksesibel.
	 *
	 * Menggantikan `window.confirm()` yang memblokir, tidak konsisten dengan
	 * design system, dan tidak menyampaikan konteks objek. Pola ini adalah
	 * variasi dari dialog hapus di `routes/messages/+page.svelte`.
	 */
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { t } from '$lib/i18n.svelte';
	import LoaderCircleIcon from '@lucide/svelte/icons/loader-circle';
	import TriangleAlertIcon from '@lucide/svelte/icons/triangle-alert';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';

	let {
		open = $bindable(false),
		title = t('Konfirmasi'),
		description = '',
		detail = '',
		confirmLabel = t('Hapus'),
		cancelLabel = t('Batal'),
		loading = false,
		destructive = true,
		onconfirm
	}: {
		open: boolean;
		title?: string;
		description?: string;
		/** Konteks objek (nama/id) yang akan ditampilkan monospace. */
		detail?: string;
		confirmLabel?: string;
		cancelLabel?: string;
		loading?: boolean;
		destructive?: boolean;
		onconfirm: () => void | Promise<void>;
	} = $props();

	const Icon = $derived(destructive ? Trash2Icon : TriangleAlertIcon);
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title class={destructive ? 'flex items-center gap-2 text-base text-destructive' : 'flex items-center gap-2 text-base'}>
				<Icon class="size-4 shrink-0" />
				<span>{title}</span>
			</Dialog.Title>
			<Dialog.Description class="text-sm">
				{description}
				{#if detail}
					<div class="my-2 rounded bg-muted p-2 font-mono text-xs break-all">{detail}</div>
				{/if}
				{#if destructive}
					<span class="font-semibold text-destructive">{t('Tindakan ini tidak dapat dibatalkan.')}</span>
				{/if}
			</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)} disabled={loading}>
				{cancelLabel}
			</Button>
			<Button variant={destructive ? 'destructive' : 'default'} onclick={onconfirm} disabled={loading}>
				{#if loading}
					<LoaderCircleIcon class="size-3.5 animate-spin" />
					<span class="ms-1.5">{t('Memproses...')}</span>
				{:else}
					{confirmLabel}
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
