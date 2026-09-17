<script lang="ts">
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import AppSidebar from '$lib/components/AppSidebar.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { activities, navItems } from '$lib/data/trade';

	import SearchIcon from '@lucide/svelte/icons/search';
	import ActivityIcon from '@lucide/svelte/icons/activity';
	import BellIcon from '@lucide/svelte/icons/bell';
	import ArrowRightLeftIcon from '@lucide/svelte/icons/arrow-right-left';
	import MenuIcon from '@lucide/svelte/icons/menu';
	import { getStatus, getUser, logout, fetchSession } from '$lib/stores/session.svelte';
	import { listNotifications } from '$lib/api/notifications';
import { t, i18n, toggleLocale } from '$lib/i18n.svelte';

	let { title = 'Overview', eyebrow = 'Export-import command center', children } = $props();
	let commandOpen = $state(false);
	let activityOpen = $state(false);
	let commandQuery = $state('');
	let loggingOut = $state(false);

	$effect(() => {
		fetchSession();
	});

	let user = $derived(getUser());
	let userStatus = $derived(getStatus());

	async function handleLogout() {
		loggingOut = true;
		await logout();
		window.location.href = '/login';
	}

	function trGroup(g: string) {
		const map: Record<string, string> = {
			Navigation: 'Navigasi', 'Trade Project': 'Proyek Dagang', Product: 'Produk', Buyer: 'Pembeli', Supplier: 'Pemasok', Task: 'Tugas', Report: 'Laporan', Integration: 'Integrasi', Template: 'Template', Automation: 'Automasi', Knowledge: 'Pengetahuan', Calendar: 'Kalender', File: 'File', Message: 'Pesan', Billing: 'Tagihan', Support: 'Dukungan', 'API Key': 'Kunci API', 'Business Profile': 'Profil Bisnis', User: 'Pengguna', 'Buyer Request': 'Permintaan Pembeli', Forwarder: 'Forwarder', Educational: 'Edukasi', Chat: 'Chat', 'Export Analysis': 'Analisis Ekspor'
		};
		return t(map[g] ?? g);
	}

	let commands = $derived([
		...navItems.map((item) => ({ label: item.label, href: item.href, group: 'Navigation' })),
		{ label: 'Dashboard', href: '/dashboard', group: 'Navigation' },
		{ label: 'Products', href: '/products', group: 'Navigation' },
		{ label: 'Export Analysis', href: '/export-analysis', group: 'Navigation' },
		{ label: 'Catalogs', href: '/catalogs', group: 'Navigation' },
		{ label: 'Costing', href: '/costing', group: 'Navigation' },
		{ label: 'Buyer Requests', href: '/buyer-requests', group: 'Navigation' },
		{ label: 'Forwarders', href: '/forwarders', group: 'Navigation' },
		{ label: 'Buyers', href: '/buyers', group: 'Navigation' },
		{ label: 'Educational', href: '/educational', group: 'Navigation' },
		{ label: 'Chat', href: '/chat', group: 'Navigation' },
		{ label: 'Marketing', href: '/marketing', group: 'Navigation' },
		{ label: 'Settings', href: '/settings', group: 'Navigation' },
		{ label: 'Register Admin', href: '/register-admin', group: 'Navigation' },
	]);
	// Catatan: pencarian data live menggunakan API /search/?q= langsung (liveResults),
	// sehingga data dari seed tidak perlu diimpor ke AppShell lagi.
	let activityCount = $derived(activities.length);
	let unreadCount = $state(0);
	let liveResults = $state<{ label: string; href: string; group: string; sub?: string }[]>([]);
	const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

	$effect(() => {
		async function refreshNotifications() {
			try {
				const res = await listNotifications();
				unreadCount = res.data.filter((n) => n.status === 'Unread').length;
			} catch {
				unreadCount = 0;
			}
		}
		refreshNotifications();

		// Realtime: SSE stream (cookie auth), fallback polling 30 detik
		let timer: ReturnType<typeof setInterval> | undefined;
		let source: EventSource | undefined;
		try {
			source = new EventSource(`${API_BASE}/notifications/stream/`, { withCredentials: true });
			source.addEventListener('unread', (ev) => {
				try {
					const payload = JSON.parse((ev as MessageEvent).data);
					unreadCount = payload.unread_count;
				} catch {
					/* abaikan event malformed */
				}
			});
			source.onerror = () => {
				source?.close();
				source = undefined;
				timer = setInterval(refreshNotifications, 30_000);
			};
		} catch {
			timer = setInterval(refreshNotifications, 30_000);
		}
		return () => {
			source?.close();
			if (timer) clearInterval(timer);
		};
	});

	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	$effect(() => {
		const q = commandQuery.trim();
		if (q.length < 2) {
			liveResults = [];
			return;
		}
		clearTimeout(searchTimer);
		searchTimer = setTimeout(async () => {
			try {
				const res = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(q)}`, { credentials: 'include' });
				if (res.ok) {
					const body = await res.json();
					liveResults = (body.data ?? []) as typeof liveResults;
				}
			} catch {
				liveResults = [];
			}
		}, 250);
	});

	let filteredCommands = $derived<{ label: string; href: string; group: string; sub?: string }[]>([
		...liveResults,
		...commands
			.filter((item) => item.label.toLowerCase().includes(commandQuery.trim().toLowerCase()))
			.slice(0, 8 - liveResults.length)
	]);
</script>

<svelte:window
	onkeydown={(event) => {
		if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
			event.preventDefault();
			commandOpen = true;
		}
	}}
/>

<Sidebar.Provider>
	<AppSidebar />

	<Sidebar.Inset class="landing-font min-h-svh">
<header
			class="sticky top-3 z-30 mx-3 mt-3 flex h-14 shrink-0 items-center justify-between gap-2 rounded-full border border-[#0b3d91]/10 bg-white/80 px-3 shadow-sm backdrop-blur-xl transition-[height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 sm:mx-4 sm:mt-4 sm:px-4 dark:border-white/10 dark:bg-[#0a1730]/80"
		>
			<div class="flex min-w-0 items-center gap-2">
				<Sidebar.Trigger class="-ms-1" />
				<Separator orientation="vertical" class="me-1 data-[orientation=vertical]:h-4" />
				<Breadcrumb.Root>
					<Breadcrumb.List>
						<Breadcrumb.Item class="hidden sm:block">
							<Breadcrumb.Link href="/dashboard" class="text-xs font-medium uppercase tracking-wide">{eyebrow}</Breadcrumb.Link>
						</Breadcrumb.Item>
						<Breadcrumb.Separator class="hidden sm:block" />
						<Breadcrumb.Item>
							<Breadcrumb.Page class="truncate font-display text-base font-black tracking-tight text-[#0b1d3a] sm:text-lg dark:text-white">{title}</Breadcrumb.Page>
						</Breadcrumb.Item>
					</Breadcrumb.List>
				</Breadcrumb.Root>
			</div>

			<div class="flex shrink-0 items-center gap-1 sm:gap-1.5">
				<ThemeToggle />
				<!-- Desktop (>lg): semua aksi inline -->
				<div class="hidden items-center gap-1.5 lg:flex">
					<Button variant="outline" size="sm" title={i18n.locale === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia'} onclick={toggleLocale}>
						<span class="text-xs font-bold uppercase tracking-wide">{i18n.locale === 'id' ? 'EN' : 'ID'}</span>
					</Button>
					<Button variant="outline" size="sm" onclick={() => (commandOpen = true)}>
						<SearchIcon class="size-3.5" />
						<span class="ms-1">{t('Search')}</span>
						<kbd class="ml-1 rounded border border-border bg-secondary px-1 py-0.5 font-mono text-[10px] text-muted-foreground">⌘K</kbd>
					</Button>
					<Button href="/notifications" variant="outline" size="sm" class="relative">
						<BellIcon class="size-3.5" />
						<span class="ms-1">{t('Notifications')}</span>
						{#if unreadCount > 0}
							<span class="absolute -right-0.5 -top-0.5 rounded-full bg-red-600 px-1 text-[10px] font-semibold text-white">{unreadCount}</span>
						{/if}
					</Button>
					<Button variant="outline" size="sm" onclick={() => (activityOpen = !activityOpen)} class="relative">
						<ActivityIcon class="size-3.5" />
						<span class="ms-1">{t('Activity')}</span>
						{#if activityCount}
							<span class="absolute -right-0.5 -top-0.5 rounded-full bg-primary px-1 text-[10px] font-semibold text-primary-foreground">{activityCount}</span>
						{/if}
					</Button>
					<Button href="/trade-projects" variant="outline" size="sm">{t('View projects')}</Button>
					<Button href="/trade-projects/new" size="sm">
						<span>{t('New trade project')}</span>
					</Button>
					{#if user}
						<Button variant="ghost" size="sm" disabled={loggingOut} title={user.role} onclick={handleLogout} class="text-muted-foreground">
							<span class="truncate max-w-[120px]">{user.name}</span>
							<span class="ms-1 text-[11px] font-semibold uppercase tracking-wide">{loggingOut ? '...' : t('Logout')}</span>
						</Button>
					{:else if userStatus === 'unauthenticated'}
						<Button href="/login" variant="outline" size="sm">{t('Login')}</Button>
					{/if}
				</div>

				<!-- Mobile/Tablet (<lg): hamburger menu -->
				<div class="flex items-center lg:hidden">
					<Button variant="ghost" size="sm" onclick={() => (commandOpen = true)} class="h-8 w-8 p-0" title={t('Search')}>
						<SearchIcon class="size-4" />
					</Button>
					<Button href="/notifications" variant="ghost" size="sm" class="relative h-8 w-8 p-0" title={t('Notifications')}>
						<BellIcon class="size-4" />
						{#if unreadCount > 0}
							<span class="absolute -right-0.5 -top-0.5 rounded-full bg-red-600 px-1 text-[10px] font-semibold text-white">{unreadCount}</span>
						{/if}
					</Button>
					<DropdownMenu.Root>
						<DropdownMenu.Trigger class="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground" title={t('Menu')}>
							<MenuIcon class="size-4" />
						</DropdownMenu.Trigger>
						<DropdownMenu.Content align="end" class="w-56">
							<DropdownMenu.Group>
								<DropdownMenu.Label>{t('Aksi Cepat')}</DropdownMenu.Label>
								<DropdownMenu.Item onclick={() => { commandOpen = true; }}>
									<SearchIcon class="size-4" />
									<span>{t('Search')}</span>
								</DropdownMenu.Item>
								<DropdownMenu.Item onclick={() => (activityOpen = true)}>
									<ActivityIcon class="size-4" />
									<span>{t('Activity')}</span>
								</DropdownMenu.Item>
								<DropdownMenu.Item onclick={toggleLocale}>
									<ArrowRightLeftIcon class="size-4" />
									<span>{i18n.locale === 'id' ? 'English' : 'Bahasa Indonesia'}</span>
								</DropdownMenu.Item>
								<DropdownMenu.Separator />
								<DropdownMenu.Item onclick={() => (window.location.href = '/trade-projects')}>
									<span>{t('View projects')}</span>
								</DropdownMenu.Item>
								<DropdownMenu.Item onclick={() => (window.location.href = '/trade-projects/new')}>
									<span>{t('New trade project')}</span>
								</DropdownMenu.Item>
								<DropdownMenu.Separator />
								{#if user}
									<DropdownMenu.Item onclick={handleLogout} class="text-destructive focus:text-destructive">
										<span>{t('Logout')} — {user.name}</span>
									</DropdownMenu.Item>
								{:else if userStatus === 'unauthenticated'}
									<DropdownMenu.Item onclick={() => (window.location.href = '/login')}>
										<span>{t('Login')}</span>
									</DropdownMenu.Item>
								{/if}
							</DropdownMenu.Group>
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				</div>
			</div>
		</header>

		<div class="mx-auto flex w-full max-w-[1600px] flex-1 flex-col gap-4 p-3 sm:p-4 lg:p-6">
			{@render children()}
		</div>
	</Sidebar.Inset>

	<Dialog.Root bind:open={commandOpen}>
		<Dialog.Content class="sm:max-w-xl">
			<Dialog.Header>
				<Dialog.Title class="sr-only">{t('Palet perintah')}</Dialog.Title>
				<Dialog.Description class="sr-only">{t('Cari navigasi, proyek, dan catatan.')}</Dialog.Description>
			</Dialog.Header>
			<div class="flex items-center gap-2 rounded-md border border-border bg-secondary px-2">
				<SearchIcon class="size-4 shrink-0 text-muted-foreground" />
				<Input
					bind:value={commandQuery}
					placeholder={t('Cari navigasi, proyek, produk...')}
					class="border-0 bg-transparent focus-visible:ring-0 focus-visible:border-0"
				/>
			</div>
			<div class="flex flex-col gap-1">
				{#each filteredCommands as command}
					<a
						href={command.href}
						onclick={() => (commandOpen = false)}
						class="flex items-center justify-between gap-3 rounded-md px-2.5 py-2 text-sm text-foreground transition-colors hover:bg-accent"
					>
						<span class="font-medium">{command.label}</span>
						<span class="flex items-center gap-2 text-xs text-muted-foreground">
							{#if command.sub}<span>{command.sub}</span>{/if}
							<span>{trGroup(command.group)}</span>
						</span>
					</a>
				{:else}
					<p class="px-2.5 py-4 text-center text-sm text-muted-foreground">{t('Tidak ada perintah ditemukan.')}</p>
				{/each}
			</div>
		</Dialog.Content>
	</Dialog.Root>

	<Sheet.Root bind:open={activityOpen}>
		<Sheet.Content side="right" class="gap-0 sm:max-w-sm">
			<Sheet.Header>
				<Sheet.Title>{t('Pusat Aktivitas')}</Sheet.Title>
				<Sheet.Description>{t('Sinyal operasional di seluruh workspace ekspor Anda.')}</Sheet.Description>
			</Sheet.Header>
			<div class="flex flex-col gap-2 px-4 pb-4">
				{#each activities as activity}
					<div class="rounded-md border border-border bg-secondary p-3">
						<div class="flex items-start gap-2.5">
							<span
								class={`mt-1.5 size-2 shrink-0 rounded-full ${
									activity.tone === 'green'
										? 'bg-green-500'
										: activity.tone === 'orange'
											? 'bg-orange-500'
											: activity.tone === 'red'
												? 'bg-red-500'
												: 'bg-primary'
								}`}
							></span>
							<div class="min-w-0">
								<p class="text-sm font-medium text-foreground">{activity.title}</p>
								<p class="mt-0.5 text-xs leading-snug text-muted-foreground">{activity.description}</p>
								<p class="mt-1 text-[11px] font-medium text-muted-foreground">{activity.time}</p>
							</div>
						</div>
					</div>
				{/each}
			</div>
			<Sheet.Footer class="px-4 sm:justify-start">
				<Button variant="outline" size="sm" onclick={() => (activityOpen = false)}>
					<ArrowRightLeftIcon class="size-3.5" />
					{t('Tutup')}
				</Button>
			</Sheet.Footer>
		</Sheet.Content>
	</Sheet.Root>
</Sidebar.Provider>
