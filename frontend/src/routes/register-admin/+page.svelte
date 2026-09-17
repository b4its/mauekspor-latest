<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Field, FieldGroup, FieldLabel } from '$lib/components/ui/field/index.js';
	import { registerAdmin } from '$lib/api/auth';
	import { setAccessToken, setRefreshToken } from '$lib/api/client';
	import { fetchSession } from '$lib/stores/session.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import { t } from '$lib/i18n.svelte';

	let email = $state('');
	let password = $state('');
	let adminCode = $state('');
	let loading = $state(false);
	let error = $state('');
	let success = $state(false);

	async function submit() {
		error = '';
		if (!email || password.length < 8 || !adminCode) {
			error = t('Lengkapi semua field (email, password min 8 karakter, dan kode admin).');
			return;
		}
		loading = true;
		try {
			const res = await registerAdmin({
				name: 'Admin',
				email,
				password,
				role: 'Admin',
				organization: '',
				admin_code: adminCode,
			});
			if (res.meta?.access_token) {
				setAccessToken(res.meta.access_token as string);
			}
			if (res.meta?.refresh_token) {
				setRefreshToken(res.meta.refresh_token as string);
			}
			await fetchSession();
			success = true;
		} catch (err) {
			error = err instanceof Error ? err.message : t('Gagal mendaftarkan admin. Periksa kode admin.');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{t('Register Admin')} | MauEkspor</title>
</svelte:head>

<div class="landing-font flex min-h-svh flex-col items-center justify-center gap-6 bg-[#eaf2ff] p-6 md:p-10 dark:bg-[#040d1f]">
	<div class="flex w-full max-w-sm flex-col gap-6">
		<div class="flex items-center justify-between">
			<Logo variant="landscape" class="justify-center" />
			<ThemeToggle />
		</div>

		{#if success}
			<Card>
				<CardHeader>
					<Badge variant="secondary">{t('Berhasil')}</Badge>
					<CardTitle class="mt-2">{t('Admin berhasil didaftarkan!')}</CardTitle>
				</CardHeader>
				<CardContent class="grid gap-3">
					<p class="text-sm leading-relaxed text-muted-foreground">{t('Sekarang Anda bisa login dengan email dan password yang baru saja dibuat.')}</p>
					<Button href="/login">{t('Masuk')}</Button>
				</CardContent>
			</Card>
		{:else}
			<Card class="border-[#0b3d91]/10 dark:border-white/10">
				<CardHeader class="text-center">
					<Badge variant="secondary" class="w-fit mx-auto">{t('Bootstrap Admin')}</Badge>
					<CardTitle class="mt-2">{t('Daftarkan Admin Baru')}</CardTitle>
				</CardHeader>
				<CardContent>
					<form onsubmit={(e) => { e.preventDefault(); submit(); }}>
						<FieldGroup>
							<Field>
								<FieldLabel>{t('Email Admin')}</FieldLabel>
								<Input type="email" placeholder="admin@company.com" bind:value={email} required />
							</Field>
							<Field>
								<FieldLabel>{t('Password')}</FieldLabel>
								<Input type="password" placeholder={t('Minimal 8 karakter')} bind:value={password} required />
							</Field>
							<Field>
								<FieldLabel>{t('Kode Admin')}</FieldLabel>
								<Input type="password" placeholder="******" bind:value={adminCode} required />
								<p class="mt-1 text-xs text-muted-foreground">{t('Kode bootstrap dari file .env (MAUEKSPOR_ADMIN_CODE).')}</p>
							</Field>
							{#if error}
								<p class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-bold text-destructive">{error}</p>
							{/if}
							<Button type="submit" disabled={loading} class="mt-2 w-full bg-[#0b3d91] text-white hover:bg-[#0b3d91]/85">
								{loading ? t('Memproses...') : t('Daftarkan Admin')}
							</Button>
						</FieldGroup>
					</form>
					<p class="mt-4 text-center text-xs text-muted-foreground">
						<a href="/login" class="text-[#0b3d91] dark:text-[#5ea1ff]">{t('Kembali ke login')}</a>
					</p>
				</CardContent>
			</Card>
		{/if}
	</div>
</div>