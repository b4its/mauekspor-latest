<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import { FieldGroup, Field, FieldLabel, FieldDescription } from '$lib/components/ui/field/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { login } from '$lib/stores/session.svelte';
	import { cn } from '$lib/utils.js';
	import type { HTMLAttributes } from 'svelte/elements';

	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> = $props();

	const id = $props.id();

	let email = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state('');
	let message = $state('');

	let canSubmit = $derived(email.includes('@') && password.length >= 8);

	async function submit() {
		error = '';
		message = '';

		if (!canSubmit) {
			error = 'Lengkapi data dengan email valid dan password minimal 8 karakter.';
			return;
		}

		loading = true;
		try {
			await login({ email, password });
			window.location.href = '/dashboard';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Gagal masuk. Silakan coba lagi.';
		} finally {
			loading = false;
		}
	}
</script>

<div class={cn('flex flex-col gap-6', className)} {...restProps}>
	<Card.Root class="border-[#0b3d91]/10 dark:border-white/10">
		<Card.Header class="text-center">
			<Card.Title class="text-xl">Selamat datang kembali</Card.Title>
			<Card.Description>Masuk ke trade command center Anda</Card.Description>
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
						<FieldLabel for="email-{id}">Email</FieldLabel>
						<Input id="email-{id}" type="email" placeholder="you@company.com" bind:value={email} required />
					</Field>
					<Field>
						<div class="flex items-center">
							<FieldLabel for="password-{id}">Password</FieldLabel>
							<a href="##" class="ms-auto text-sm text-[#0b3d91] underline-offset-4 hover:underline dark:text-[#5ea1ff]">
								Lupa password?
							</a>
						</div>
						<Input id="password-{id}" type="password" placeholder="Minimum 8 karakter" bind:value={password} required />
					</Field>

					{#if error}
						<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
					{/if}
					{#if message}
						<p class="rounded-lg border border-[#0b3d91]/30 bg-[#0b3d91]/10 px-3 py-2 text-sm font-bold text-[#0b3d91] dark:border-[#5ea1ff]/30 dark:bg-[#5ea1ff]/10 dark:text-[#5ea1ff]">{message}</p>
					{/if}

					<Field>
						<Button type="submit" disabled={loading} class="bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">
							{loading ? 'Memproses...' : 'Masuk'}
						</Button>
						<FieldDescription class="text-center">
							Belum punya akun? <a href="/register" class="text-[#0b3d91] dark:text-[#5ea1ff]">Daftar</a>
						</FieldDescription>
					</Field>
				</FieldGroup>
			</form>
		</Card.Content>
	</Card.Root>
	<FieldDescription class="px-6 text-center">
		Dengan melanjutkan, Anda menyetujui <a href="##" class="text-[#0b3d91] dark:text-[#5ea1ff]">Ketentuan Layanan</a>
		dan <a href="##" class="text-[#0b3d91] dark:text-[#5ea1ff]">Kebijakan Privasi</a> kami.
	</FieldDescription>
</div>
