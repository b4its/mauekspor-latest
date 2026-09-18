<script lang="ts">
 	import { Button } from '$lib/components/ui/button/index.js';
 	import * as Card from '$lib/components/ui/card/index.js';
 	import { FieldGroup, Field, FieldLabel, FieldDescription } from '$lib/components/ui/field/index.js';
 	import { Input } from '$lib/components/ui/input/index.js';
 	import { login } from '$lib/stores/session.svelte';
 	import { cn } from '$lib/utils.js';
 	import type { HTMLAttributes } from 'svelte/elements';
 	import { t } from '$lib/i18n.svelte';
 	import EyeIcon from '@lucide/svelte/icons/eye';
 	import EyeOffIcon from '@lucide/svelte/icons/eye-off';

 	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> = $props();

 	const id = $props.id();

 	let email = $state('');
 	let password = $state('');
 	let showPassword = $state(false);
 	let loading = $state(false);
 	let error = $state('');
 	let message = $state('');

 	let canSubmit = $derived(email.includes('@') && password.length >= 8);

 	async function submit() {
 		error = '';
 		message = '';

 		if (!canSubmit) {
 			error = t('Lengkapi data dengan email valid dan password minimal 8 karakter.');
 			return;
 		}

 		loading = true;
 		try {
 			await login({ email, password });
 			window.location.href = '/dashboard';
 		} catch (err) {
 			error = err instanceof Error ? err.message : t('Gagal masuk. Silakan coba lagi.');
 		} finally {
 			loading = false;
 		}
 	}
</script>

<div class={cn('flex flex-col gap-6', className)} {...restProps}>
	<Card.Root class="border-[#0b3d91]/10 dark:border-white/10">
		<Card.Header class="text-center">
			<Card.Title class="text-xl">{t('Selamat datang kembali')}</Card.Title>
			<Card.Description>{t('Masuk ke trade command center Anda')}</Card.Description>
		</Card.Header>
		<Card.Content>
			<form
				onsubmit={(event) => {
					event.preventDefault();
					submit();
				}}
			>
				<FieldGroup>
					<Field>
						<FieldLabel for="email-{id}">{t('Email')}</FieldLabel>
						<Input id="email-{id}" type="email" placeholder="you@company.com" bind:value={email} required />
					</Field>
					<Field>
						<div class="flex items-center">
							<FieldLabel for="password-{id}">{t('Kata sandi')}</FieldLabel>
							<span class="ms-auto text-sm text-muted-foreground">{t('Lupa password? Hubungi admin')}</span>
						</div>
						<div class="relative flex items-center">
							<div class="flex-1">
								<Input 
									id="password-{id}" 
									type={showPassword ? 'text' : 'password'} 
									placeholder={t('Minimum 8 karakter')} 
									bind:value={password} 
									required 
								/>
							</div>
							<button
								type="button"
								class="ml-2 p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
								onclick={() => (showPassword = !showPassword)}
								title={showPassword ? t('Sembunyikan') : t('Tampilkan')}
								aria-label={showPassword ? t('Sembunyikan password') : t('Tampilkan password')}
							>
								{#if showPassword}
									<EyeOffIcon class="size-4" />
								{:else}
									<EyeIcon class="size-4" />
								{/if}
							</button>
						</div>
					</Field>

					{#if error}
						<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					{#if message}
						<p class="rounded-lg border border-[#0b3d91]/30 bg-[#0b3d91]/10 px-3 py-2 text-sm font-bold text-[#0b3d91] dark:border-[#5ea1ff]/30 dark:bg-[#5ea1ff]/10 dark:text-[#5ea1ff]">{message}</p>
					{/if}

					<Field>
						<Button type="submit" disabled={loading} class="bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">
							{loading ? t('Memproses...') : t('Masuk')}
						</Button>
						<FieldDescription class="text-center">
							{t('Belum punya akun?')} <a href="/register" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Daftar')}</a>
						</FieldDescription>
					</Field>
				</FieldGroup>
			</form>
		</Card.Content>
	</Card.Root>
	<FieldDescription class="px-6 text-center">
		{t('Dengan melanjutkan, Anda menyetujui')} <a href="/about" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Ketentuan Layanan')}</a>
		{t('dan')} <a href="/about" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Kebijakan Privasi')}</a> {t('kami.')}
	</FieldDescription>
</div>
