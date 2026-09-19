<script lang="ts">
	import { page } from '$app/state';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as Avatar from '$lib/components/ui/avatar/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { useSidebar } from '$lib/components/ui/sidebar/index.js';
	import Logo from '$lib/components/Logo.svelte';
	import { navGroups, projects, userAccounts } from '$lib/data/trade';
	import { t } from '$lib/i18n.svelte';

	import InfoIcon from '@lucide/svelte/icons/info';
	import RouteIcon from '@lucide/svelte/icons/route';
	import PackageIcon from '@lucide/svelte/icons/package';
	import ChartLineIcon from '@lucide/svelte/icons/chart-line';
	import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import FolderOpenIcon from '@lucide/svelte/icons/folder-open';
	import ContactIcon from '@lucide/svelte/icons/contact';
	import ClipboardListIcon from '@lucide/svelte/icons/clipboard-list';
	import FactoryIcon from '@lucide/svelte/icons/factory';
	import TruckIcon from '@lucide/svelte/icons/truck';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import ReceiptTextIcon from '@lucide/svelte/icons/receipt-text';
	import CalculatorIcon from '@lucide/svelte/icons/calculator';
	import ClipboardCheckIcon from '@lucide/svelte/icons/clipboard-check';
	import WalletIcon from '@lucide/svelte/icons/wallet';
	import ListTodoIcon from '@lucide/svelte/icons/list-todo';
	import ShipIcon from '@lucide/svelte/icons/ship';
	import ChartPieIcon from '@lucide/svelte/icons/chart-pie';
	import FileChartColumnIcon from '@lucide/svelte/icons/file-chart-column';
	import ScrollTextIcon from '@lucide/svelte/icons/scroll-text';
	import UserCogIcon from '@lucide/svelte/icons/user-cog';
	import BellIcon from '@lucide/svelte/icons/bell';
	import PlugIcon from '@lucide/svelte/icons/plug';
	import { logout } from '$lib/stores/session.svelte';
	import LayoutTemplateIcon from '@lucide/svelte/icons/layout-template';
	import WorkflowIcon from '@lucide/svelte/icons/workflow';
	import BookIcon from '@lucide/svelte/icons/book';
	import BookOpenCheckIcon from '@lucide/svelte/icons/book-open-check';
	import MessageCircleIcon from '@lucide/svelte/icons/message-circle';
	import MegaphoneIcon from '@lucide/svelte/icons/megaphone';
	import CalendarIcon from '@lucide/svelte/icons/calendar';
	import FolderIcon from '@lucide/svelte/icons/folder';
	import MessageSquareIcon from '@lucide/svelte/icons/message-square';
	import CreditCardIcon from '@lucide/svelte/icons/credit-card';
	import LifeBuoyIcon from '@lucide/svelte/icons/life-buoy';
	import KeyIcon from '@lucide/svelte/icons/key';
	import Settings2Icon from '@lucide/svelte/icons/settings-2';
	import LayoutDashboardIcon from '@lucide/svelte/icons/layout-dashboard';
	import BriefcaseIcon from '@lucide/svelte/icons/briefcase';
	import UsersIcon from '@lucide/svelte/icons/users';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';
	import BadgeCheckIcon from '@lucide/svelte/icons/badge-check';
	import LogOutIcon from '@lucide/svelte/icons/log-out';

	const sidebar = useSidebar();
	const currentUser = userAccounts[0];
	let openRiskCount = $derived(projects.filter((project) => project.risk !== 'Low').length);

	const groupIconFor: Record<string, typeof RouteIcon> = {
		Overview: LayoutDashboardIcon,
		'Trade Operations': RouteIcon,
		Commercial: ReceiptTextIcon,
		Fulfillment: ShieldCheckIcon,
		Insights: ChartPieIcon,
		Workspace: FolderOpenIcon,
		Admin: Settings2Icon
	};

	const iconFor: Record<string, typeof RouteIcon> = {
		Dashboard: LayoutDashboardIcon,
		About: InfoIcon,
		'Business Profile': BriefcaseIcon,
		Users: UsersIcon,
		'Trade Projects': RouteIcon,
		Products: PackageIcon,
		'Export Analysis': ChartLineIcon,
		Compliance: ShieldCheckIcon,
		Markets: GlobeIcon,
		Countries: GlobeIcon,
		Catalogs: FolderOpenIcon,
		Buyers: ContactIcon,
		'Buyer Requests': ClipboardListIcon,
		Suppliers: FactoryIcon,
		Forwarders: TruckIcon,
		RFQ: FileTextIcon,
		Quotations: ReceiptTextIcon,
		Costing: CalculatorIcon,
		Orders: ClipboardCheckIcon,
		Payments: WalletIcon,
		Tasks: ListTodoIcon,
		Documents: FileTextIcon,
		Shipments: ShipIcon,
		Analytics: ChartPieIcon,
		Reports: FileChartColumnIcon,
		'Audit Log': ScrollTextIcon,
		Team: UserCogIcon,
		Notifications: BellIcon,
		Integrations: PlugIcon,
		Templates: LayoutTemplateIcon,
		Automations: WorkflowIcon,
		'Knowledge Base': BookIcon,
		Educational: BookOpenCheckIcon,
		Chat: MessageCircleIcon,
		Marketing: MegaphoneIcon,
		Calendar: CalendarIcon,
		Files: FolderIcon,
		Messages: MessageSquareIcon,
		Billing: CreditCardIcon,
		Support: LifeBuoyIcon,
		'API Keys': KeyIcon,
		Settings: Settings2Icon
	};

	function isActive(href: string) {
		return page.url.pathname === href || (href !== '/' && page.url.pathname.startsWith(href));
	}

	function groupIsActive(items: { href: string }[]) {
		return items.some((item) => isActive(item.href));
	}

	function initials(name: string) {
		return name
			.split(' ')
			.map((part) => part[0])
			.slice(0, 2)
			.join('')
			.toUpperCase();
	}
</script>

<Sidebar.Root collapsible="icon" class="landing-font">
	<Sidebar.Header>
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton size="lg" tooltipContent={t('MauEkspor Dashboard')}>
					{#snippet child({ props }: { props: Record<string, unknown> })}
						<a {...props} href="/dashboard" class="flex items-center gap-2.5">
							<Logo variant="logo" class="hidden shrink-0 group-data-[collapsible=icon]:block" />
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Header>

	<Sidebar.Content>
		{#each navGroups as group (group.label)}
			{@const GroupIcon = groupIconFor[group.label] ?? InfoIcon}
			{#if group.label === 'Overview'}
				<Sidebar.Group>
					<Sidebar.GroupLabel>{t(group.label)}</Sidebar.GroupLabel>
					<Sidebar.Menu>
						{#each group.items as item (item.href)}
							{@const NavIcon = iconFor[item.label] ?? InfoIcon}
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
			{:else}
				<Sidebar.Group>
					<Sidebar.GroupLabel>{t(group.label)}</Sidebar.GroupLabel>
					<Sidebar.Menu>
						<Collapsible.Root open={groupIsActive(group.items)} class="group/collapsible">
							{#snippet child({ props })}
								<Sidebar.MenuItem {...props}>
									<Collapsible.Trigger>
										{#snippet child({ props })}
											<Sidebar.MenuButton {...props} tooltipContent={t(group.label)}>
												<GroupIcon class="size-4 shrink-0" />
												<span>{t(group.label)}</span>
												<ChevronRightIcon
													class="ms-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
												/>
											</Sidebar.MenuButton>
										{/snippet}
									</Collapsible.Trigger>
									<Collapsible.Content>
										<Sidebar.MenuSub>
											{#each group.items as item (item.href)}
												<Sidebar.MenuSubItem>
													<Sidebar.MenuSubButton isActive={isActive(item.href)}>
											{#snippet child({ props })}
														<a
															{...props}
															href={item.href}
															onclick={() => sidebar.setOpenMobile(false)}
														>
															<span>{t(item.label)}</span>
															{#if item.label === 'Compliance' && openRiskCount}
																<Badge variant="destructive" class="ms-auto h-4 min-w-4 px-1 text-[10px]">
																	{openRiskCount}
																</Badge>
															{/if}
														</a>
													{/snippet}
													</Sidebar.MenuSubButton>
												</Sidebar.MenuSubItem>
											{/each}
										</Sidebar.MenuSub>
									</Collapsible.Content>
								</Sidebar.MenuItem>
							{/snippet}
						</Collapsible.Root>
					</Sidebar.Menu>
				</Sidebar.Group>
			{/if}
		{/each}
	</Sidebar.Content>

	<Sidebar.Footer>
		<div
			class="rounded-xl border border-sidebar-border bg-gradient-to-br from-[#0b3d91]/10 to-[#1e63d6]/5 p-3 shadow-xs group-data-[collapsible=icon]:hidden dark:from-white/10 dark:to-white/5"
		>
			<Badge variant="outline" class="gap-1 border-[#0b3d91]/30 bg-[#0b3d91]/10 text-[#0b3d91] dark:border-white/30 dark:bg-white/10 dark:text-white">
				<SparklesIcon class="size-3" />
				<span>{t('AI copilot active')}</span>
			</Badge>
			<p class="mt-2 text-[13px] leading-snug text-sidebar-foreground/70">
				{t('Resolve label evidence for Japan before quotation approval.')}
			</p>
		</div>

		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<DropdownMenu.Root>
					<DropdownMenu.Trigger>
						{#snippet child({ props })}
							<Sidebar.MenuButton
								size="lg"
								class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
								{...props}
							>
								<Avatar.Root class="size-8 rounded-lg">
									<Avatar.Fallback class="rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
										{initials(currentUser.fullName)}
									</Avatar.Fallback>
								</Avatar.Root>
								<div class="grid flex-1 text-left text-sm leading-tight">
									<span class="truncate font-medium">{currentUser.fullName}</span>
									<span class="truncate text-xs text-sidebar-foreground/60">{currentUser.email}</span>
								</div>
								<ChevronsUpDownIcon class="ms-auto size-4" />
							</Sidebar.MenuButton>
						{/snippet}
					</DropdownMenu.Trigger>
					<DropdownMenu.Content
						class="w-(--bits-dropdown-menu-anchor-width) min-w-56 rounded-lg"
						side={sidebar.isMobile ? 'bottom' : 'right'}
						align="end"
						sideOffset={4}
					>
						<DropdownMenu.Label class="p-0 font-normal">
							<div class="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
								<Avatar.Root class="size-8 rounded-lg">
									<Avatar.Fallback class="rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
										{initials(currentUser.fullName)}
									</Avatar.Fallback>
								</Avatar.Root>
								<div class="grid flex-1 text-left text-sm leading-tight">
									<span class="truncate font-medium">{currentUser.fullName}</span>
									<span class="truncate text-xs text-muted-foreground">{currentUser.email}</span>
								</div>
							</div>
						</DropdownMenu.Label>
						<DropdownMenu.Separator />
						<DropdownMenu.Group>
							<DropdownMenu.Item>
								{#snippet child({ props })}
									<a {...props} href="/compliance">
										<ClipboardCheckIcon class="text-muted-foreground" />
										{t('Open checklist')}
									</a>
								{/snippet}
							</DropdownMenu.Item>
						</DropdownMenu.Group>
						<DropdownMenu.Separator />
						<DropdownMenu.Group>
							<DropdownMenu.Item>
								{#snippet child({ props })}
									<a {...props} href="/users">
										<BadgeCheckIcon class="text-muted-foreground" />
										{t('Account')}
									</a>
								{/snippet}
							</DropdownMenu.Item>
							<DropdownMenu.Item>
								{#snippet child({ props })}
									<a {...props} href="/billing">
										<CreditCardIcon class="text-muted-foreground" />
										{t('Billing')}
									</a>
								{/snippet}
							</DropdownMenu.Item>
							<DropdownMenu.Item>
								{#snippet child({ props })}
									<a {...props} href="/notifications">
										<BellIcon class="text-muted-foreground" />
										{t('Notifications')}
									</a>
								{/snippet}
							</DropdownMenu.Item>
						</DropdownMenu.Group>
						<DropdownMenu.Separator />
						<DropdownMenu.Item onclick={async () => { await logout(); window.location.href = '/login'; }}>
							{#snippet child({ props })}
								<a {...props}>
									<LogOutIcon class="text-muted-foreground" />
									{t('Logout')}
								</a>
							{/snippet}
						</DropdownMenu.Item>
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
