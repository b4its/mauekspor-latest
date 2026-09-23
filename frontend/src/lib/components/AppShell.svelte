<script lang="ts">
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import AppSidebar from '$lib/components/AppSidebar.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { activities, apiKeys, automationRules, billingRecords, businessProfiles, buyerRequests, buyers, calendarEvents, chatConversations, educationalModules, exportAnalyses, fileAssets, forwarders, integrations, knowledgeArticles, messageThreads, navItems, products, projects, suppliers, supportTickets, teamMembers, templates, tradeReports, userAccounts, workTasks } from '$lib/data/trade';

	import SearchIcon from '@lucide/svelte/icons/search';
	import ActivityIcon from '@lucide/svelte/icons/activity';
	import BellIcon from '@lucide/svelte/icons/bell';
	import ArrowRightLeftIcon from '@lucide/svelte/icons/arrow-right-left';
	import { getStatus, getUser, logout, fetchSession } from '$lib/stores/session.svelte';
	import { listNotifications } from '$lib/api/notifications';

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

	let commands = $derived([
		...navItems.map((item) => ({ label: item.label, href: item.href, group: 'Navigation' })),
		...projects.map((project) => ({ label: project.name, href: `/trade-projects/${project.id}`, group: 'Trade Project' })),
		...products.map((product) => ({ label: product.name, href: `/products/${product.id}`, group: 'Product' })),
		...buyers.map((buyer) => ({ label: buyer.name, href: `/buyers/${buyer.id}`, group: 'Buyer' })),
		...suppliers.map((supplier) => ({ label: supplier.name, href: `/suppliers/${supplier.id}`, group: 'Supplier' })),
		...workTasks.map((task) => ({ label: task.title, href: `/tasks/${task.id}`, group: 'Task' })),
		...tradeReports.map((report) => ({ label: report.title, href: `/reports/${report.id}`, group: 'Report' })),
		...integrations.map((integration) => ({ label: integration.name, href: '/integrations', group: 'Integration' })),
		...templates.map((template) => ({ label: template.title, href: '/templates', group: 'Template' })),
		...automationRules.map((rule) => ({ label: rule.name, href: '/automations', group: 'Automation' })),
		...knowledgeArticles.map((article) => ({ label: article.title, href: '/knowledge', group: 'Knowledge' })),
		...calendarEvents.map((event) => ({ label: event.title, href: '/calendar', group: 'Calendar' })),
		...fileAssets.map((file) => ({ label: file.name, href: '/files', group: 'File' })),
		...messageThreads.map((thread) => ({ label: thread.subject, href: '/messages', group: 'Message' })),
		...billingRecords.map((record) => ({ label: `${record.plan} plan`, href: '/billing', group: 'Billing' })),
		...supportTickets.map((ticket) => ({ label: ticket.subject, href: '/support', group: 'Support' })),
		...apiKeys.map((key) => ({ label: key.name, href: '/api-keys', group: 'API Key' })),
		...businessProfiles.map((profile) => ({ label: profile.companyName, href: '/business-profile', group: 'Business Profile' })),
		...userAccounts.map((user) => ({ label: user.fullName, href: `/users/${user.id}`, group: 'User' })),
		...buyerRequests.map((request) => ({ label: request.subject, href: `/buyer-requests/${request.id}`, group: 'Buyer Request' })),
		...forwarders.map((forwarder) => ({ label: forwarder.name, href: `/forwarders/${forwarder.id}`, group: 'Forwarder' })),
		...educationalModules.map((module) => ({ label: module.title, href: '/educational', group: 'Educational' })),
		...chatConversations.map((chat) => ({ label: chat.title, href: '/chat', group: 'Chat' })),
		...exportAnalyses.map((analysis) => ({ label: `${analysis.productName} - ${analysis.destination}`, href: `/export-analysis/${analysis.id}`, group: 'Export Analysis' }))
	]);
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
		// Polling ringan agar badge notifikasi tetap segar (tiap 30 detik)
		const timer = setInterval(refreshNotifications, 30_000);
		return () => clearInterval(timer);
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

	<Sidebar.Inset class="min-h-svh">
		<header
			class="flex h-16 shrink-0 flex-wrap items-center justify-between gap-3 border-b border-sidebar-border px-3 transition-[height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-14 sm:px-4"
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
							<Breadcrumb.Page class="truncate text-base font-semibold tracking-tight sm:text-lg">{title}</Breadcrumb.Page>
						</Breadcrumb.Item>
					</Breadcrumb.List>
				</Breadcrumb.Root>
			</div>

			<div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
				<ThemeToggle />
				<Button variant="outline" size="sm" onclick={() => (commandOpen = true)}>
					<SearchIcon class="size-3.5" />
					<span class="hidden sm:inline">Search</span>
					<kbd class="ml-1 hidden rounded border border-border bg-secondary px-1 py-0.5 font-mono text-[10px] text-muted-foreground sm:inline-block">⌘K</kbd>
				</Button>
				<Button href="/notifications" variant="outline" size="sm" class="relative">
					<BellIcon class="size-3.5" />
					<span class="hidden sm:inline">Notifications</span>
					{#if unreadCount > 0}
						<span class="ml-0.5 rounded-full bg-red-600 px-1.5 text-[10px] font-semibold text-white">
							{unreadCount}
						</span>
					{/if}
				</Button>
				<Button
					variant="outline"
					size="sm"
					class="relative"
					onclick={() => (activityOpen = !activityOpen)}
				>
					<ActivityIcon class="size-3.5" />
					<span class="hidden sm:inline">Activity</span>
					{#if activityCount}
						<span class="ml-0.5 rounded-full bg-primary px-1.5 text-[10px] font-semibold text-primary-foreground">
							{activityCount}
						</span>
					{/if}
				</Button>
				<Button href="/trade-projects" variant="outline" size="sm" class="hidden md:inline-flex">View projects</Button>
				<Button href="/trade-projects/new" size="sm">
					<span class="hidden sm:inline">New trade project</span>
					<span class="sm:hidden">New project</span>
				</Button>
				{#if user}
					<Button
						variant="ghost"
						size="sm"
						disabled={loggingOut}
						title={user.role}
						onclick={handleLogout}
						class="text-muted-foreground"
					>
						<span class="hidden truncate sm:inline">{user.name}</span>
						<span class="text-[11px] font-semibold uppercase tracking-wide">{loggingOut ? '...' : 'Logout'}</span>
					</Button>
				{:else if userStatus === 'unauthenticated'}
					<Button href="/login" variant="outline" size="sm">Login</Button>
				{/if}
			</div>
		</header>

		<div class="mx-auto flex w-full max-w-[1600px] flex-1 flex-col gap-4 p-3 sm:p-4 lg:p-6">
			{@render children()}
		</div>
	</Sidebar.Inset>

	<Dialog.Root bind:open={commandOpen}>
		<Dialog.Content class="sm:max-w-xl">
			<Dialog.Header>
				<Dialog.Title class="sr-only">Command palette</Dialog.Title>
				<Dialog.Description class="sr-only">Search navigation, projects, and records.</Dialog.Description>
			</Dialog.Header>
			<div class="flex items-center gap-2 rounded-md border border-border bg-secondary px-2">
				<SearchIcon class="size-4 shrink-0 text-muted-foreground" />
				<Input
					bind:value={commandQuery}
					placeholder="Search navigation, projects, products..."
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
							<span>{command.group}</span>
						</span>
					</a>
				{:else}
					<p class="px-2.5 py-4 text-center text-sm text-muted-foreground">No command found.</p>
				{/each}
			</div>
		</Dialog.Content>
	</Dialog.Root>

	<Sheet.Root bind:open={activityOpen}>
		<Sheet.Content side="right" class="gap-0 sm:max-w-sm">
			<Sheet.Header>
				<Sheet.Title>Activity Center</Sheet.Title>
				<Sheet.Description>Operational signals across your export workspace.</Sheet.Description>
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
					Close
				</Button>
			</Sheet.Footer>
		</Sheet.Content>
	</Sheet.Root>
</Sidebar.Provider>