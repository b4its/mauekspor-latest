<script lang="ts">
	import { t } from '$lib/i18n.svelte';
	import BotIcon from '@lucide/svelte/icons/bot';
	import SearchIcon from '@lucide/svelte/icons/search';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import BrainIcon from '@lucide/svelte/icons/brain';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import CheckIcon from '@lucide/svelte/icons/check';

	let step = $state(0);

	const steps = [
		{ label: t('Menganalisis pertanyaan...'), detail: t('Memahami konteks dan intent dari pertanyaan Anda') },
		{ label: t('Mencari data workspace...'), detail: t('Menelusuri produk, proyek, dan informasi relevan') },
		{ label: t('Memeriksa kepatuhan & regulasi...'), detail: t('Mengecek aturan ekspor, HS code, dan persyaratan') },
		{ label: t('Menyusun jawaban...'), detail: t('Merangkum informasi dalam format yang jelas') },
		{ label: t('Menyelesaikan...'), detail: t('Finalisasi dan formatting respons') },
	];

	let current = $derived(steps[step % steps.length]);

	$effect(() => {
		const interval = setInterval(() => {
			step = (step + 1);
			if (step >= steps.length * 2) step = steps.length - 1;
		}, 1800);
		return () => clearInterval(interval);
	});
</script>

<div class="flex items-start gap-2">
	<div class="shrink-0 rounded-full border bg-muted p-1.5">
		<BotIcon class="size-4" />
	</div>
	<div class="max-w-[92%] space-y-2 md:max-w-[75%]">
		<span class="text-xs font-bold text-muted-foreground">{t('Asisten')}</span>
		<div class="rounded-xl border bg-muted/50 px-4 py-3.5 space-y-2">
			<div class="flex items-start gap-2.5">
				<div class="shrink-0 pt-0.5">
					{#if step % 5 === 0}
						<SearchIcon class="size-4 text-primary/70" />
					{:else if step % 5 === 1}
						<FileTextIcon class="size-4 text-primary/70" />
					{:else if step % 5 === 2}
						<BrainIcon class="size-4 text-primary/70" />
					{:else if step % 5 === 3}
						<SparklesIcon class="size-4 text-primary/70" />
					{:else}
						<CheckIcon class="size-4 text-primary/70" />
					{/if}
				</div>
				<div class="min-w-0 flex-1">
					<p class="text-sm font-semibold text-foreground">{current.label}</p>
					<p class="text-xs text-muted-foreground mt-0.5">{current.detail}</p>
				</div>
				<span class="inline-flex gap-1 shrink-0 pt-1">
					<span class="size-1.5 animate-bounce rounded-full bg-primary/50 [animation-delay:0ms]"></span>
					<span class="size-1.5 animate-bounce rounded-full bg-primary/50 [animation-delay:150ms]"></span>
					<span class="size-1.5 animate-bounce rounded-full bg-primary/50 [animation-delay:300ms]"></span>
				</span>
			</div>
			<div class="h-1 overflow-hidden rounded-full bg-muted-foreground/10">
				<div class="h-full rounded-full bg-primary/60 transition-all duration-700" style="width: {Math.min(100, (step / (steps.length - 1)) * 100)}%"></div>
			</div>
		</div>
	</div>
</div>