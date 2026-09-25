<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { useSidebar } from '$lib/components/ui/sidebar/index.js';
	import Logo from '$lib/components/Logo.svelte';
	import { t } from '$lib/i18n.svelte';
	import { logout, getUser } from '$lib/stores/session.svelte';

	import LayoutDashboardIcon from '@lucide/svelte/icons/layout-dashboard';
	import DatabaseIcon from '@lucide/svelte/icons/database';
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import UsersIcon from '@lucide/svelte/icons/users';
	import ScrollTextIcon from '@lucide/svelte/icons/scroll-text';
	import KeyIcon from '@lucide/svelte/icons/key';
	import Settings2Icon from '@lucide/svelte/icons/settings-2';
	import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
	import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
	import LogOutIcon from '@lucide/svelte/icons/log-out';

	const sidebar = useSidebar();
	const currentUser = $derived(getUser());
	const displayName = $derived(currentUser?.name ?? currentUser?.email ?? 'Admin');

	// Navigasi panel Admin — ini sidebar KHUSUS admin, menggantikan sidebar utama
	// sehingga /admin adalah panel tersendiri (bukan halaman di dalam app shell
	// yang menambah kolom sidebar kedua).
	const adminNav: { label: string; href: string; icon: typeof DatabaseIcon }[] = [
		{ label: 'Dasbor Admin', href: '/admin', icon: LayoutDashboardIcon },
		{ label: 'Studio Database', href: '/admin#studio', icon: DatabaseIcon },
		{ label: 'Negara & Regulasi', href: '/admin/countries', icon: GlobeIcon },
		{ label: 'Pengguna', href: '/users', icon: UsersIcon },
		{ label: 'Audit Log', href: '/audit', icon: ScrollTextIcon },
		{ label: 'Kunci API', href: '/api-keys', icon: KeyIcon },
		{ label: 'Pengaturan', href: '/settings', icon: Settings2Icon }
	];

	function isActive(href: string) {
		const clean = href.split('#')[0];
		if (clean === '/admin') return page.url.pathname === '/admin';
		return page.url.pathname === clean || page.url.pathname.startsWith(clean + '/');
	}
</script>

<Sidebar.Root collapsible="icon" class="landing-font">
	<Sidebar.Header>
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton size="lg" tooltipContent={t('Panel Admin')}>
					{#snippet child({ props }: { props: Record<string, unknown> })}
						<a {...props} href="/admin" class="flex items-center gap-2.5">
							<Logo variant="logo" class="hidden shrink-0 group-data-[collapsible=icon]:block" />
							<div class="grid flex-1 text-left leading-tight group-data-[collapsible=icon]:hidden">
								<span class="truncate text-sm font-bold">{t('Panel Admin')}</span>
								<span class="truncate text-xs text-sidebar-foreground/60">MauEkspor</span>
							</div>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Header>

	<Sidebar.Content>
		<Sidebar.Group>
			<Sidebar.GroupLabel>{t('Administrasi')}</Sidebar.GroupLabel>
			<Sidebar.Menu>
				{#each adminNav as item (item.href)}
					{@const NavIcon = item.icon}
					<Sidebar.MenuItem>
						<Sidebar.MenuButton isActive={isActive(item.href)} tooltipContent={t(item.label)}>
							{#snippet child({ props }: { props: Record<string, unknown> })}
								<a {...props} href={item.href} onclick={() => sidebar.setOpenMobile(false)}>
									<NavIcon class="size-4 shrink-0" />
									<span>{t(item.label)}</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
				{/each}
			</Sidebar.Menu>
		</Sidebar.Group>

		<Sidebar.Group>
			<Sidebar.GroupLabel>{t('Navigasi')}</Sidebar.GroupLabel>
			<Sidebar.Menu>
				<Sidebar.MenuItem>
					<Sidebar.MenuButton tooltipContent={t('Kembali ke aplikasi')}>
						{#snippet child({ props }: { props: Record<string, unknown> })}
							<a {...props} href="/dashboard" onclick={() => sidebar.setOpenMobile(false)}>
								<ArrowLeftIcon class="size-4 shrink-0" />
								<span>{t('Kembali ke aplikasi')}</span>
							</a>
						{/snippet}
					</Sidebar.MenuButton>
				</Sidebar.MenuItem>
			</Sidebar.Menu>
		</Sidebar.Group>
	</Sidebar.Content>

	<Sidebar.Footer>
		<div
			class="rounded-xl border border-sidebar-border bg-gradient-to-br from-[#0b3d91]/10 to-[#1e63d6]/5 p-3 shadow-xs group-data-[collapsible=icon]:hidden dark:from-white/10 dark:to-white/5"
		>
			<Badge variant="outline" class="gap-1 border-[#0b3d91]/30 bg-[#0b3d91]/10 text-[#0b3d91] dark:border-white/30 dark:bg-white/10 dark:text-white">
				<ShieldCheckIcon class="size-3" />
				<span>{t('Akses Admin')}</span>
			</Badge>
			<p class="mt-2 text-[13px] leading-snug text-sidebar-foreground/70">
				{t('Panel ini hanya untuk peran Admin.')}
			</p>
		</div>

		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton size="lg" tooltipContent={t('Keluar')} onclick={async () => { await logout(); await goto('/login'); }}>
					{#snippet child({ props }: { props: Record<string, unknown> })}
						<button {...props} class="w-full">
							<LogOutIcon class="size-4 shrink-0" />
							<div class="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
								<span class="truncate font-medium">{displayName}</span>
								<span class="truncate text-xs text-sidebar-foreground/60">{t('Keluar')}</span>
							</div>
						</button>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
