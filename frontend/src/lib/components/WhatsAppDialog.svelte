<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { openWhatsApp, getWhatsAppTemplates } from '$lib/utils/whatsapp';
	import { t } from '$lib/i18n.svelte';

	let {
		phone = '',
		contactName = 'Anda',
		company = 'perusahaan kami'
	}: { phone?: string; contactName?: string; company?: string } = $props();

	let open = $state(false);
	const templates = getWhatsAppTemplates();
	let selected = $state(templates[0].text);

	function send() {
		const message = selected
			.replace(/\{name\}/g, contactName)
			.replace(/\{company\}/g, company);
		openWhatsApp(phone, message);
		open = false;
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		<Button variant="outline" size="sm">{t('Hubungi via WhatsApp')}</Button>
	</Dialog.Trigger>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>{t('Kirim pesan WhatsApp')}</Dialog.Title>
			<Dialog.Description>{t('Pilih template pesan untuk')} {contactName} ({company}).</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-2 px-6 pb-4">
			{#each templates as template}
				<button
					class={`rounded-lg border p-3 text-left text-sm transition-colors ${selected === template.text ? 'border-ring bg-primary/10' : 'bg-muted/30 hover:bg-muted/60'}`}
					onclick={() => (selected = template.text)}
				>
					<strong class="block text-xs text-muted-foreground">{template.label}</strong>
					<span class="mt-1 block leading-relaxed text-muted-foreground">{template.text}</span>
				</button>
			{/each}
		</div>
		<Dialog.Footer class="flex justify-between gap-2">
			<Dialog.Close>
				<Button variant="outline">{t('Batal')}</Button>
			</Dialog.Close>
			<Button onclick={send} disabled={!phone}>{t('Buka WhatsApp')}</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
