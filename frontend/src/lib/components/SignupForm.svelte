<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Field from '$lib/components/ui/field/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { NativeSelect } from '$lib/components/ui/native-select/index.js';
	import { register } from '$lib/stores/session.svelte';
	import type { UserRole } from '$lib/api/auth';
	import { cn } from '$lib/utils.js';
	import type { HTMLAttributes } from 'svelte/elements';
	import { t } from '$lib/i18n.svelte';

	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> = $props();

	const roleOptions: UserRole[] = ['Exporter', 'Buyer', 'Forwarder', 'CustomsBroker', 'Finance'];

	let role = $state<UserRole>('Exporter');
	let name = $state('');
	let organization = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');
	let message = $state('');

	let canSubmit = $derived(
		name.length > 1 &&
			organization.length > 1 &&
			email.includes('@') &&
			password.length >= 8 &&
			password === confirmPassword
	);

	async function submit() {
		error = '';
		message = '';

		if (!canSubmit) {
			error =
				password !== confirmPassword
					? t('Password dan konfirmasi password tidak sama.')
					: t('Lengkapi nama, organisasi, email valid, dan password minimal 8 karakter.');
			return;
		}

		loading = true;
		try {
			await register({ name, organization, role, email, password });
			window.location.href = '/dashboard';
		} catch (err) {
			error = err instanceof Error ? err.message : t('Gagal membuat akun. Silakan coba lagi.');
		} finally {
			loading = false;
		}
	}
</script>

<div class={cn('flex flex-col gap-6', className)} {...restProps}>
	<Card.Root class="border-[#0b3d91]/10 dark:border-white/10">
		<Card.Header class="text-center">
			<Card.Title class="text-xl">{t('Buat workspace Anda')}</Card.Title>
			<Card.Description>{t('Isi data di bawah untuk membuat akun ekspor-impor Anda')}</Card.Description>
		</Card.Header>
		<Card.Content>
			<form
				onsubmit={(event) => {
					event.preventDefault();
					submit();
				}}
			>
				<Field.Group>
					<Field.Field>
						<Field.Label for="name">{t('Nama Lengkap')}</Field.Label>
						<Input id="name" type="text" placeholder="Ayu Pratama" bind:value={name} required />
					</Field.Field>
					<Field.Field>
						<Field.Label for="organization">{t('Organisasi')}</Field.Label>
						<Input id="organization" type="text" placeholder="PT Kopi Gayo Nusantara" bind:value={organization} required />
					</Field.Field>
					<Field.Field>
						<Field.Label for="role">{t('Peran Utama')}</Field.Label>
						<NativeSelect id="role" bind:value={role} class="w-full">
						{#each roleOptions as item}
							<option>{item}</option>
						{/each}
					</NativeSelect>
					</Field.Field>
					<Field.Field>
						<Field.Label for="email">{t('Email')}</Field.Label>
						<Input id="email" type="email" placeholder="you@company.com" bind:value={email} required />
					</Field.Field>
					<Field.Field>
						<Field.Field class="grid grid-cols-2 gap-4">
							<Field.Field>
								<Field.Label for="password">{t('Kata sandi')}</Field.Label>
								<Input id="password" type="password" bind:value={password} required />
							</Field.Field>
							<Field.Field>
								<Field.Label for="confirm-password">{t('Konfirmasi Password')}</Field.Label>
								<Input id="confirm-password" type="password" bind:value={confirmPassword} required />
							</Field.Field>
						</Field.Field>
						<Field.Description>{t('Minimal 8 karakter.')}</Field.Description>
					</Field.Field>

					{#if error}
						<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					{#if message}
						<p class="rounded-lg border border-[#0b3d91]/30 bg-[#0b3d91]/10 px-3 py-2 text-sm font-bold text-[#0b3d91] dark:border-[#5ea1ff]/30 dark:bg-[#5ea1ff]/10 dark:text-[#5ea1ff]">{message}</p>
					{/if}

					<Field.Field>
						<Button type="submit" disabled={loading} class="bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">
							{loading ? t('Memproses...') : t('Buat Akun')}
						</Button>
						<Field.Description class="text-center">
							{t('Sudah punya akun?')} <a href="/login" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Masuk')}</a>
						</Field.Description>
					</Field.Field>
				</Field.Group>
			</form>
		</Card.Content>
	</Card.Root>
	<Field.Description class="px-6 text-center">
		{t('Dengan melanjutkan, Anda menyetujui')} <a href="##" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Ketentuan Layanan')}</a>
		{t('dan')} <a href="##" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Kebijakan Privasi')}</a> {t('kami.')}
	</Field.Description>
</div>
