<script lang="ts">
	import AppShell from '$lib/components/AppShell.svelte';
	import AdminSidebar from '$lib/components/AdminSidebar.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { NativeSelect, NativeSelectOption } from '$lib/components/ui/native-select/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Pagination from '$lib/components/Pagination.svelte';
	import {
		listAdminTables,
		listAdminRecords,
		createAdminRecord,
		updateAdminRecord,
		deleteAdminRecord,
		getAiStatus,
		testAi,
		type AdminTable,
		type AdminRecord,
		type AiStatus,
		type AiTestResult
	} from '$lib/api/admin';
	import { t } from '$lib/i18n.svelte';
	import { getStatus, getUser } from '$lib/stores/session.svelte';

	import LayoutDashboardIcon from '@lucide/svelte/icons/layout-dashboard';
	import DatabaseIcon from '@lucide/svelte/icons/database';
	import BotIcon from '@lucide/svelte/icons/bot';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import UsersIcon from '@lucide/svelte/icons/users';
	import LayersIcon from '@lucide/svelte/icons/layers';
	import ServerIcon from '@lucide/svelte/icons/server';
	import ActivityIcon from '@lucide/svelte/icons/activity';
	import ShieldAlertIcon from '@lucide/svelte/icons/shield-alert';
	import ShieldCheckIcon from '@lucide/svelte/icons/shield-check';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';
	import SearchIcon from '@lucide/svelte/icons/search';
	import PlusIcon from '@lucide/svelte/icons/plus';
	import PencilIcon from '@lucide/svelte/icons/pencil';
	import Trash2Icon from '@lucide/svelte/icons/trash-2';
	import EyeIcon from '@lucide/svelte/icons/eye';
	import CopyIcon from '@lucide/svelte/icons/copy';
	import CheckIcon from '@lucide/svelte/icons/check';
	import CheckCircle2Icon from '@lucide/svelte/icons/check-circle-2';
	import AlertCircleIcon from '@lucide/svelte/icons/alert-circle';
	import XIcon from '@lucide/svelte/icons/x';
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
	import ShoppingCartIcon from '@lucide/svelte/icons/shopping-cart';
	import TruckIcon from '@lucide/svelte/icons/truck';
	import PackageIcon from '@lucide/svelte/icons/package';
	import ClockIcon from '@lucide/svelte/icons/clock';

	// Tab navigation
	type AdminTab = 'dashboard' | 'crud' | 'diagnostics' | 'audit';
	let activeTab = $state<AdminTab>('dashboard');

	// Tables state
	let tables = $state<AdminTable[]>([]);
	let tablesLoading = $state(true);
	let activeTable = $state('');
	let records = $state<AdminRecord[]>([]);
	let recordsLoading = $state(false);
	let total = $state(0);
	let search = $state('');
	let tableSearch = $state('');
	let selectedCategory = $state('all');
	let error = $state('');
	let successMessage = $state('');
	let page = $state(1);
	let pageSize = $state(10);

	// Quick action loading state
	let saveLoading = $state(false);
	let deleteLoading = $state(false);

	// Inspect modal
	let inspectOpen = $state(false);
	let inspectRecord = $state<AdminRecord | null>(null);
	let copied = $state(false);

	// Edit / Create modal
	let editOpen = $state(false);
	let editRecord = $state<AdminRecord | null>(null);
	let editJson = $state('');
	let editError = $state('');
	let isNew = $state(false);

	// Delete modal
	let deleteOpen = $state(false);
	let deleteTarget = $state<AdminRecord | null>(null);

	// AI Diagnostics state
	let aiStatus = $state<AiStatus | null>(null);
	let aiLoading = $state(false);
	let aiTesting = $state(false);
	let aiTestResult = $state<AiTestResult | null>(null);
	let aiLatencyMs = $state<number | null>(null);

	// Dashboard additional state
	let usersList = $state<AdminRecord[]>([]);
	let auditEvents = $state<AdminRecord[]>([]);
	let auditLoading = $state(false);
	let auditSearch = $state('');
	let auditActionFilter = $state('all');

	let totalPages = $derived(Math.max(1, Math.ceil(total / pageSize)));
	let isAdmin = $derived(getStatus() === 'authenticated' && getUser()?.role === 'Admin');

	// Computed overall metrics
	let totalRecordsCount = $derived(tables.reduce((acc, t) => acc + (t.count || 0), 0));
	let totalTablesCount = $derived(tables.length);
	let totalUsersCount = $derived(tables.find((t) => t.name === 'users')?.count ?? usersList.length);

	// User role distribution derived
	let userRoles = $derived.by(() => {
		const counts: Record<string, number> = {
			Admin: 0,
			Exporter: 0,
			Buyer: 0,
			Forwarder: 0,
			CustomsBroker: 0,
			Finance: 0
		};
		for (const u of usersList) {
			const role = String(u.role || 'Exporter');
			counts[role] = (counts[role] || 0) + 1;
		}
		return counts;
	});

	// Domain categories mapping
	type TableCategory = {
		id: string;
		label: string;
		tables: string[];
	};

	const TABLE_CATEGORIES: TableCategory[] = [
		{
			id: 'all',
			label: 'Semua Domain',
			tables: []
		},
		{
			id: 'business',
			label: 'Bisnis & Pengguna',
			tables: ['users', 'business_profiles', 'buyer_profiles', 'forwarder_profiles', 'team_members', 'suppliers']
		},
		{
			id: 'catalog',
			label: 'Katalog & Produk Desa',
			tables: ['products', 'catalogs', 'catalog_images', 'catalog_variant_types', 'catalog_variant_options', 'product_enrichments', 'villages']
		},
		{
			id: 'commercial',
			label: 'Komersial & Transaksi',
			tables: ['rfqs', 'quotations', 'orders', 'payments', 'costing', 'pricing_results', 'buyer_requests', 'buyers']
		},
		{
			id: 'logistics',
			label: 'Logistik & Kepatuhan',
			tables: ['shipments', 'forwarders', 'forwarder_reviews', 'compliance_requirements', 'documents', 'regulations', 'regulation_recommendations', 'countries']
		},
		{
			id: 'master',
			label: 'Master Data Global',
			tables: ['hs_codes', 'exchange_rates', 'markets', 'market_intelligence']
		},
		{
			id: 'operations',
			label: 'Operasional & Komunikasi',
			tables: ['tasks', 'calendar_events', 'messages', 'chat_sessions', 'chat_conversations', 'notifications', 'support_tickets']
		},
		{
			id: 'education',
			label: 'Edukasi & Pengetahuan',
			tables: ['knowledge_articles', 'educational_modules', 'educational_articles', 'educational_lessons']
		},
		{
			id: 'system',
			label: 'Sistem & Keamanan',
			tables: ['settings', 'automations', 'integrations', 'templates', 'files', 'reports', 'api_keys', 'billing_records', 'audit_events', 'refresh_tokens']
		}
	];

	// Schema templates for quick and clean record creation
	const TABLE_TEMPLATES: Record<string, Record<string, unknown>> = {
		users: {
			name: 'Budi Santoso',
			email: 'budi@example.com',
			role: 'Exporter',
			status: 'Active',
			phone: '+6281234567890'
		},
		products: {
			name: 'Kopi Arabika Gayo Specialty',
			hsCode: '0901.11.10',
			category: 'Agriculture',
			price: 12.5,
			currency: 'USD',
			origin: 'Aceh Tengah',
			status: 'Ready'
		},
		villages: {
			name: 'Desa Reje Gayo',
			district: 'Lut Tawar',
			regency: 'Aceh Tengah',
			province: 'Aceh',
			commodity: 'Kopi Arabika',
			potentialCapacity: '50 Ton/Tahun',
			status: 'Active'
		},
		orders: {
			orderNumber: 'ORD-2026-001',
			buyer: 'Tokyo Trading Co.',
			status: 'Confirmed',
			totalValue: 35000,
			currency: 'USD',
			paymentStatus: 'Paid'
		},
		shipments: {
			trackingNumber: 'SHP-2026-001',
			carrier: 'Maersk Line',
			originPort: 'Belawan',
			destinationPort: 'Yokohama',
			status: 'In Transit',
			eta: '2026-10-15'
		},
		countries: {
			code: 'SG',
			name: 'Singapura',
			region: 'Southeast Asia',
			currency: 'SGD',
			riskScore: 'Low'
		},
		hs_codes: {
			code: '0901.11.10',
			description: 'Coffee, not roasted, not decaffeinated, Arabica WIB',
			chapter: '09',
			dutyRate: '0%'
		},
		regulations: {
			countryCode: 'JP',
			title: 'Japan Food Sanitation Act',
			ruleCategory: 'Quarantine & Phytosanitary',
			description: 'Residue limit standards for agricultural commodities',
			status: 'Active'
		},
		tasks: {
			title: 'Verifikasi Dokumen Phytosanitary',
			priority: 'High',
			status: 'Pending',
			assignedTo: 'Admin'
		},
		notifications: {
			title: 'Pemberitahuan Sistem',
			message: 'Sinkronisasi berhasil dijalankan.',
			type: 'info',
			status: 'Unread'
		},
		settings: {
			key: 'app_system_mode',
			value: 'Production',
			category: 'system'
		},
		catalogs: {
			title: 'Katalog Komoditas Ekspor Premium 2026',
			status: 'Published',
			language: 'en'
		}
	};

	// Filtered tables according to domain category and search query
	let filteredTables = $derived.by(() => {
		let list = tables;
		if (selectedCategory !== 'all') {
			const cat = TABLE_CATEGORIES.find((c) => c.id === selectedCategory);
			if (cat) {
				list = list.filter((t) => cat.tables.includes(t.name));
			}
		}
		if (tableSearch.trim()) {
			const q = tableSearch.toLowerCase().trim();
			list = list.filter((t) => t.name.toLowerCase().includes(q));
		}
		return list;
	});

	// Dynamic column derivation
	let columns = $derived.by(() => {
		if (records.length === 0) return ['id'];
		const sample = records[0];
		const keys = Object.keys(sample);
		const prioritized = ['id', 'name', 'title', 'code', 'orderNumber', 'trackingNumber', 'email', 'role', 'status', 'category', 'totalValue', 'countryCode'];
		const ordered: string[] = [];
		for (const p of prioritized) {
			if (keys.includes(p) && !ordered.includes(p)) ordered.push(p);
		}
		for (const k of keys) {
			if (!ordered.includes(k) && ordered.length < 6) {
				ordered.push(k);
			}
		}
		return ordered.slice(0, 6);
	});

	// Filtered audit events
	let filteredAuditEvents = $derived.by(() => {
		let list = auditEvents;
		if (auditActionFilter !== 'all') {
			list = list.filter((ev) => String(ev.action || '').toLowerCase() === auditActionFilter.toLowerCase());
		}
		if (auditSearch.trim()) {
			const q = auditSearch.toLowerCase().trim();
			list = list.filter((ev) => JSON.stringify(ev).toLowerCase().includes(q));
		}
		return list;
	});

	async function loadAiStatus() {
		aiLoading = true;
		try {
			const res = await getAiStatus();
			aiStatus = res.data;
		} catch {
			// ignore
		} finally {
			aiLoading = false;
		}
	}

	async function handleTestAi() {
		aiTesting = true;
		aiTestResult = null;
		const start = performance.now();
		try {
			const res = await testAi();
			aiLatencyMs = Math.round(performance.now() - start);
			aiTestResult = res.data;
		} catch (err) {
			aiLatencyMs = Math.round(performance.now() - start);
			aiTestResult = {
				success: false,
				error: err instanceof Error ? err.message : 'Error connecting to AI service'
			};
		} finally {
			aiTesting = false;
		}
	}

	async function loadTables() {
		tablesLoading = true;
		try {
			const res = await listAdminTables();
			tables = res.data;
			if (!activeTable && tables.length) {
				activeTable = tables[0].name;
			}
		} catch {
			error = t('Gagal memuat daftar tabel.');
		} finally {
			tablesLoading = false;
		}
	}

	async function loadRecords() {
		if (!activeTable) return;
		recordsLoading = true;
		try {
			const res = await listAdminRecords(activeTable, {
				search: search || undefined,
				limit: pageSize,
				offset: (page - 1) * pageSize
			});
			records = res.data;
			total = Number(res.meta?.total ?? res.data.length);
		} catch {
			error = t('Gagal memuat data tabel.');
			records = [];
		} finally {
			recordsLoading = false;
		}
	}

	async function loadUsersSummary() {
		try {
			const res = await listAdminRecords('users', { limit: 100 });
			usersList = res.data;
		} catch {
			usersList = [];
		}
	}

	async function loadAuditEvents() {
		auditLoading = true;
		try {
			const res = await listAdminRecords('audit_events', { limit: 50 });
			auditEvents = res.data;
		} catch {
			auditEvents = [];
		} finally {
			auditLoading = false;
		}
	}

	async function refreshAll() {
		await Promise.all([
			loadTables(),
			loadAiStatus(),
			loadUsersSummary(),
			loadAuditEvents()
		]);
		if (activeTable) {
			await loadRecords();
		}
	}

	$effect(() => {
		loadTables();
		loadAiStatus();
		loadUsersSummary();
		loadAuditEvents();
	});

	$effect(() => {
		if (activeTable) {
			loadRecords();
		}
	});

	function selectTable(name: string) {
		activeTable = name;
		search = '';
		page = 1;
	}

	function jumpToCategory(catId: string, initialTable?: string) {
		selectedCategory = catId;
		if (initialTable) {
			activeTable = initialTable;
		} else {
			const cat = TABLE_CATEGORIES.find((c) => c.id === catId);
			if (cat && cat.tables.length > 0) {
				activeTable = cat.tables[0];
			}
		}
		search = '';
		page = 1;
		activeTab = 'crud';
	}

	function jumpToCreate(tableName: string, catId: string) {
		selectedCategory = catId;
		activeTable = tableName;
		activeTab = 'crud';
		openCreate();
	}

	function openInspect(record: AdminRecord) {
		inspectRecord = record;
		copied = false;
		inspectOpen = true;
	}

	async function copyInspectJson() {
		if (!inspectRecord) return;
		try {
			await navigator.clipboard.writeText(JSON.stringify(inspectRecord, null, 2));
			copied = true;
			setTimeout(() => {
				copied = false;
			}, 2000);
		} catch {
			// ignore
		}
	}

	function cloneRecord(record: AdminRecord) {
		isNew = true;
		const clone = { ...record };
		delete (clone as Record<string, unknown>).id;
		delete (clone as Record<string, unknown>).created_at;
		delete (clone as Record<string, unknown>).updated_at;
		editRecord = null;
		editJson = JSON.stringify(clone, null, 2);
		editError = '';
		inspectOpen = false;
		editOpen = true;
	}

	function openCreate() {
		isNew = true;
		editRecord = null;
		const template = TABLE_TEMPLATES[activeTable] || { name: 'Contoh Data', status: 'Active' };
		editJson = JSON.stringify(template, null, 2);
		editError = '';
		editOpen = true;
	}

	function applyStandardTemplate() {
		const template = TABLE_TEMPLATES[activeTable] || { name: 'Contoh Data', status: 'Active' };
		editJson = JSON.stringify(template, null, 2);
		editError = '';
	}

	function openEdit(record: AdminRecord) {
		isNew = false;
		editRecord = record;
		editJson = JSON.stringify(record, null, 2);
		editError = '';
		editOpen = true;
	}

	async function saveEdit() {
		editError = '';
		saveLoading = true;
		let payload: Record<string, unknown>;
		try {
			payload = JSON.parse(editJson);
		} catch {
			editError = t('Format JSON tidak valid. Periksa tanda koma dan kurung kurawal.');
			saveLoading = false;
			return;
		}

		try {
			if (isNew) {
				await createAdminRecord(activeTable, payload);
			} else if (editRecord?.id) {
				await updateAdminRecord(activeTable, editRecord.id, payload);
			}
			editOpen = false;
			editRecord = null;
			successMessage = t('Record berhasil disimpan.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
			await loadRecords();
			await loadTables();
			if (activeTable === 'users') loadUsersSummary();
			if (activeTable === 'audit_events') loadAuditEvents();
		} catch (e) {
			editError = e instanceof Error ? e.message : t('Gagal menyimpan data.');
		} finally {
			saveLoading = false;
		}
	}

	function openDelete(record: AdminRecord) {
		deleteTarget = record;
		deleteOpen = true;
	}

	async function confirmDelete() {
		if (!deleteTarget) return;
		deleteLoading = true;
		try {
			await deleteAdminRecord(activeTable, deleteTarget.id);
			deleteOpen = false;
			deleteTarget = null;
			successMessage = t('Record berhasil dihapus.');
			setTimeout(() => {
				successMessage = '';
			}, 3500);
			await loadRecords();
			await loadTables();
			if (activeTable === 'users') loadUsersSummary();
			if (activeTable === 'audit_events') loadAuditEvents();
		} catch {
			error = t('Gagal menghapus record.');
		} finally {
			deleteLoading = false;
		}
	}

	function isBadgeCol(col: string): boolean {
		return ['status', 'role', 'priority', 'riskScore', 'currency'].includes(col);
	}

	function getBadgeVariant(val: unknown): 'default' | 'secondary' | 'outline' | 'destructive' {
		const s = String(val).toLowerCase();
		if (['active', 'healthy', 'ready', 'confirmed', 'paid', 'verified', 'published', 'low'].includes(s)) return 'default';
		if (['pending', 'in transit', 'draft', 'in review', 'medium', 'warning'].includes(s)) return 'secondary';
		if (['failed', 'degraded', 'error', 'rejected', 'high', 'critical', 'cancelled'].includes(s)) return 'destructive';
		return 'outline';
	}

	function cellPreview(record: AdminRecord, key: string) {
		const v = record[key];
		if (v === null || v === undefined) return '—';
		if (typeof v === 'object') {
			try {
				const s = JSON.stringify(v);
				return s.length > 35 ? s.slice(0, 35) + '…' : s;
			} catch {
				return '[obj]';
			}
		}
		const s = String(v);
		return s.length > 35 ? s.slice(0, 35) + '…' : s;
	}

	function getDomainCount(cat: TableCategory): number {
		return tables
			.filter((t) => cat.tables.includes(t.name))
			.reduce((acc, t) => acc + (t.count || 0), 0);
	}
</script>

<svelte:head>
	<title>{t('Admin Panel')} | MauEkspor</title>
</svelte:head>

<AppShell title={t('Admin Panel')} eyebrow={t('Pusat Komando & Administrasi Ekspor-Impor')}>
	{#snippet sidebar()}
		<AdminSidebar />
	{/snippet}
	{#if !isAdmin}
		<div class="grid place-items-center gap-4 rounded-xl border border-destructive/30 bg-destructive/5 p-12 text-center">
			<ShieldAlertIcon class="size-12 text-destructive/60" />
			<div>
				<h2 class="text-xl font-bold">{t('Akses Ditolak')}</h2>
				<p class="mt-1 text-sm text-muted-foreground">{t('Halaman ini khusus Admin.')}</p>
			</div>
			<Button href="/dashboard" variant="outline">{t('Kembali ke Dashboard')}</Button>
		</div>
	{:else}
		<!-- Header Controls & Sub-Module Shortcuts -->
		<div class="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border bg-card p-4 shadow-sm">
			<div class="flex items-center gap-3">
				<div class="rounded-xl bg-primary/10 p-2.5 text-primary">
					<DatabaseIcon class="size-6" />
				</div>
				<div>
					<div class="flex flex-wrap items-center gap-2">
						<h2 class="text-base font-bold text-foreground">{t('Admin Panel')}</h2>
						{#if aiStatus}
							<Badge variant={aiStatus.health === 'healthy' ? 'default' : 'destructive'} class="text-xs">
								{aiStatus.health}
							</Badge>
							<Badge variant="outline" class="text-xs font-medium">
								{t('Mode AI')}: {aiStatus.mode}
							</Badge>
						{/if}
					</div>
					<p class="text-xs text-muted-foreground">{t('Pusat Komando & Administrasi Ekspor-Impor')}</p>
				</div>
			</div>

			<div class="flex flex-wrap items-center gap-2">
				<Button size="sm" variant="outline" onclick={refreshAll} title={t('Segarkan Data')}>
					<RefreshCwIcon class="size-3.5 {tablesLoading ? 'animate-spin' : ''}" />
					<span class="ms-1 hidden sm:inline">{t('Segarkan Data')}</span>
				</Button>
				<Button href="/admin/countries" size="sm" variant="outline">
					<GlobeIcon class="size-3.5" />
					<span class="ms-1">{t('Kelola Negara & Regulasi')}</span>
				</Button>
			</div>
		</div>

		<!-- Feedback Alerts -->
		{#if error}
			<div class="mb-4 flex items-center justify-between rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-semibold text-destructive">
				<div class="flex items-center gap-2">
					<AlertCircleIcon class="size-4" />
					<span>{error}</span>
				</div>
				<button onclick={() => (error = '')} class="text-destructive hover:opacity-80"><XIcon class="size-4" /></button>
			</div>
		{/if}

		{#if successMessage}
			<div class="mb-4 flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-800 dark:text-emerald-300">
				<div class="flex items-center gap-2">
					<CheckCircle2Icon class="size-4" />
					<span>{successMessage}</span>
				</div>
				<button onclick={() => (successMessage = '')} class="hover:opacity-80"><XIcon class="size-4" /></button>
			</div>
		{/if}

		<!-- Navigation Tabs -->
		<div class="mb-6 flex flex-wrap items-center gap-2 border-b pb-3">
			<button
				onclick={() => (activeTab = 'dashboard')}
				class="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all {activeTab === 'dashboard' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
			>
				<LayoutDashboardIcon class="size-4" />
				<span>{t('Ringkasan Eksekutif')}</span>
			</button>

			<button
				onclick={() => (activeTab = 'crud')}
				class="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all {activeTab === 'crud' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
			>
				<DatabaseIcon class="size-4" />
				<span>{t('Database CRUD Studio')}</span>
				<Badge variant={activeTab === 'crud' ? 'secondary' : 'outline'} class="ms-1 text-xs">
					{totalTablesCount}
				</Badge>
			</button>

			<button
				onclick={() => (activeTab = 'diagnostics')}
				class="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all {activeTab === 'diagnostics' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
			>
				<BotIcon class="size-4" />
				<span>{t('Diagnostik AI & Sistem')}</span>
			</button>

			<button
				onclick={() => (activeTab = 'audit')}
				class="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all {activeTab === 'audit' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
			>
				<FileTextIcon class="size-4" />
				<span>{t('Log Aktivitas Audit')}</span>
			</button>
		</div>

		<!-- ==================================================================== -->
		<!-- TAB 1: EXECUTIVE DASHBOARD                                           -->
		<!-- ==================================================================== -->
		{#if activeTab === 'dashboard'}
			<div class="space-y-6">
				<!-- High Level KPI Cards -->
				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
					<Card>
						<CardContent class="p-5">
							<div class="flex items-center justify-between">
								<p class="text-xs font-medium uppercase tracking-wider text-muted-foreground">{t('Total Record Database')}</p>
								<div class="rounded-lg bg-primary/10 p-2 text-primary">
									<LayersIcon class="size-4" />
								</div>
							</div>
							<div class="mt-3">
								<h3 class="text-2xl font-bold tracking-tight text-foreground">{totalRecordsCount.toLocaleString()}</h3>
								<p class="mt-1 text-xs text-muted-foreground">{t('Di seluruh tabel database')}</p>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardContent class="p-5">
							<div class="flex items-center justify-between">
								<p class="text-xs font-medium uppercase tracking-wider text-muted-foreground">{t('Total Tabel Aktif')}</p>
								<div class="rounded-lg bg-emerald-500/10 p-2 text-emerald-700 dark:text-emerald-400">
									<DatabaseIcon class="size-4" />
								</div>
							</div>
							<div class="mt-3">
								<h3 class="text-2xl font-bold tracking-tight text-foreground">{totalTablesCount}</h3>
								<p class="mt-1 text-xs text-muted-foreground">{t('Tabel siap operasi')}</p>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardContent class="p-5">
							<div class="flex items-center justify-between">
								<p class="text-xs font-medium uppercase tracking-wider text-muted-foreground">{t('Pengguna Terdaftar')}</p>
								<div class="rounded-lg bg-blue-500/10 p-2 text-blue-700 dark:text-blue-400">
									<UsersIcon class="size-4" />
								</div>
							</div>
							<div class="mt-3">
								<h3 class="text-2xl font-bold tracking-tight text-foreground">{totalUsersCount}</h3>
								<p class="mt-1 text-xs text-muted-foreground">{t('Pengguna aktif platform')}</p>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardContent class="p-5">
							<div class="flex items-center justify-between">
								<p class="text-xs font-medium uppercase tracking-wider text-muted-foreground">{t('Kesehatan AI Copilot')}</p>
								<div class="rounded-lg bg-purple-500/10 p-2 text-purple-700 dark:text-purple-400">
									<BotIcon class="size-4" />
								</div>
							</div>
							<div class="mt-3 flex items-baseline gap-2">
								<h3 class="text-2xl font-bold capitalize tracking-tight text-foreground">{aiStatus?.health ?? 'Healthy'}</h3>
								<Badge variant={aiStatus?.health === 'healthy' ? 'default' : 'destructive'} class="text-[10px]">
									{aiStatus?.mode ?? 'mock'}
								</Badge>
							</div>
							<p class="mt-1 text-xs text-muted-foreground">{t('Layanan AI terhubung')}</p>
						</CardContent>
					</Card>
				</div>

				<!-- Quick Action Launchpad -->
				<Card>
					<CardHeader class="p-4 pb-2">
						<CardTitle class="text-base font-semibold">{t('Tindakan Cepat Admin')}</CardTitle>
					</CardHeader>
					<CardContent class="p-4 pt-2">
						<div class="flex flex-wrap gap-2.5">
							<Button size="sm" onclick={() => jumpToCreate('users', 'business')}>
								<PlusIcon class="size-3.5" />
								<span class="ms-1.5">{t('Buat Pengguna Baru')}</span>
							</Button>
							<Button size="sm" variant="outline" onclick={() => jumpToCreate('products', 'catalog')}>
								<PackageIcon class="size-3.5" />
								<span class="ms-1.5">{t('Tambah Produk Desa')}</span>
							</Button>
							<Button size="sm" variant="outline" onclick={() => jumpToCreate('villages', 'catalog')}>
								<PlusIcon class="size-3.5" />
								<span class="ms-1.5">{t('Registrasi Komoditas Desa')}</span>
							</Button>
							<Button size="sm" variant="outline" href="/admin/countries">
								<GlobeIcon class="size-3.5" />
								<span class="ms-1.5">{t('Kelola Regulasi Ekspor')}</span>
							</Button>
							<Button
								size="sm"
								variant="outline"
								onclick={() => {
									activeTab = 'diagnostics';
									handleTestAi();
								}}
							>
								<BotIcon class="size-3.5" />
								<span class="ms-1.5">{t('Uji Konektivitas AI')}</span>
							</Button>
						</div>
					</CardContent>
				</Card>

				<!-- User Roles Breakdown & Storage Grid -->
				<div class="grid gap-6 lg:grid-cols-2">
					<!-- Role Breakdown Card -->
					<Card>
						<CardHeader class="p-5 pb-3">
							<CardTitle class="flex items-center gap-2 text-base font-semibold">
								<UsersIcon class="size-4 text-primary" />
								<span>{t('Distribusi Peran Pengguna')}</span>
							</CardTitle>
						</CardHeader>
						<CardContent class="space-y-3 p-5 pt-0">
							<div class="grid grid-cols-2 gap-2.5 sm:grid-cols-3">
								{#each Object.entries(userRoles) as [role, count]}
									<div class="rounded-lg border bg-muted/30 p-3">
										<p class="text-xs font-semibold text-muted-foreground">{role}</p>
										<p class="mt-1 text-xl font-bold text-foreground">{count}</p>
									</div>
								{/each}
							</div>
							<div class="mt-4 flex items-center justify-between border-t pt-3">
								<Button size="sm" variant="ghost" onclick={() => jumpToCategory('business', 'users')}>
									<span>{t('Kelola Data Tabel')}</span>
									<ArrowRightIcon class="ms-1.5 size-3.5" />
								</Button>
							</div>
						</CardContent>
					</Card>

					<!-- Database Architecture Card -->
					<Card>
						<CardHeader class="p-5 pb-3">
							<CardTitle class="flex items-center gap-2 text-base font-semibold">
								<ServerIcon class="size-4 text-primary" />
								<span>{t('Arsitektur Database & Penyimpanan')}</span>
							</CardTitle>
						</CardHeader>
						<CardContent class="space-y-3 p-5 pt-0">
							<div class="grid grid-cols-2 gap-2.5">
								<div class="rounded-lg border bg-muted/30 p-3">
									<p class="text-xs font-semibold text-muted-foreground">{t('Mesin Database')}</p>
									<p class="mt-1 text-base font-bold text-foreground">SQLite / PostgreSQL</p>
								</div>
								<div class="rounded-lg border bg-muted/30 p-3">
									<p class="text-xs font-semibold text-muted-foreground">{t('Persistensi Data')}</p>
									<p class="mt-1 text-base font-bold text-foreground">{t('Aktif (Disimpan ke Disk)')}</p>
								</div>
								<div class="rounded-lg border bg-muted/30 p-3">
									<p class="text-xs font-semibold text-muted-foreground">{t('Total Tabel')}</p>
									<p class="mt-1 text-base font-bold text-foreground">{totalTablesCount} {t('Tabel')}</p>
								</div>
								<div class="rounded-lg border bg-muted/30 p-3">
									<p class="text-xs font-semibold text-muted-foreground">{t('Total Baris Data')}</p>
									<p class="mt-1 text-base font-bold text-foreground">{totalRecordsCount.toLocaleString()} {t('record')}</p>
								</div>
							</div>
							<div class="mt-4 flex items-center justify-between border-t pt-3">
								<Button size="sm" variant="ghost" onclick={() => (activeTab = 'crud')}>
									<span>{t('Database CRUD Studio')}</span>
									<ArrowRightIcon class="ms-1.5 size-3.5" />
								</Button>
							</div>
						</CardContent>
					</Card>
				</div>

				<!-- Domain Hub Breakdown Cards -->
				<div>
					<h3 class="mb-3 text-base font-bold text-foreground">{t('Semua Domain')}</h3>
					<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
						{#each TABLE_CATEGORIES.filter((c) => c.id !== 'all') as cat}
							{@const domainCount = getDomainCount(cat)}
							<Card class="flex flex-col justify-between transition-shadow hover:shadow-md">
								<CardHeader class="p-4 pb-2">
									<CardTitle class="text-sm font-bold text-foreground">{t(cat.label)}</CardTitle>
									<CardDescription class="text-xs">
										{cat.tables.length} {t('Tabel')} · {domainCount} {t('record')}
									</CardDescription>
								</CardHeader>
								<CardContent class="p-4 pt-1">
									<div class="mb-3 flex flex-wrap gap-1">
										{#each cat.tables.slice(0, 4) as tb}
											{@const tRecord = tables.find((x) => x.name === tb)}
											<Badge variant="outline" class="text-[10px]">
												{tb} ({tRecord?.count ?? 0})
											</Badge>
										{/each}
										{#if cat.tables.length > 4}
											<Badge variant="secondary" class="text-[10px]">+{cat.tables.length - 4}</Badge>
										{/if}
									</div>
									<Button size="sm" variant="outline" class="w-full text-xs" onclick={() => jumpToCategory(cat.id)}>
										<span>{t('Buka CRUD')}</span>
										<ArrowRightIcon class="ms-1.5 size-3" />
									</Button>
								</CardContent>
							</Card>
						{/each}
					</div>
				</div>

				<!-- Recent Audit Activity Stream -->
				<Card>
					<CardHeader class="flex-row items-center justify-between p-5 pb-3">
						<CardTitle class="flex items-center gap-2 text-base font-semibold">
							<ClockIcon class="size-4 text-primary" />
							<span>{t('Aktivitas Audit Terkini')}</span>
						</CardTitle>
						<Button size="sm" variant="ghost" onclick={() => (activeTab = 'audit')}>
							<span>{t('Lihat Detail')}</span>
							<ArrowRightIcon class="ms-1.5 size-3.5" />
						</Button>
					</CardHeader>
					<CardContent class="p-5 pt-0">
						{#if auditEvents.length === 0}
							<p class="py-6 text-center text-sm text-muted-foreground">{t('Tidak ada aktivitas audit tercatat.')}</p>
						{:else}
							<div class="divide-y text-sm">
								{#each auditEvents.slice(0, 5) as ev (ev.id)}
									<div class="flex flex-wrap items-center justify-between gap-2 py-2.5">
										<div class="flex items-center gap-3">
											<Badge variant={getBadgeVariant(ev.action)} class="text-[11px] uppercase">
												{ev.action || 'EVENT'}
											</Badge>
											<div>
												<p class="text-xs font-semibold text-foreground">
													{ev.entity || ev.target || 'Record'} <span class="font-normal text-muted-foreground">({ev.id})</span>
												</p>
												<p class="text-[11px] text-muted-foreground">
													{ev.user || ev.actor || 'System'} · {ev.timestamp || ev.created_at || 'Recently'}
												</p>
											</div>
										</div>
										<Button size="sm" variant="ghost" class="h-7 px-2 text-xs" onclick={() => openInspect(ev)}>
											<EyeIcon class="size-3.5" />
										</Button>
									</div>
								{/each}
							</div>
						{/if}
					</CardContent>
				</Card>
			</div>
		{/if}

		<!-- ==================================================================== -->
		<!-- TAB 2: DATABASE CRUD STUDIO                                          -->
		<!-- ==================================================================== -->
		{#if activeTab === 'crud'}
			<div class="space-y-4">
				<!-- Category Filter Pills -->
				<div class="flex flex-wrap items-center gap-1.5 rounded-xl border bg-card p-2 shadow-sm">
					{#each TABLE_CATEGORIES as cat}
						<button
							onclick={() => {
								selectedCategory = cat.id;
								if (cat.id !== 'all' && cat.tables.length > 0 && !cat.tables.includes(activeTable)) {
									activeTable = cat.tables[0];
									page = 1;
								}
							}}
							class="rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors {selectedCategory === cat.id ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}"
						>
							{t(cat.label)}
						</button>
					{/each}
				</div>

				<!-- Horizontal Table Selector (pengganti kolom "sidebar tabel" agar
				     panel admin tidak tampak memiliki sidebar kedua). -->
				<Card>
					<CardHeader class="flex-row flex-wrap items-center justify-between gap-3 p-3">
						<CardTitle class="flex items-center gap-1.5 text-sm">
							<DatabaseIcon class="size-4" />
							{t('Tabel')} ({filteredTables.length})
						</CardTitle>
						<div class="flex items-center gap-1.5 rounded-md border bg-muted/20 px-2 py-1">
							<SearchIcon class="size-3.5 text-muted-foreground" />
							<input
								type="text"
								placeholder={t('Cari nama tabel...')}
								bind:value={tableSearch}
								class="w-40 bg-transparent text-xs outline-none sm:w-56"
							/>
							{#if tableSearch}
								<button onclick={() => (tableSearch = '')} class="text-muted-foreground hover:text-foreground">
									<XIcon class="size-3" />
								</button>
							{/if}
						</div>
					</CardHeader>
					<CardContent class="p-3 pt-0">
						{#if tablesLoading}
							<div class="flex flex-wrap gap-1.5">
								{#each [1, 2, 3, 4, 5, 6, 7, 8] as _}
									<div class="h-7 w-24 animate-pulse rounded-full bg-muted/40"></div>
								{/each}
							</div>
						{:else if filteredTables.length === 0}
							<p class="py-3 text-center text-xs text-muted-foreground">{t('Tabel tidak ditemukan')}</p>
						{:else}
							<div class="flex flex-wrap gap-1.5">
								{#each filteredTables as table}
									<button
										onclick={() => selectTable(table.name)}
										class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs transition-colors hover:bg-accent {activeTable === table.name ? 'border-primary bg-primary font-bold text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}"
									>
										<span class="truncate">{table.name}</span>
										<Badge variant={activeTable === table.name ? 'secondary' : 'outline'} class="h-4 shrink-0 px-1.5 text-[10px]">
											{table.count}
										</Badge>
									</button>
								{/each}
							</div>
						{/if}
					</CardContent>
				</Card>

				<div class="grid gap-4">
					<!-- Table Records Management Panel -->
					<Card>
						<CardHeader class="flex-row flex-wrap items-center justify-between gap-3 p-4">
							<div>
								<div class="flex items-center gap-2">
									<CardTitle class="text-base font-bold">{activeTable || '—'}</CardTitle>
									<Badge variant="secondary" class="text-xs">{total} {t('record')}</Badge>
								</div>
								<CardDescription class="text-xs">{t('Kelola Data Tabel')}</CardDescription>
							</div>

							<div class="flex flex-wrap items-center gap-2">
								<div class="flex items-center gap-1.5 rounded-md border bg-muted/20 px-2 py-1">
									<SearchIcon class="size-3.5 text-muted-foreground" />
									<input
										type="text"
										placeholder={t('Cari data di tabel ini...')}
										bind:value={search}
										oninput={() => (page = 1)}
										class="w-32 bg-transparent text-xs outline-none sm:w-44"
									/>
									{#if search}
										<button onclick={() => { search = ''; page = 1; }} class="text-muted-foreground hover:text-foreground">
											<XIcon class="size-3" />
										</button>
									{/if}
								</div>

								<div class="flex items-center gap-1 text-xs text-muted-foreground">
									<span>{t('Baris per halaman:')}</span>
									<NativeSelect
										value={String(pageSize)}
										onchange={(e) => {
											pageSize = Number((e.target as HTMLSelectElement).value);
											page = 1;
											loadRecords();
										}}
										class="h-7 w-16 text-xs"
									>
										<NativeSelectOption value="5">5</NativeSelectOption>
										<NativeSelectOption value="10">10</NativeSelectOption>
										<NativeSelectOption value="25">25</NativeSelectOption>
										<NativeSelectOption value="50">50</NativeSelectOption>
										<NativeSelectOption value="100">100</NativeSelectOption>
									</NativeSelect>
								</div>

								<Button size="sm" onclick={openCreate}>
									<PlusIcon class="size-3.5" />
									<span class="ms-1">{t('Buat Record')}</span>
								</Button>

								<Button size="sm" variant="outline" onclick={loadRecords} title={t('Segarkan')}>
									<RefreshCwIcon class="size-3.5 {recordsLoading ? 'animate-spin' : ''}" />
								</Button>
							</div>
						</CardHeader>

						<CardContent class="p-4 pt-0">
							{#if recordsLoading}
								<div class="space-y-2 py-4">
									{#each [1, 2, 3, 4, 5] as _}
										<div class="h-10 animate-pulse rounded-lg bg-muted/40"></div>
									{/each}
								</div>
							{:else if records.length === 0}
								<div class="rounded-xl border border-dashed p-12 text-center">
									<DatabaseIcon class="mx-auto size-8 text-muted-foreground/50" />
									<p class="mt-2 text-sm font-semibold text-foreground">{t('Tidak ada data ditemukan pada tabel ini.')}</p>
									<p class="mt-1 text-xs text-muted-foreground">{t('Gunakan tombol Buat Record untuk menambahkan baris baru.')}</p>
									<Button size="sm" class="mt-4" onclick={openCreate}>
										<PlusIcon class="size-3.5" />
										<span class="ms-1.5">{t('Buat Record Baru')}</span>
									</Button>
								</div>
							{:else}
								<!-- Data Table -->
								<div class="overflow-x-auto rounded-lg border">
									<table class="w-full text-xs">
										<thead>
											<tr class="border-b bg-muted/30 text-left font-semibold uppercase tracking-wider text-muted-foreground">
												{#each columns as col}
													<th class="px-3 py-2.5">{col}</th>
												{/each}
												<th class="px-3 py-2.5 text-right">{t('Aksi')}</th>
											</tr>
										</thead>
										<tbody class="divide-y">
											{#each records as record (record.id)}
												<tr class="transition-colors hover:bg-accent/40">
													{#each columns as col}
														<td class="max-w-[180px] truncate px-3 py-2.5 font-mono text-[11px]">
															{#if isBadgeCol(col)}
																<Badge variant={getBadgeVariant(record[col])} class="text-[10px]">
																	{String(record[col] ?? '—')}
																</Badge>
															{:else}
																{cellPreview(record, col)}
															{/if}
														</td>
													{/each}
													<td class="px-3 py-2.5 text-right">
														<div class="flex items-center justify-end gap-1">
															<button
																onclick={() => openInspect(record)}
																class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
																title={t('Lihat Detail')}
															>
																<EyeIcon class="size-3.5" />
															</button>
															<button
																onclick={() => cloneRecord(record)}
																class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
																title={t('Klon Record')}
															>
																<CopyIcon class="size-3.5" />
															</button>
															<button
																onclick={() => openEdit(record)}
																class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
																title={t('Edit Record')}
															>
																<PencilIcon class="size-3.5" />
															</button>
															<button
																onclick={() => openDelete(record)}
																class="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
																title={t('Hapus Record')}
															>
																<Trash2Icon class="size-3.5" />
															</button>
														</div>
													</td>
												</tr>
											{/each}
										</tbody>
									</table>
								</div>

								<div class="mt-3">
									<Pagination bind:page bind:pageSize totalPages={totalPages} totalItems={total} />
								</div>
							{/if}
						</CardContent>
					</Card>
				</div>
			</div>
		{/if}

		<!-- ==================================================================== -->
		<!-- TAB 3: DIAGNOSTICS & SYSTEM STATUS                                   -->
		<!-- ==================================================================== -->
		{#if activeTab === 'diagnostics'}
			<div class="space-y-6">
				<div class="grid gap-6 lg:grid-cols-2">
					<!-- AI Copilot Diagnostic Card -->
					<Card>
						<CardHeader class="p-5">
							<div class="flex items-center gap-2">
								<BotIcon class="size-5 text-primary" />
								<div>
									<CardTitle class="text-base font-semibold">{t('Status & Konfigurasi AI Copilot')}</CardTitle>
									<CardDescription class="text-xs">
										{t('Periksa kesiapan konektivitas API AI untuk fitur rekomendasi, enrichment komoditas, dan perbandingan regulasi.')}
									</CardDescription>
								</div>
							</div>
						</CardHeader>
						<CardContent class="space-y-4 p-5 pt-0">
							<div class="grid grid-cols-2 gap-3">
								<div class="rounded-lg border bg-muted/20 p-3">
									<p class="text-xs text-muted-foreground">{t('Status Kesehatan')}</p>
									<div class="mt-1 flex items-center gap-2">
										<Badge variant={aiStatus?.health === 'healthy' ? 'default' : 'destructive'} class="text-xs">
											{aiStatus?.health ?? 'Healthy'}
										</Badge>
									</div>
								</div>

								<div class="rounded-lg border bg-muted/20 p-3">
									<p class="text-xs text-muted-foreground">{t('Mode AI')}</p>
									<p class="mt-1 font-mono text-sm font-bold text-foreground uppercase">{aiStatus?.mode ?? 'MOCK'}</p>
								</div>

								<div class="rounded-lg border bg-muted/20 p-3">
									<p class="text-xs text-muted-foreground">{t('Penyedia Model')}</p>
									<p class="mt-1 text-sm font-semibold text-foreground">{aiStatus?.configured_provider || 'Mock / Fallback'}</p>
								</div>

								<div class="rounded-lg border bg-muted/20 p-3">
									<p class="text-xs text-muted-foreground">{t('Tipe Lingkungan')}</p>
									<p class="mt-1 text-sm font-semibold text-foreground">
										{aiStatus?.using_remote ? 'Remote Cloud' : 'Local Sandbox'}
									</p>
								</div>
							</div>

							<div class="rounded-xl border bg-card p-4">
								<div class="flex flex-wrap items-center justify-between gap-3">
									<div>
										<h4 class="text-xs font-bold text-foreground">{t('Tes Ping AI Copilot')}</h4>
										<p class="text-[11px] text-muted-foreground">{t('Jalankan pengujian sintesis teks sederhana untuk memverifikasi responsivitas model.')}</p>
									</div>
									<Button size="sm" disabled={aiTesting} onclick={handleTestAi}>
										<RefreshCwIcon class="size-3.5 {aiTesting ? 'animate-spin' : ''}" />
										<span class="ms-1.5">{aiTesting ? t('Menguji AI...') : t('Uji Responsivitas AI')}</span>
									</Button>
								</div>

								{#if aiLatencyMs !== null}
									<div class="mt-3 flex items-center gap-2 text-xs">
										<span class="text-muted-foreground">{t('Latensi Respons')}:</span>
										<Badge variant="outline" class="font-mono text-xs">{aiLatencyMs} ms</Badge>
									</div>
								{/if}

								{#if aiTestResult}
									<div class="mt-3 rounded-lg border p-3 {aiTestResult.success ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-destructive/30 bg-destructive/10'}">
										<div class="flex items-center gap-2">
											{#if aiTestResult.success}
												<CheckCircle2Icon class="size-4 text-emerald-600 dark:text-emerald-400" />
												<span class="text-xs font-bold text-emerald-800 dark:text-emerald-300">{t('Berhasil')}</span>
											{:else}
												<AlertCircleIcon class="size-4 text-destructive" />
												<span class="text-xs font-bold text-destructive">{t('Gagal')}</span>
											{/if}
										</div>
										<p class="mt-1 font-mono text-xs text-foreground">
											{aiTestResult.response || aiTestResult.error || 'Response OK'}
										</p>
									</div>
								{/if}
							</div>
						</CardContent>
					</Card>

					<!-- Database Architecture & Storage -->
					<Card>
						<CardHeader class="p-5">
							<div class="flex items-center gap-2">
								<ServerIcon class="size-5 text-primary" />
								<div>
									<CardTitle class="text-base font-semibold">{t('Arsitektur Database & Penyimpanan')}</CardTitle>
									<CardDescription class="text-xs">{t('Informasi mesin persistensi database dan statistik penyimpanan MauEkspor.')}</CardDescription>
								</div>
							</div>
						</CardHeader>
						<CardContent class="space-y-4 p-5 pt-0">
							<div class="space-y-3">
								<div class="flex items-center justify-between border-b pb-2 text-xs">
									<span class="text-muted-foreground">{t('Mesin Database')}</span>
									<span class="font-semibold text-foreground">SQLite / PostgreSQL Engine</span>
								</div>
								<div class="flex items-center justify-between border-b pb-2 text-xs">
									<span class="text-muted-foreground">{t('Persistensi Data')}</span>
									<span class="font-semibold text-emerald-600 dark:text-emerald-400">{t('Aktif (Disimpan ke Disk)')}</span>
								</div>
								<div class="flex items-center justify-between border-b pb-2 text-xs">
									<span class="text-muted-foreground">{t('Total Tabel')}</span>
									<span class="font-semibold text-foreground">{totalTablesCount}</span>
								</div>
								<div class="flex items-center justify-between border-b pb-2 text-xs">
									<span class="text-muted-foreground">{t('Total Baris Data')}</span>
									<span class="font-semibold text-foreground">{totalRecordsCount.toLocaleString()}</span>
								</div>
							</div>

							<div class="mt-4 flex flex-wrap gap-2">
								<Button size="sm" variant="outline" onclick={refreshAll}>
									<RefreshCwIcon class="size-3.5" />
									<span class="ms-1.5">{t('Segarkan Data')}</span>
								</Button>
								<Button size="sm" variant="default" onclick={() => (activeTab = 'crud')}>
									<DatabaseIcon class="size-3.5" />
									<span class="ms-1.5">{t('Buka CRUD')}</span>
								</Button>
							</div>
						</CardContent>
					</Card>
				</div>
			</div>
		{/if}

		<!-- ==================================================================== -->
		<!-- TAB 4: AUDIT ACTIVITY LOG                                            -->
		<!-- ==================================================================== -->
		{#if activeTab === 'audit'}
			<Card>
				<CardHeader class="flex-row flex-wrap items-center justify-between gap-3 p-4">
					<div>
						<CardTitle class="text-base font-semibold">{t('Log Aktivitas Audit')}</CardTitle>
						<CardDescription class="text-xs">{t('Aktivitas Audit Terkini')}</CardDescription>
					</div>

					<div class="flex flex-wrap items-center gap-2">
						<div class="flex items-center gap-1.5 rounded-md border bg-muted/20 px-2 py-1">
							<SearchIcon class="size-3.5 text-muted-foreground" />
							<input
								type="text"
								placeholder={t('Cari audit log...')}
								bind:value={auditSearch}
								class="w-32 bg-transparent text-xs outline-none sm:w-44"
							/>
							{#if auditSearch}
								<button onclick={() => (auditSearch = '')} class="text-muted-foreground hover:text-foreground">
									<XIcon class="size-3" />
								</button>
							{/if}
						</div>

						<NativeSelect
							value={auditActionFilter}
							onchange={(e) => {
								auditActionFilter = (e.target as HTMLSelectElement).value;
							}}
							class="h-8 text-xs"
						>
							<NativeSelectOption value="all">{t('Semua Aksi')}</NativeSelectOption>
							<NativeSelectOption value="create">CREATE</NativeSelectOption>
							<NativeSelectOption value="update">UPDATE</NativeSelectOption>
							<NativeSelectOption value="delete">DELETE</NativeSelectOption>
							<NativeSelectOption value="login">LOGIN</NativeSelectOption>
							<NativeSelectOption value="export">EXPORT</NativeSelectOption>
						</NativeSelect>

						<Button size="sm" variant="outline" onclick={loadAuditEvents} title={t('Segarkan')}>
							<RefreshCwIcon class="size-3.5 {auditLoading ? 'animate-spin' : ''}" />
						</Button>
					</div>
				</CardHeader>

				<CardContent class="p-4 pt-0">
					{#if auditLoading}
						<div class="space-y-2 py-4">
							{#each [1, 2, 3, 4, 5] as _}
								<div class="h-10 animate-pulse rounded-lg bg-muted/40"></div>
							{/each}
						</div>
					{:else if filteredAuditEvents.length === 0}
						<p class="py-10 text-center text-sm text-muted-foreground">{t('Tidak ada aktivitas audit tercatat.')}</p>
					{:else}
						<div class="overflow-x-auto rounded-lg border">
							<table class="w-full text-xs">
								<thead>
									<tr class="border-b bg-muted/30 text-left font-semibold uppercase tracking-wider text-muted-foreground">
										<th class="px-3 py-2.5">{t('Waktu')}</th>
										<th class="px-3 py-2.5">{t('Aksi')}</th>
										<th class="px-3 py-2.5">{t('Aktor')}</th>
										<th class="px-3 py-2.5">{t('Entitas')}</th>
										<th class="px-3 py-2.5">{t('Detail')}</th>
										<th class="px-3 py-2.5 text-right">{t('Aksi')}</th>
									</tr>
								</thead>
								<tbody class="divide-y">
									{#each filteredAuditEvents as ev (ev.id)}
										<tr class="transition-colors hover:bg-accent/40">
											<td class="whitespace-nowrap px-3 py-2.5 font-mono text-[11px] text-muted-foreground">
												{ev.timestamp || ev.created_at || '—'}
											</td>
											<td class="px-3 py-2.5">
												<Badge variant={getBadgeVariant(ev.action)} class="text-[10px] uppercase">
													{ev.action || 'EVENT'}
												</Badge>
											</td>
											<td class="max-w-[140px] truncate px-3 py-2.5 font-medium text-foreground">
												{ev.user || ev.actor || 'System'}
											</td>
											<td class="max-w-[120px] truncate px-3 py-2.5 font-mono text-[11px]">
												{ev.entity || ev.target || '—'}
											</td>
											<td class="max-w-[200px] truncate px-3 py-2.5 text-muted-foreground">
												{cellPreview(ev, 'details') !== '—' ? cellPreview(ev, 'details') : cellPreview(ev, 'message')}
											</td>
											<td class="px-3 py-2.5 text-right">
												<button
													onclick={() => openInspect(ev)}
													class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
													title={t('Lihat Detail')}
												>
													<EyeIcon class="size-3.5" />
												</button>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{/if}
				</CardContent>
			</Card>
		{/if}
	{/if}
</AppShell>

<!-- ==================================================================== -->
<!-- DIALOG 1: INSPECT RECORD                                             -->
<!-- ==================================================================== -->
{#if inspectOpen && inspectRecord}
	<Dialog.Root bind:open={inspectOpen}>
		<Dialog.Content class="max-h-[85vh] sm:max-w-2xl">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base">
					<EyeIcon class="size-4 text-primary" />
					<span>{t('Detail Record')} — <code class="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">{inspectRecord.id}</code></span>
				</Dialog.Title>
				<Dialog.Description>{t('Informasi lengkap record database.')}</Dialog.Description>
			</Dialog.Header>

			<div class="space-y-4 overflow-y-auto py-2">
				<div class="rounded-lg border bg-muted/20 p-3">
					<div class="mb-2 flex items-center justify-between">
						<span class="text-xs font-semibold text-muted-foreground">{t('Salin JSON')}</span>
						<Button size="sm" variant="outline" class="h-7 text-xs" onclick={copyInspectJson}>
							{#if copied}
								<CheckIcon class="size-3 text-emerald-600 dark:text-emerald-400" />
								<span class="ms-1 text-emerald-700 dark:text-emerald-400">{t('Tersalin!')}</span>
							{:else}
								<CopyIcon class="size-3" />
								<span class="ms-1">{t('Salin JSON')}</span>
							{/if}
						</Button>
					</div>
					<pre class="max-h-64 overflow-x-auto rounded bg-background p-3 font-mono text-[11px] leading-relaxed text-foreground select-all">{JSON.stringify(inspectRecord, null, 2)}</pre>
				</div>
			</div>

			<Dialog.Footer class="flex flex-wrap items-center justify-between gap-2">
				<div class="flex items-center gap-2">
					<Button
						size="sm"
						variant="outline"
						onclick={() => {
							if (inspectRecord) cloneRecord(inspectRecord);
						}}
					>
						<CopyIcon class="size-3.5" />
						<span class="ms-1">{t('Klon Record')}</span>
					</Button>
					<Button
						size="sm"
						variant="outline"
						onclick={() => {
							if (inspectRecord) {
								inspectOpen = false;
								openEdit(inspectRecord);
							}
						}}
					>
						<PencilIcon class="size-3.5" />
						<span class="ms-1">{t('Edit Record')}</span>
					</Button>
				</div>
				<Button size="sm" onclick={() => (inspectOpen = false)}>{t('Tutup')}</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- ==================================================================== -->
<!-- DIALOG 2: EDIT / CREATE RECORD                                       -->
<!-- ==================================================================== -->
{#if editOpen}
	<Dialog.Root bind:open={editOpen}>
		<Dialog.Content class="max-h-[85vh] sm:max-w-2xl">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base">
					<DatabaseIcon class="size-4 text-primary" />
					<span>{isNew ? t('Buat Record') : t('Edit Record')} — {activeTable}</span>
				</Dialog.Title>
				<Dialog.Description>
					{isNew ? t('Isi formulir data dalam format JSON yang valid.') : t('Perbarui data record dalam format JSON.')}
				</Dialog.Description>
			</Dialog.Header>

			<div class="grid gap-3 py-2">
				{#if isNew}
					<div class="flex items-center justify-between">
						<span class="text-xs text-muted-foreground">{t('Gunakan Template Standar')}</span>
						<Button size="sm" variant="outline" class="h-7 text-xs" onclick={applyStandardTemplate}>
							<CopyIcon class="size-3" />
							<span class="ms-1">{t('Gunakan Template Standar')}</span>
						</Button>
					</div>
				{/if}

				{#if editError}
					<div class="flex items-center gap-2 rounded-lg bg-destructive/10 px-3 py-2 text-xs font-semibold text-destructive">
						<AlertCircleIcon class="size-4 shrink-0" />
						<span>{editError}</span>
					</div>
				{/if}

				<Textarea bind:value={editJson} rows={14} class="font-mono text-xs" spellcheck="false" />
			</div>

			<Dialog.Footer>
				<Button variant="outline" onclick={() => (editOpen = false)} disabled={saveLoading}>
					{t('Batal')}
				</Button>
				<Button onclick={saveEdit} disabled={saveLoading}>
					{#if saveLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menyimpan...')}</span>
					{:else}
						{t('Simpan')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- ==================================================================== -->
<!-- DIALOG 3: DELETE CONFIRMATION                                        -->
<!-- ==================================================================== -->
{#if deleteOpen}
	<Dialog.Root bind:open={deleteOpen}>
		<Dialog.Content class="sm:max-w-md">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-2 text-base text-destructive">
					<Trash2Icon class="size-4" />
					<span>{t('Hapus Record')}</span>
				</Dialog.Title>
				<Dialog.Description class="pt-2 text-xs">
					{t('Apakah Anda yakin ingin menghapus record ini?')}
					<div class="my-2 rounded bg-muted p-2 font-mono text-xs">
						ID: {deleteTarget?.id} <br />
						{t('Tabel')}: {activeTable}
					</div>
					<span class="text-destructive font-semibold">{t('Tindakan ini tidak dapat dibatalkan.')}</span>
				</Dialog.Description>
			</Dialog.Header>
			<Dialog.Footer>
				<Button variant="outline" onclick={() => (deleteOpen = false)} disabled={deleteLoading}>
					{t('Batal')}
				</Button>
				<Button variant="destructive" onclick={confirmDelete} disabled={deleteLoading}>
					{#if deleteLoading}
						<RefreshCwIcon class="size-3.5 animate-spin" />
						<span class="ms-1.5">{t('Menghapus...')}</span>
					{:else}
						{t('Hapus')}
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
{/if}