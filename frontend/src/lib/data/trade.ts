export type RiskLevel = 'Low' | 'Medium' | 'High';
export type TaskStatus = 'Verified' | 'In Review' | 'Blocked' | 'Pending';

export type TradeProject = {
	id: string;
	name: string;
	buyer: string;
	country: string;
	product: string;
	stage: string;
	readiness: number;
	value: number;
	risk: RiskLevel;
	eta: string;
	incoterm: string;
	hsCode: string;
	port: string;
	payment: string;
};

export type ComplianceTask = {
	name: string;
	owner: string;
	status: TaskStatus;
	due: string;
};

export type PipelineItem = {
	label: string;
	value: number;
};

export type DocumentItem = {
	name: string;
	status: 'Ready' | 'Needs Review' | 'Missing';
	score: number;
};

export type Product = {
	id: string;
	name: string;
	category: string;
	status: 'Enriched' | 'Needs HS Review' | 'Ready';
	hs: string;
	origin: string;
	packaging: string;
	netWeight: string;
	grossWeight: string;
	moq: string;
	leadTime: string;
	certificates: string[];
	readiness: number;
	hsConfidence?: number;
	sku?: string;
	description?: string;
	description_english_b2b?: string;
	material_composition?: string;
	quality_specs?: Record<string, unknown>;
	updatedAt?: string;
};

export type ActivityItem = {
	title: string;
	description: string;
	time: string;
	tone: 'green' | 'blue' | 'orange' | 'red';
};

export type ComplianceRequirement = {
	id: string;
	projectId: string;
	productId: string;
	title: string;
	category: 'HS Classification' | 'Labeling' | 'Certificate' | 'Document' | 'Logistics';
	severity: 'Critical' | 'Major' | 'Minor';
	status: 'Verified' | 'Evidence Uploaded' | 'In Review' | 'Blocked' | 'Not Started';
	owner: string;
	due: string;
	source: string;
	sourceDate: string;
	requiredEvidence: string;
	currentEvidence: string;
	confidence: number;
};

export type TradeDocument = {
	id: string;
	projectId: string;
	type: 'Commercial Invoice' | 'Packing List' | 'Certificate of Origin' | 'Lab Report' | 'Insurance Certificate';
	status: 'Draft' | 'Ready' | 'Needs Review' | 'Approved' | 'Missing';
	version: string;
	owner: string;
	updatedAt: string;
	validationScore: number;
	fields: Record<string, string>;
	checks: Array<{
		label: string;
		status: 'Passed' | 'Warning' | 'Failed';
		detail: string;
	}>;
};

export type Shipment = {
	id: string;
	projectId: string;
	forwarder: string;
	mode: 'Ocean LCL' | 'Ocean FCL' | 'Air Freight';
	route: string;
	status: 'Booking Requested' | 'Customs Submitted' | 'Loaded' | 'In Transit' | 'Delivered' | 'Exception';
	eta: string;
	progress: number;
	container: string;
	bookingNo: string;
	exception?: string;
	milestones: Array<{
		label: string;
		status: 'Done' | 'Current' | 'Pending' | 'Exception';
		time: string;
		note: string;
	}>;
};

export type RFQ = {
	id: string;
	projectId: string;
	buyer: string;
	product: string;
	destination: string;
	quantity: string;
	incoterm: string;
	status: 'Matching' | 'Quoted' | 'Accepted' | 'Closed';
	deadline: string;
	matchScore: number;
	requirements: string[];
	matches: Array<{
		supplier: string;
		catalog: string;
		score: number;
		reason: string;
	}>;
};

export type Quotation = {
	id: string;
	rfqId: string;
	projectId: string;
	supplier: string;
	buyer: string;
	incoterm: string;
	value: number;
	currency: 'USD' | 'IDR';
	status: 'Draft' | 'In Review' | 'Revision Needed' | 'Accepted' | 'Expired';
	validUntil: string;
	margin: number;
	costLines: Array<{
		label: string;
		amount: number;
	}>;
	notes: string;
};

export type SalesOrder = {
	id: string;
	quotationId: string;
	projectId: string;
	buyer: string;
	supplier: string;
	status: 'Draft' | 'Confirmed' | 'Document Prep' | 'In Shipment' | 'Closed';
	incoterm: string;
	value: number;
	currency: 'USD' | 'IDR';
	paymentTerms: string;
	deliveryWindow: string;
	readiness: number;
	lines: Array<{
		product: string;
		quantity: string;
		unitPrice: number;
		total: number;
	}>;
	checklist: Array<{
		label: string;
		status: 'Done' | 'Current' | 'Pending';
	}>;
};

export type CostingScenario = {
	id: string;
	projectId: string;
	productId: string;
	title: string;
	destination: string;
	incoterm: 'EXW' | 'FOB' | 'CIF' | 'DAP';
	currency: 'USD' | 'IDR';
	status: 'Draft' | 'Ready' | 'Needs Review';
	margin: number;
	exchangeRate: number;
	exchangeSource?: string;
	exwPrice: number;
	fobPrice: number;
	cifPrice: number;
	landedCost: number;
	profit: number;
	confidence: number;
	lines: Array<{
		category: 'Production' | 'Origin' | 'Freight' | 'Insurance' | 'Destination' | 'Tax' | 'Margin' | 'Local logistics' | 'Documents' | string;
		label: string;
		amount: number;
	}>;
	risks: string[];
	container?: {
		capacity_20ft?: number;
		capacity_40ft?: number;
		utilization_note?: string;
		tips?: string[];
	};
	cogs_per_unit_idr?: number;
};

export type MarketInsight = {
	id: string;
	productId: string;
	projectId: string;
	country: string;
	marketScore: number;
	complianceComplexity: 'Low' | 'Medium' | 'High';
	logisticsFeasibility: number;
	estimatedMargin: number;
	status: 'Recommended' | 'Watchlist' | 'Needs Research';
	importValue: string;
	growth: string;
	tariff: string;
	entryStrategy: string;
	opportunities: string[];
	risks: string[];
	sources: Array<{
		name: string;
		date: string;
	}>;
};

export type Catalog = {
	id: string;
	productId: string;
	projectId: string;
	title: string;
	status: 'Draft' | 'Published' | 'Needs Review';
	targetMarket: string;
	moq: string;
	leadTime: string;
	priceRange: string;
	incoterms: string[];
	readiness: number;
	updatedAt: string;
	description: string;
	highlights: string[];
	specifications: Array<{
		label: string;
		value: string;
	}>;
	images: number;
	variants: string[];
};

export type Buyer = {
	id: string;
	name: string;
	country: string;
	segment: string;
	status: 'Lead' | 'Qualified' | 'Negotiating' | 'Active' | 'At Risk';
	fitScore: number;
	projectIds: string[];
	interestedProducts: string[];
	estimatedAnnualValue: number;
	paymentProfile: string;
	lastContact: string;
	nextStep: string;
	contact: {
		name: string;
		role: string;
		email: string;
		phone: string;
	};
	signals: Array<{
		label: string;
		detail: string;
		tone: 'green' | 'blue' | 'orange' | 'red';
	}>;
	notes: string[];
};

export type Supplier = {
	id: string;
	name: string;
	location: string;
	category: string;
	status: 'Verified' | 'In Review' | 'Needs Evidence';
	capabilityScore: number;
	productIds: string[];
	capacity: string;
	leadTime: string;
	qualityScore: number;
	complianceScore: number;
	contact: string;
	certificates: string[];
	risks: string[];
	nextAudit: string;
};

export type Payment = {
	id: string;
	orderId: string;
	buyer: string;
	status: 'Pending' | 'Deposit Paid' | 'Due Soon' | 'Overdue' | 'Settled';
	currency: 'USD' | 'IDR';
	amount: number;
	paid: number;
	dueDate: string;
	method: 'Bank Transfer' | 'LC at sight' | 'Net Terms';
	risk: RiskLevel;
	milestones: Array<{
		label: string;
		amount: number;
		status: 'Done' | 'Current' | 'Pending' | 'Overdue';
	}>;
};

export type AnalyticsMetric = {
	label: string;
	value: string;
	change: string;
	tone: 'green' | 'blue' | 'orange' | 'red';
};

export type WorkTask = {
	id: string;
	title: string;
	module: 'Compliance' | 'Documents' | 'Shipment' | 'Payment' | 'Catalog' | 'Supplier';
	projectId: string;
	owner: string;
	priority: 'Low' | 'Medium' | 'High' | 'Critical';
	status: 'Open' | 'In Progress' | 'Blocked' | 'Done';
	due: string;
	description: string;
	checklist: Array<{ label: string; done: boolean }>;
};

export type TradeReport = {
	id: string;
	title: string;
	type: 'Executive' | 'Compliance' | 'Financial' | 'Shipment';
	status: 'Draft' | 'Ready' | 'Scheduled';
	period: string;
	owner: string;
	updatedAt: string;
	sections: string[];
	insights: string[];
};

export type AuditEvent = {
	id: string;
	time: string;
	actor: string;
	action: string;
	module: string;
	entity: string;
	severity: 'Info' | 'Warning' | 'Critical';
	detail: string;
};

export type TeamMember = {
	id: string;
	name: string;
	role: 'Admin' | 'Operations' | 'Compliance' | 'Finance' | 'Sales';
	status: 'Active' | 'Invited' | 'Suspended';
	email: string;
	lastActive: string;
	permissions: string[];
	workload: number;
};

export type NotificationItem = {
	id: string;
	title: string;
	description: string;
	module: string;
	severity: 'Info' | 'Warning' | 'Critical';
	status: 'Unread' | 'Read' | 'Archived';
	time: string;
	href: string;
};

export type Integration = {
	id: string;
	name: string;
	category: 'Logistics' | 'Finance' | 'Compliance' | 'Commerce' | 'AI';
	status: 'Connected' | 'Available' | 'Needs Auth' | 'Error';
	description: string;
	lastSync: string;
	scopes: string[];
};

export type Template = {
	id: string;
	title: string;
	category: 'Document' | 'Email' | 'Workflow' | 'Catalog';
	status: 'Ready' | 'Draft' | 'Needs Review';
	description: string;
	usedBy: string;
	updatedAt: string;
	fields: string[];
};

export type AutomationRule = {
	id: string;
	name: string;
	trigger: string;
	action: string;
	status: 'Active' | 'Paused' | 'Draft';
	module: 'Compliance' | 'Documents' | 'Payments' | 'Shipments' | 'Reports';
	runs: number;
	lastRun: string;
	description: string;
};

export type KnowledgeArticle = {
	id: string;
	title: string;
	category: 'Export Basics' | 'Compliance' | 'Logistics' | 'Finance' | 'Platform';
	status: 'Published' | 'Draft' | 'Needs Review';
	readTime: string;
	updatedAt: string;
	summary: string;
	steps: string[];
};

export type CalendarEvent = {
	id: string;
	title: string;
	date: string;
	time: string;
	type: 'Compliance' | 'Payment' | 'Shipment' | 'Buyer' | 'Supplier';
	status: 'Scheduled' | 'Due Soon' | 'Blocked' | 'Done';
	projectId: string;
	owner: string;
	description: string;
};

export type FileAsset = {
	id: string;
	name: string;
	type: 'Document' | 'Certificate' | 'Image' | 'Evidence' | 'Report';
	status: 'Verified' | 'Needs Review' | 'Missing Metadata' | 'Archived';
	projectId: string;
	owner: string;
	updatedAt: string;
	size: string;
	tags: string[];
	storageName?: string;
	contentType?: string;
};

export type MessageThread = {
	id: string;
	subject: string;
	party: string;
	channel: 'Email' | 'WhatsApp' | 'Portal' | 'Internal';
	status: 'Open' | 'Waiting Reply' | 'Resolved' | 'Escalated';
	lastMessage: string;
	time: string;
	linkedTo: string;
	participants: string[];
};

export type BillingRecord = {
	id: string;
	plan: 'Starter' | 'Growth' | 'Enterprise';
	status: 'Active' | 'Trial' | 'Past Due' | 'Cancelled';
	amount: number;
	currency: 'USD' | 'IDR';
	period: string;
	dueDate: string;
	usage: Array<{ label: string; used: number; limit: number }>;
};

export type SupportTicket = {
	id: string;
	subject: string;
	category: 'Bug' | 'Question' | 'Billing' | 'Integration' | 'Operations';
	status: 'Open' | 'Waiting Reply' | 'Resolved' | 'Escalated';
	priority: 'Low' | 'Medium' | 'High' | 'Critical';
	createdAt: string;
	owner: string;
	description: string;
};

export type ApiKey = {
	id: string;
	name: string;
	prefix: string;
	status: 'Active' | 'Revoked' | 'Expiring Soon';
	scopes: string[];
	createdAt: string;
	lastUsed: string;
	owner: string;
};

export type BusinessProfile = {
	id: string;
	companyName: string;
	address: string;
	productionCapacity: string;
	yearEstablished: number;
	certifications: string[];
	status: 'Complete' | 'Needs Review' | 'Draft';
	owner: string;
	readiness: number;
};

export type UserAccount = {
	id: string;
	email: string;
	fullName: string;
	role: 'Admin' | 'UMKM' | 'Buyer' | 'Forwarder';
	status: 'Active' | 'Invited' | 'Suspended';
	createdAt: string;
	lastLogin: string;
};

export type BuyerRequest = {
	id: string;
	buyerId: string;
	productId: string;
	subject: string;
	status: 'New' | 'Matched' | 'Quoted' | 'Closed';
	destination: string;
	quantity: string;
	deadline: string;
	requirements: string[];
};

export type Forwarder = {
	id: string;
	name: string;
	coverage: string;
	status: 'Verified' | 'In Review' | 'Needs Auth';
	mode: 'Ocean' | 'Air' | 'Multimodal';
	onTimeRate: number;
	quoteSpeed: string;
	lanes: string[];
	contact: string;
	averageRating?: number;
	totalReviews?: number;
};

export type EducationalModule = {
	id: string;
	title: string;
	level: 'Beginner' | 'Intermediate' | 'Advanced';
	status: 'Published' | 'Draft' | 'Needs Review';
	lessons: number;
	completion: number;
	summary: string;
	// Field backend
	description?: string;
	orderIndex?: number;
	articleCount?: number;
	articles?: EducationalArticle[];
	createdAt?: string;
	updatedAt?: string;
};

export type EducationalLesson = {
	id: string;
	moduleId: string;
	title: string;
	duration: string;
	kind: 'Video' | 'Reading' | 'Quiz';
	completed: boolean;
	content: string;
	keyPoints: string[];
};

export type ChatConversation = {
	id: string;
	title: string;
	status: 'Active' | 'Archived';
	updatedAt: string;
	messages: Array<{ role: 'User' | 'AI'; text: string }>;
};

export type ExportAnalysis = {
	id: string;
	productId: string;
	productName: string;
	destination: string;
	status: 'Ready' | 'In Progress' | 'Needs Review';
	hsCode: string;
	confidence: number;
	score: number;
	marketDemand: 'High' | 'Medium' | 'Low';
	duties: string;
	restrictions: string[];
	recommendations: Array<{
		type: 'Certificate' | 'Labeling' | 'Document';
		title: string;
		status: 'Recommended' | 'Required';
		detail: string;
	}>;
	summary: string;
	countryCode?: string;
	statusGrade?: 'Ready' | 'Warning' | 'Critical';
	complianceIssues?: Array<{
		type: string;
		rule_key?: string;
		your_value?: string;
		required_value?: string;
		description?: string;
		severity?: 'critical' | 'major' | 'minor';
	}>;
	productSnapshot?: Record<string, unknown>;
	regulationSnapshot?: unknown[];
	snapshotProductName?: string;
	productChanged?: boolean;
};

export type EducationalArticle = {
	id: string;
	title: string;
	status: 'Published' | 'Draft' | 'Needs Review';
	level: 'Beginner' | 'Intermediate' | 'Advanced';
	readMinutes: number;
	tags: string[];
	summary: string;
	body: string;
	// Field backend (educational CRUD)
	moduleId?: string;
	content?: string;
	videoUrl?: string;
	fileUrl?: string;
	fileName?: string;
	orderIndex?: number;
	createdAt?: string;
	updatedAt?: string;
};

export const navItems = [
	{ label: 'Dashboard', href: '/dashboard' },
	{ label: 'About', href: '/about' },
	{ label: 'Business Profile', href: '/business-profile' },
	{ label: 'Users', href: '/users' },
	{ label: 'Trade Projects', href: '/trade-projects' },
	{ label: 'Products', href: '/products' },
	{ label: 'Export Analysis', href: '/export-analysis' },
	{ label: 'Compliance', href: '/compliance' },
	{ label: 'Markets', href: '/markets' },
	{ label: 'Catalogs', href: '/catalogs' },
	{ label: 'Buyers', href: '/buyers' },
	{ label: 'Buyer Requests', href: '/buyer-requests' },
	{ label: 'Suppliers', href: '/suppliers' },
	{ label: 'Forwarders', href: '/forwarders' },
	{ label: 'RFQ', href: '/rfq' },
	{ label: 'Quotations', href: '/quotations' },
	{ label: 'Costing', href: '/costing' },
	{ label: 'Orders', href: '/orders' },
	{ label: 'Payments', href: '/payments' },
	{ label: 'Tasks', href: '/tasks' },
	{ label: 'Documents', href: '/documents' },
	{ label: 'Shipments', href: '/shipments' },
	{ label: 'Analytics', href: '/analytics' },
	{ label: 'Reports', href: '/reports' },
	{ label: 'Audit Log', href: '/audit' },
	{ label: 'Team', href: '/team' },
	{ label: 'Notifications', href: '/notifications' },
	{ label: 'Integrations', href: '/integrations' },
	{ label: 'Templates', href: '/templates' },
	{ label: 'Automations', href: '/automations' },
	{ label: 'Knowledge Base', href: '/knowledge' },
	{ label: 'Educational', href: '/educational' },
	{ label: 'Chat', href: '/chat' },
	{ label: 'Marketing', href: '/marketing' },
	{ label: 'Calendar', href: '/calendar' },
	{ label: 'Files', href: '/files' },
	{ label: 'Messages', href: '/messages' },
	{ label: 'Billing', href: '/billing' },
	{ label: 'Support', href: '/support' },
	{ label: 'API Keys', href: '/api-keys' },
	{ label: 'Settings', href: '/settings' }
];

export type NavGroup = {
	label: string;
	items: { label: string; href: string }[];
};

/**
 * Sidebar navigation grouped into collapsible sections (shadcn-svelte sidebar-07 style).
 * `Overview` renders flat (no collapsible), the rest render as collapsible groups with sub-items.
 */
export const navGroups: NavGroup[] = [
	{
		label: 'Overview',
		items: [
			{ label: 'Dashboard', href: '/dashboard' },
			{ label: 'About', href: '/about' }
		]
	},
	{
		label: 'Trade Operations',
		items: [
			{ label: 'Business Profile', href: '/business-profile' },
			{ label: 'Trade Projects', href: '/trade-projects' },
			{ label: 'Products', href: '/products' },
			{ label: 'Export Analysis', href: '/export-analysis' },
			{ label: 'Markets', href: '/markets' },
			{ label: 'Catalogs', href: '/catalogs' }
		]
	},
	{
		label: 'Commercial',
		items: [
			{ label: 'Buyers', href: '/buyers' },
			{ label: 'Buyer Requests', href: '/buyer-requests' },
			{ label: 'Suppliers', href: '/suppliers' },
			{ label: 'Forwarders', href: '/forwarders' },
			{ label: 'RFQ', href: '/rfq' },
			{ label: 'Quotations', href: '/quotations' },
			{ label: 'Costing', href: '/costing' },
			{ label: 'Orders', href: '/orders' },
			{ label: 'Payments', href: '/payments' }
		]
	},
	{
		label: 'Fulfillment',
		items: [
			{ label: 'Compliance', href: '/compliance' },
			{ label: 'Tasks', href: '/tasks' },
			{ label: 'Documents', href: '/documents' },
			{ label: 'Shipments', href: '/shipments' }
		]
	},
	{
		label: 'Insights',
		items: [
			{ label: 'Analytics', href: '/analytics' },
			{ label: 'Reports', href: '/reports' },
			{ label: 'Audit Log', href: '/audit' }
		]
	},
	{
		label: 'Workspace',
		items: [
			{ label: 'Team', href: '/team' },
			{ label: 'Calendar', href: '/calendar' },
			{ label: 'Messages', href: '/messages' },
			{ label: 'Chat', href: '/chat' },
			{ label: 'Files', href: '/files' },
			{ label: 'Notifications', href: '/notifications' },
			{ label: 'Automations', href: '/automations' },
			{ label: 'Integrations', href: '/integrations' },
			{ label: 'Templates', href: '/templates' },
			{ label: 'Knowledge Base', href: '/knowledge' },
			{ label: 'Educational', href: '/educational' },
			{ label: 'Marketing', href: '/marketing' }
		]
	},
	{
		label: 'Admin',
		items: [
			{ label: 'Users', href: '/users' },
			{ label: 'Billing', href: '/billing' },
			{ label: 'Support', href: '/support' },
			{ label: 'API Keys', href: '/api-keys' },
			{ label: 'Settings', href: '/settings' }
		]
	}
];

export const projects: TradeProject[] = [
	{
		id: 'EXP-2408-017',
		name: 'Japan Coffee Trial Shipment',
		buyer: 'Hikari Foods Co.',
		country: 'Japan',
		product: 'Gayo Arabica Coffee Beans',
		stage: 'Compliance Review',
		readiness: 82,
		value: 42800,
		risk: 'Medium',
		eta: '18 Sep 2026',
		incoterm: 'FOB Tanjung Priok',
		hsCode: '0901.21',
		port: 'Tanjung Priok to Yokohama',
		payment: '30% deposit, 70% before shipment'
	},
	{
		id: 'EXP-2408-021',
		name: 'EU Rattan Furniture Program',
		buyer: 'Nordhaus Living',
		country: 'Germany',
		product: 'Handwoven Rattan Chair Set',
		stage: 'Quotation',
		readiness: 74,
		value: 96500,
		risk: 'High',
		eta: '04 Oct 2026',
		incoterm: 'CIF Hamburg',
		hsCode: '9401.53',
		port: 'Tanjung Perak to Hamburg',
		payment: 'LC at sight'
	},
	{
		id: 'EXP-2408-026',
		name: 'Singapore Organic Snacks',
		buyer: 'Merlion Grocers',
		country: 'Singapore',
		product: 'Cassava Chips Sea Salt',
		stage: 'Documents',
		readiness: 91,
		value: 21800,
		risk: 'Low',
		eta: '29 Aug 2026',
		incoterm: 'DAP Singapore DC',
		hsCode: '2005.99',
		port: 'Belawan to Singapore',
		payment: 'Net 21 after delivery'
	}
];

export const complianceTasks: ComplianceTask[] = [
	{ name: 'HS classification confirmation', owner: 'Compliance', status: 'In Review', due: 'Today' },
	{ name: 'Japanese nutrition label proof', owner: 'Exporter', status: 'Blocked', due: 'Tomorrow' },
	{ name: 'Packing list auto-validation', owner: 'System', status: 'Verified', due: 'Done' },
	{ name: 'Forwarder rate validity check', owner: 'Logistics', status: 'Pending', due: '2 days' }
];

export const complianceRequirements: ComplianceRequirement[] = [
	{
		id: 'CMP-JP-001',
		projectId: 'EXP-2408-017',
		productId: 'PRD-COF-001',
		title: 'Confirm HS classification rationale for roasted coffee',
		category: 'HS Classification',
		severity: 'Major',
		status: 'In Review',
		owner: 'Compliance Officer',
		due: 'Today',
		source: 'Japan Customs tariff schedule',
		sourceDate: '2026-07-28',
		requiredEvidence: 'Classification rationale and product composition statement',
		currentEvidence: 'AI candidate code available; reviewer note missing',
		confidence: 84
	},
	{
		id: 'CMP-JP-002',
		projectId: 'EXP-2408-017',
		productId: 'PRD-COF-001',
		title: 'Japanese nutrition and allergen label proof',
		category: 'Labeling',
		severity: 'Critical',
		status: 'Blocked',
		owner: 'Exporter',
		due: 'Tomorrow',
		source: 'Consumer Affairs Agency Japan food labeling guidance',
		sourceDate: '2026-07-30',
		requiredEvidence: 'Japanese label artwork, nutrition facts, importer review',
		currentEvidence: 'English label only',
		confidence: 79
	},
	{
		id: 'CMP-EU-004',
		projectId: 'EXP-2408-021',
		productId: 'PRD-FUR-014',
		title: 'SVLK certificate scope must match rattan furniture shipment',
		category: 'Certificate',
		severity: 'Critical',
		status: 'Evidence Uploaded',
		owner: 'Exporter',
		due: '2 days',
		source: 'EU timber regulation due-diligence requirement',
		sourceDate: '2026-07-21',
		requiredEvidence: 'Valid SVLK certificate, scope page, supplier declaration',
		currentEvidence: 'SVLK certificate uploaded; scope verification pending',
		confidence: 88
	},
	{
		id: 'CMP-SG-003',
		projectId: 'EXP-2408-026',
		productId: 'PRD-SNK-006',
		title: 'Packing list quantity matches commercial invoice',
		category: 'Document',
		severity: 'Minor',
		status: 'Verified',
		owner: 'System',
		due: 'Done',
		source: 'Internal document consistency rule',
		sourceDate: '2026-08-05',
		requiredEvidence: 'Invoice and packing list generated from same order lines',
		currentEvidence: 'Auto-validation passed',
		confidence: 100
	}
];

export const pipeline: PipelineItem[] = [
	{ label: 'Product', value: 100 },
	{ label: 'HS Code', value: 86 },
	{ label: 'Compliance', value: 72 },
	{ label: 'Costing', value: 91 },
	{ label: 'Documents', value: 63 },
	{ label: 'Shipment', value: 38 }
];

export const documents: DocumentItem[] = [
	{ name: 'Commercial Invoice', status: 'Ready', score: 100 },
	{ name: 'Packing List', status: 'Ready', score: 100 },
	{ name: 'Certificate of Origin', status: 'Needs Review', score: 64 },
	{ name: 'Lab Report', status: 'Missing', score: 0 }
];

export const tradeDocuments: TradeDocument[] = [
	{
		id: 'DOC-JP-INV-001',
		projectId: 'EXP-2408-017',
		type: 'Commercial Invoice',
		status: 'Ready',
		version: 'v1.2',
		owner: 'Operations',
		updatedAt: '2026-08-05 10:42',
		validationScore: 96,
		fields: {
			invoiceNo: 'INV-JP-2408-017',
			buyer: 'Hikari Foods Co.',
			incoterm: 'FOB Tanjung Priok',
			currency: 'USD',
			totalValue: '42,800',
			hsCode: '0901.21'
		},
		checks: [
			{ label: 'Invoice quantity matches order', status: 'Passed', detail: '2,000 bags found in both records.' },
			{ label: 'HS code matches product master', status: 'Passed', detail: '0901.21 matches PRD-COF-001.' },
			{ label: 'Incoterm named place present', status: 'Passed', detail: 'FOB Tanjung Priok is explicit.' }
		]
	},
	{
		id: 'DOC-JP-PL-001',
		projectId: 'EXP-2408-017',
		type: 'Packing List',
		status: 'Ready',
		version: 'v1.1',
		owner: 'Warehouse',
		updatedAt: '2026-08-05 10:38',
		validationScore: 100,
		fields: {
			packingNo: 'PL-JP-2408-017',
			cartons: '84',
			netWeight: '500 kg',
			grossWeight: '560 kg',
			containerMode: 'LCL'
		},
		checks: [
			{ label: 'Gross weight exceeds net weight', status: 'Passed', detail: '560 kg > 500 kg.' },
			{ label: 'Carton count available', status: 'Passed', detail: '84 cartons declared.' },
			{ label: 'Product packaging reference available', status: 'Passed', detail: '250g valve bag, 24 bags per carton.' }
		]
	},
	{
		id: 'DOC-JP-COO-001',
		projectId: 'EXP-2408-017',
		type: 'Certificate of Origin',
		status: 'Needs Review',
		version: 'draft',
		owner: 'Compliance',
		updatedAt: '2026-08-05 09:10',
		validationScore: 64,
		fields: {
			origin: 'Indonesia',
			criterion: 'Wholly obtained / produced',
			issuer: 'Chamber of Commerce',
			referenceInvoice: 'INV-JP-2408-017'
		},
		checks: [
			{ label: 'Invoice reference matches', status: 'Passed', detail: 'Reference invoice found.' },
			{ label: 'Origin criterion evidence', status: 'Warning', detail: 'Supplier origin declaration missing.' },
			{ label: 'Issuer field complete', status: 'Passed', detail: 'Chamber of Commerce selected.' }
		]
	},
	{
		id: 'DOC-JP-LAB-001',
		projectId: 'EXP-2408-017',
		type: 'Lab Report',
		status: 'Missing',
		version: '-',
		owner: 'Exporter',
		updatedAt: 'Not uploaded',
		validationScore: 0,
		fields: {
			testType: 'Nutrition and residue test',
			requiredBy: 'Buyer and label review',
			deadline: '2026-08-12'
		},
		checks: [
			{ label: 'File uploaded', status: 'Failed', detail: 'No lab report file found.' },
			{ label: 'Report date valid', status: 'Failed', detail: 'Cannot validate before upload.' },
			{ label: 'Product batch reference', status: 'Warning', detail: 'Batch number will be required.' }
		]
	}
];

export const shipments: Shipment[] = [
	{
		id: 'SHP-JP-017',
		projectId: 'EXP-2408-017',
		forwarder: 'Nusantara Global Logistics',
		mode: 'Ocean LCL',
		route: 'Tanjung Priok - Yokohama',
		status: 'Customs Submitted',
		eta: '18 Sep 2026',
		progress: 48,
		container: 'LCL / 2.4 CBM',
		bookingNo: 'NGL-JP-240817',
		milestones: [
			{ label: 'Booking Confirmed', status: 'Done', time: '2026-08-04 09:00', note: 'Space confirmed with co-loader.' },
			{ label: 'Cargo Ready', status: 'Done', time: '2026-08-07 14:30', note: '84 cartons ready at exporter warehouse.' },
			{ label: 'Picked Up', status: 'Done', time: '2026-08-08 08:10', note: 'Truck departed Aceh consolidation point.' },
			{ label: 'Customs Submitted', status: 'Current', time: '2026-08-10 11:15', note: 'Export declaration under review.' },
			{ label: 'Loaded', status: 'Pending', time: 'Planned 2026-08-13', note: 'Awaiting customs clearance.' },
			{ label: 'Departed', status: 'Pending', time: 'Planned 2026-08-14', note: 'Yokohama feeder service.' }
		]
	},
	{
		id: 'SHP-EU-021',
		projectId: 'EXP-2408-021',
		forwarder: 'Archipelago Freight Network',
		mode: 'Ocean FCL',
		route: 'Tanjung Perak - Hamburg',
		status: 'Exception',
		eta: '04 Oct 2026',
		progress: 22,
		container: '1x20GP',
		bookingNo: 'AFN-EU-240821',
		exception: 'Forwarder rate validity expires in 2 days. Booking approval required.',
		milestones: [
			{ label: 'Booking Requested', status: 'Done', time: '2026-08-05 15:00', note: 'FCL rate requested.' },
			{ label: 'Rate Confirmed', status: 'Exception', time: '2026-08-06 10:30', note: 'Rate valid until 2026-08-08 only.' },
			{ label: 'Booking Confirmed', status: 'Pending', time: 'Pending', note: 'Requires commercial approval.' },
			{ label: 'Cargo Ready', status: 'Pending', time: 'Planned 2026-09-05', note: 'Production still running.' }
		]
	},
	{
		id: 'SHP-SG-026',
		projectId: 'EXP-2408-026',
		forwarder: 'Merah Putih Express',
		mode: 'Ocean LCL',
		route: 'Belawan - Singapore',
		status: 'Loaded',
		eta: '29 Aug 2026',
		progress: 68,
		container: 'LCL / 1.1 CBM',
		bookingNo: 'MPE-SG-240826',
		milestones: [
			{ label: 'Booking Confirmed', status: 'Done', time: '2026-08-02 13:10', note: 'LCL booking confirmed.' },
			{ label: 'Cargo Ready', status: 'Done', time: '2026-08-09 09:45', note: 'Cargo ready at Medan warehouse.' },
			{ label: 'Customs Cleared', status: 'Done', time: '2026-08-11 16:20', note: 'Export declaration cleared.' },
			{ label: 'Loaded', status: 'Current', time: '2026-08-12 07:30', note: 'Cargo loaded into consolidation container.' },
			{ label: 'Departed', status: 'Pending', time: 'Planned 2026-08-13', note: 'Short-sea service to Singapore.' },
			{ label: 'Arrived', status: 'Pending', time: 'Planned 2026-08-15', note: 'Destination customs handoff.' }
		]
	}
];

export const rfqs: RFQ[] = [
	{
		id: 'RFQ-0891',
		projectId: 'EXP-2408-017',
		buyer: 'Hikari Foods Co.',
		product: 'Gayo Arabica Coffee Beans',
		destination: 'Japan',
		quantity: '2,000 bags / 500 kg',
		incoterm: 'FOB Tanjung Priok',
		status: 'Matching',
		deadline: '2026-08-12',
		matchScore: 86,
		requirements: ['HS 0901.21 candidate', 'Japanese label review', 'Lab report before shipment', 'FOB price validity 14 days'],
		matches: [
			{ supplier: 'PT Kopi Gayo Nusantara', catalog: 'Premium Gayo Arabica 250g', score: 86, reason: 'Strong HS/category fit and capacity available.' },
			{ supplier: 'Aceh Highland Beans', catalog: 'Arabica Green Beans Bulk', score: 62, reason: 'Category fit but packaging differs from RFQ.' }
		]
	},
	{
		id: 'RFQ-0903',
		projectId: 'EXP-2408-021',
		buyer: 'Nordhaus Living',
		product: 'Handwoven Rattan Chair Set',
		destination: 'Germany',
		quantity: '120 sets',
		incoterm: 'CIF Hamburg',
		status: 'Quoted',
		deadline: '2026-08-16',
		matchScore: 74,
		requirements: ['SVLK scope evidence', 'Fumigation certificate', 'KD carton packaging', 'CIF Hamburg rate'],
		matches: [
			{ supplier: 'Cirebon Rattan Works', catalog: 'Handwoven Rattan Chair Set', score: 74, reason: 'Good product fit; SVLK scope verification pending.' },
			{ supplier: 'Java Natural Living', catalog: 'Rattan Lounge Series', score: 68, reason: 'Similar material but MOQ above buyer target.' }
		]
	},
	{
		id: 'RFQ-0914',
		projectId: 'EXP-2408-026',
		buyer: 'Merlion Grocers',
		product: 'Cassava Chips Sea Salt',
		destination: 'Singapore',
		quantity: '5,000 pouches',
		incoterm: 'DAP Singapore DC',
		status: 'Accepted',
		deadline: '2026-08-09',
		matchScore: 91,
		requirements: ['Halal certificate', 'HACCP', 'Nutrition facts ready', 'Retail pouch packaging'],
		matches: [
			{ supplier: 'North Sumatra Snacks', catalog: 'Cassava Chips Sea Salt', score: 91, reason: 'All core requirements satisfied.' }
		]
	}
];

export const quotations: Quotation[] = [
	{
		id: 'Q-2408-017-A',
		rfqId: 'RFQ-0891',
		projectId: 'EXP-2408-017',
		supplier: 'PT Kopi Gayo Nusantara',
		buyer: 'Hikari Foods Co.',
		incoterm: 'FOB Tanjung Priok',
		value: 42800,
		currency: 'USD',
		status: 'In Review',
		validUntil: '2026-08-20',
		margin: 22,
		notes: 'Pending Japanese label proof and lab report schedule confirmation.',
		costLines: [
			{ label: 'COGS', amount: 28500 },
			{ label: 'Export packaging', amount: 2100 },
			{ label: 'Origin handling', amount: 1250 },
			{ label: 'Margin', amount: 10950 }
		]
	},
	{
		id: 'Q-2408-021-B',
		rfqId: 'RFQ-0903',
		projectId: 'EXP-2408-021',
		supplier: 'Cirebon Rattan Works',
		buyer: 'Nordhaus Living',
		incoterm: 'CIF Hamburg',
		value: 96500,
		currency: 'USD',
		status: 'Revision Needed',
		validUntil: '2026-08-08',
		margin: 18,
		notes: 'Freight rate expires soon; CIF should be revised with new validity window.',
		costLines: [
			{ label: 'COGS', amount: 64100 },
			{ label: 'Export packing', amount: 7200 },
			{ label: 'Ocean freight', amount: 10800 },
			{ label: 'Insurance', amount: 1250 },
			{ label: 'Margin', amount: 13150 }
		]
	},
	{
		id: 'Q-2408-026-A',
		rfqId: 'RFQ-0914',
		projectId: 'EXP-2408-026',
		supplier: 'North Sumatra Snacks',
		buyer: 'Merlion Grocers',
		incoterm: 'DAP Singapore DC',
		value: 21800,
		currency: 'USD',
		status: 'Accepted',
		validUntil: '2026-08-30',
		margin: 24,
		notes: 'Accepted and converted to document preparation.',
		costLines: [
			{ label: 'COGS', amount: 13200 },
			{ label: 'Retail packaging', amount: 1850 },
			{ label: 'Logistics and delivery', amount: 2250 },
			{ label: 'Margin', amount: 4500 }
		]
	}
];

export const orders: SalesOrder[] = [
	{
		id: 'SO-2408-026',
		quotationId: 'Q-2408-026-A',
		projectId: 'EXP-2408-026',
		buyer: 'Merlion Grocers',
		supplier: 'North Sumatra Snacks',
		status: 'Document Prep',
		incoterm: 'DAP Singapore DC',
		value: 21800,
		currency: 'USD',
		paymentTerms: 'Net 21 after delivery',
		deliveryWindow: '24-29 Aug 2026',
		readiness: 88,
		lines: [
			{ product: 'Cassava Chips Sea Salt', quantity: '5,000 pouches', unitPrice: 4.36, total: 21800 }
		],
		checklist: [
			{ label: 'Quotation accepted', status: 'Done' },
			{ label: 'Commercial invoice generated', status: 'Current' },
			{ label: 'Packing list approved', status: 'Pending' },
			{ label: 'Shipment booking confirmed', status: 'Pending' }
		]
	},
	{
		id: 'SO-2408-017',
		quotationId: 'Q-2408-017-A',
		projectId: 'EXP-2408-017',
		buyer: 'Hikari Foods Co.',
		supplier: 'PT Kopi Gayo Nusantara',
		status: 'Draft',
		incoterm: 'FOB Tanjung Priok',
		value: 42800,
		currency: 'USD',
		paymentTerms: '30% deposit, 70% before shipment',
		deliveryWindow: '12-18 Sep 2026',
		readiness: 71,
		lines: [
			{ product: 'Gayo Arabica Coffee Beans', quantity: '2,000 bags', unitPrice: 21.4, total: 42800 }
		],
		checklist: [
			{ label: 'Quotation accepted', status: 'Pending' },
			{ label: 'Compliance blockers resolved', status: 'Current' },
			{ label: 'Pro forma invoice issued', status: 'Pending' },
			{ label: 'Deposit received', status: 'Pending' }
		]
	},
	{
		id: 'SO-2408-021',
		quotationId: 'Q-2408-021-B',
		projectId: 'EXP-2408-021',
		buyer: 'Nordhaus Living',
		supplier: 'Cirebon Rattan Works',
		status: 'Draft',
		incoterm: 'CIF Hamburg',
		value: 96500,
		currency: 'USD',
		paymentTerms: 'LC at sight',
		deliveryWindow: '28 Sep-04 Oct 2026',
		readiness: 59,
		lines: [
			{ product: 'Handwoven Rattan Chair Set', quantity: '120 sets', unitPrice: 804.17, total: 96500 }
		],
		checklist: [
			{ label: 'Quotation revised', status: 'Current' },
			{ label: 'Freight rate renewed', status: 'Pending' },
			{ label: 'SVLK scope verified', status: 'Pending' },
			{ label: 'LC terms confirmed', status: 'Pending' }
		]
	}
];

export const costingScenarios: CostingScenario[] = [
	{
		id: 'CST-JP-017',
		projectId: 'EXP-2408-017',
		productId: 'PRD-COF-001',
		title: 'Japan Coffee FOB Base Case',
		destination: 'Japan',
		incoterm: 'FOB',
		currency: 'USD',
		status: 'Ready',
		margin: 22,
		exchangeRate: 16250,
		exwPrice: 39150,
		fobPrice: 42800,
		cifPrice: 46200,
		landedCost: 51380,
		profit: 10950,
		confidence: 84,
		lines: [
			{ category: 'Production', label: 'COGS', amount: 28500 },
			{ category: 'Origin', label: 'Export packaging', amount: 2100 },
			{ category: 'Origin', label: 'Inland and origin handling', amount: 1550 },
			{ category: 'Freight', label: 'Ocean LCL estimate', amount: 3400 },
			{ category: 'Insurance', label: 'Cargo insurance', amount: 420 },
			{ category: 'Destination', label: 'Japan handling estimate', amount: 1780 },
			{ category: 'Tax', label: 'Estimated duty and tax reserve', amount: 3000 },
			{ category: 'Margin', label: 'Target margin', amount: 10950 }
		],
		risks: ['Freight estimate not yet converted to forwarder booking', 'Lab report cost may affect final margin']
	},
	{
		id: 'CST-EU-021',
		projectId: 'EXP-2408-021',
		productId: 'PRD-FUR-014',
		title: 'EU Rattan CIF Hamburg Review',
		destination: 'Germany',
		incoterm: 'CIF',
		currency: 'USD',
		status: 'Needs Review',
		margin: 18,
		exchangeRate: 16250,
		exwPrice: 82450,
		fobPrice: 84450,
		cifPrice: 96500,
		landedCost: 112800,
		profit: 13150,
		confidence: 71,
		lines: [
			{ category: 'Production', label: 'COGS', amount: 64100 },
			{ category: 'Origin', label: 'KD export packing', amount: 7200 },
			{ category: 'Origin', label: 'Origin handling and trucking', amount: 3150 },
			{ category: 'Freight', label: '20GP ocean freight', amount: 10800 },
			{ category: 'Insurance', label: 'Cargo insurance', amount: 1250 },
			{ category: 'Destination', label: 'Hamburg destination handling estimate', amount: 5200 },
			{ category: 'Tax', label: 'Duty/VAT reserve estimate', amount: 11100 },
			{ category: 'Margin', label: 'Target margin', amount: 13150 }
		],
		risks: ['Forwarder rate expires in 2 days', 'SVLK scope review may add documentation cost']
	},
	{
		id: 'CST-SG-026',
		projectId: 'EXP-2408-026',
		productId: 'PRD-SNK-006',
		title: 'Singapore Snacks DAP Accepted Case',
		destination: 'Singapore',
		incoterm: 'DAP',
		currency: 'USD',
		status: 'Ready',
		margin: 24,
		exchangeRate: 16250,
		exwPrice: 17300,
		fobPrice: 18750,
		cifPrice: 20250,
		landedCost: 21800,
		profit: 4500,
		confidence: 91,
		lines: [
			{ category: 'Production', label: 'COGS', amount: 13200 },
			{ category: 'Origin', label: 'Retail packaging', amount: 1850 },
			{ category: 'Origin', label: 'Origin handling', amount: 700 },
			{ category: 'Freight', label: 'Singapore LCL freight', amount: 1500 },
			{ category: 'Destination', label: 'DAP local delivery', amount: 750 },
			{ category: 'Tax', label: 'Destination reserve', amount: 800 },
			{ category: 'Margin', label: 'Target margin', amount: 4500 }
		],
		risks: ['Currency movement above 3% requires quote revision']
	}
];

export const marketInsights: MarketInsight[] = [
	{
		id: 'MKT-JP-COF',
		productId: 'PRD-COF-001',
		projectId: 'EXP-2408-017',
		country: 'Japan',
		marketScore: 84,
		complianceComplexity: 'Medium',
		logisticsFeasibility: 78,
		estimatedMargin: 22,
		status: 'Recommended',
		importValue: '$1.61B roasted/green coffee category',
		growth: '+5.8% YoY specialty segment signal',
		tariff: 'Low tariff exposure; labeling and residue evidence required',
		entryStrategy: 'Start with specialty importer trial shipment and bilingual label pack.',
		opportunities: ['Specialty coffee demand remains resilient', 'Importer already accepts FOB trial shipment', 'Premium origin story is strong for Gayo'],
		risks: ['Japanese label proof is blocked', 'Lab report timing can delay shipment', 'Importer quality claims need evidence'],
		sources: [
			{ name: 'Japan customs import statistics', date: '2026-07-28' },
			{ name: 'Trade Map coffee category trend', date: '2026-07-30' },
			{ name: 'Buyer RFQ requirement data', date: '2026-08-05' }
		]
	},
	{
		id: 'MKT-DE-FUR',
		productId: 'PRD-FUR-014',
		projectId: 'EXP-2408-021',
		country: 'Germany',
		marketScore: 69,
		complianceComplexity: 'High',
		logisticsFeasibility: 62,
		estimatedMargin: 18,
		status: 'Watchlist',
		importValue: '$4.2B furniture import category',
		growth: '+2.1% YoY, competitive market',
		tariff: 'Moderate tariff exposure; timber/rattan due diligence critical',
		entryStrategy: 'Proceed only after SVLK scope and freight validity are resolved.',
		opportunities: ['Large home-living import market', 'Buyer has concrete volume request', 'Handmade natural material positioning fits niche retail'],
		risks: ['SVLK scope not fully verified', 'CIF freight rate expires soon', 'Destination VAT/duty reserve compresses margin'],
		sources: [
			{ name: 'EU furniture import data', date: '2026-07-21' },
			{ name: 'Forwarder CIF quote', date: '2026-08-06' },
			{ name: 'EU due diligence requirement summary', date: '2026-07-21' }
		]
	},
	{
		id: 'MKT-SG-SNK',
		productId: 'PRD-SNK-006',
		projectId: 'EXP-2408-026',
		country: 'Singapore',
		marketScore: 91,
		complianceComplexity: 'Low',
		logisticsFeasibility: 93,
		estimatedMargin: 24,
		status: 'Recommended',
		importValue: '$890M packaged snack category',
		growth: '+6.4% YoY premium snack signal',
		tariff: 'Low trade barrier; retail labeling and shelf-life evidence ready',
		entryStrategy: 'Scale from accepted DAP order into recurring monthly replenishment.',
		opportunities: ['Short logistics route', 'Accepted quotation already converted to order', 'Halal and HACCP evidence ready'],
		risks: ['Currency movement above 3% requires revision', 'Retail reorder depends on first delivery performance'],
		sources: [
			{ name: 'Singapore packaged food import trend', date: '2026-08-01' },
			{ name: 'Accepted buyer RFQ', date: '2026-08-05' },
			{ name: 'Internal landed-cost scenario', date: '2026-08-06' }
		]
	}
];

export const catalogs: Catalog[] = [
	{
		id: 'CAT-COF-JP-001',
		productId: 'PRD-COF-001',
		projectId: 'EXP-2408-017',
		title: 'Premium Gayo Arabica Coffee Beans 250g',
		status: 'Needs Review',
		targetMarket: 'Japan specialty importers',
		moq: '2,000 bags',
		leadTime: '21 days after deposit',
		priceRange: 'FOB USD 20.80-21.40 per bag',
		incoterms: ['EXW', 'FOB'],
		readiness: 78,
		updatedAt: '2026-08-05 11:20',
		description:
			'Single-origin Gayo Arabica coffee beans prepared for specialty retail and importer trial shipment, packed in export-ready valve bags.',
		highlights: ['Single-origin Aceh profile', 'Export valve bag packaging', 'FOB Tanjung Priok quote available', 'HS candidate 0901.21'],
		specifications: [
			{ label: 'Origin', value: 'Aceh, Indonesia' },
			{ label: 'Packaging', value: '250g valve bag, 24 bags per carton' },
			{ label: 'Shelf readiness', value: 'Japanese label proof pending' },
			{ label: 'Certificates', value: 'Halal, lab report required' }
		],
		images: 5,
		variants: ['Medium roast 250g', 'Dark roast 250g']
	},
	{
		id: 'CAT-FUR-EU-014',
		productId: 'PRD-FUR-014',
		projectId: 'EXP-2408-021',
		title: 'Handwoven Rattan Chair Set for EU Retail',
		status: 'Draft',
		targetMarket: 'Germany home-living buyers',
		moq: '120 sets',
		leadTime: '45 days after order confirmation',
		priceRange: 'CIF Hamburg USD 780-805 per set',
		incoterms: ['FOB', 'CIF'],
		readiness: 62,
		updatedAt: '2026-08-04 16:05',
		description:
			'Natural rattan chair set designed for boutique home-living retailers, supplied in KD export cartons with corner protection.',
		highlights: ['Handwoven natural material', 'KD export carton', 'SVLK certificate in review', 'CIF Hamburg scenario available'],
		specifications: [
			{ label: 'Origin', value: 'Cirebon, Indonesia' },
			{ label: 'Packaging', value: 'KD carton with corner protection' },
			{ label: 'Certificate', value: 'SVLK scope verification pending' },
			{ label: 'Container', value: '1x20GP scenario' }
		],
		images: 8,
		variants: ['Natural finish', 'Walnut finish']
	},
	{
		id: 'CAT-SNK-SG-006',
		productId: 'PRD-SNK-006',
		projectId: 'EXP-2408-026',
		title: 'Cassava Chips Sea Salt Retail Pouch',
		status: 'Published',
		targetMarket: 'Singapore grocery distributors',
		moq: '5,000 pouches',
		leadTime: '14 days after PO',
		priceRange: 'DAP Singapore DC USD 4.36 per pouch',
		incoterms: ['FOB', 'CIF', 'DAP'],
		readiness: 94,
		updatedAt: '2026-08-06 09:35',
		description:
			'Crispy Indonesian cassava chips in retail-ready sea salt flavor with Halal and HACCP evidence prepared for Singapore distribution.',
		highlights: ['Halal and HACCP ready', 'Retail pouch format', 'Accepted DAP quote', 'Short Singapore logistics route'],
		specifications: [
			{ label: 'Origin', value: 'North Sumatra, Indonesia' },
			{ label: 'Packaging', value: '80g pouch, 48 pouches per carton' },
			{ label: 'Certificates', value: 'Halal, HACCP, nutrition facts ready' },
			{ label: 'MOQ', value: '5,000 pouches' }
		],
		images: 6,
		variants: ['Sea salt 80g', 'Spicy 80g']
	}
];

export const buyers: Buyer[] = [
	{
		id: 'BUY-HIKARI-JP',
		name: 'Hikari Foods Co.',
		country: 'Japan',
		segment: 'Specialty food importer',
		status: 'Negotiating',
		fitScore: 86,
		projectIds: ['EXP-2408-017'],
		interestedProducts: ['Gayo Arabica Coffee Beans'],
		estimatedAnnualValue: 185000,
		paymentProfile: '30% deposit, 70% before shipment',
		lastContact: '2026-08-05 15:40',
		nextStep: 'Send Japanese label proof and lab report timing confirmation.',
		contact: {
			name: 'Aya Nakamura',
			role: 'Import Category Manager',
			email: 'aya.nakamura@hikari-foods.example',
			phone: '+81 45 0000 1901'
		},
		signals: [
			{ label: 'RFQ urgency', detail: 'Quotation deadline in 6 days for trial shipment.', tone: 'orange' },
			{ label: 'Product fit', detail: 'Specialty retail channel matches Gayo origin story.', tone: 'green' },
			{ label: 'Compliance gap', detail: 'Japanese label proof still blocked.', tone: 'red' }
		],
		notes: ['Buyer prefers bilingual catalog copy.', 'Quality claim must cite lab evidence before final PO.']
	},
	{
		id: 'BUY-NORDHAUS-DE',
		name: 'Nordhaus Living',
		country: 'Germany',
		segment: 'Home-living retail chain',
		status: 'At Risk',
		fitScore: 71,
		projectIds: ['EXP-2408-021'],
		interestedProducts: ['Handwoven Rattan Chair Set'],
		estimatedAnnualValue: 420000,
		paymentProfile: 'LC at sight',
		lastContact: '2026-08-04 10:10',
		nextStep: 'Resolve SVLK scope and confirm CIF Hamburg freight validity.',
		contact: {
			name: 'Lena Hartmann',
			role: 'Sourcing Lead',
			email: 'lena.hartmann@nordhaus.example',
			phone: '+49 40 0000 2140'
		},
		signals: [
			{ label: 'Large account', detail: 'Potential recurring EU furniture program.', tone: 'blue' },
			{ label: 'Rate expiry', detail: 'Forwarder quote expires in 2 days.', tone: 'red' },
			{ label: 'Certificate risk', detail: 'SVLK scope verification is still pending.', tone: 'orange' }
		],
		notes: ['Buyer requested KD packaging images.', 'Margin sensitive to freight changes above 3%.']
	},
	{
		id: 'BUY-MERLION-SG',
		name: 'Merlion Grocers',
		country: 'Singapore',
		segment: 'Grocery distributor',
		status: 'Active',
		fitScore: 93,
		projectIds: ['EXP-2408-026'],
		interestedProducts: ['Cassava Chips Sea Salt'],
		estimatedAnnualValue: 132000,
		paymentProfile: 'Net 21 after delivery',
		lastContact: '2026-08-06 08:25',
		nextStep: 'Track first shipment performance and prepare reorder proposal.',
		contact: {
			name: 'Daniel Tan',
			role: 'Procurement Manager',
			email: 'daniel.tan@merlion-grocers.example',
			phone: '+65 6000 0914'
		},
		signals: [
			{ label: 'Converted order', detail: 'Accepted DAP quote already moved to sales order.', tone: 'green' },
			{ label: 'Low friction route', detail: 'Short-sea logistics and documents are on track.', tone: 'green' },
			{ label: 'Reorder opportunity', detail: 'Monthly replenishment proposal can follow delivery.', tone: 'blue' }
		],
		notes: ['Buyer wants retail display carton option.', 'Push reorder discussion after delivery confirmation.']
	}
];

export const suppliers: Supplier[] = [
	{
		id: 'SUP-KOPI-GAYO',
		name: 'PT Kopi Gayo Nusantara',
		location: 'Aceh, Indonesia',
		category: 'Coffee processor',
		status: 'Verified',
		capabilityScore: 88,
		productIds: ['PRD-COF-001'],
		capacity: '12,000 retail bags / month',
		leadTime: '21 days',
		qualityScore: 91,
		complianceScore: 82,
		contact: 'Rizal Fahmi · Export Manager',
		certificates: ['Halal', 'Organic in progress', 'Origin declaration'],
		risks: ['Lab report scheduling depends on batch release', 'Japanese label artwork still pending'],
		nextAudit: '2026-09-12'
	},
	{
		id: 'SUP-CIREBON-RATTAN',
		name: 'Cirebon Rattan Works',
		location: 'Cirebon, Indonesia',
		category: 'Furniture manufacturer',
		status: 'Needs Evidence',
		capabilityScore: 74,
		productIds: ['PRD-FUR-014'],
		capacity: '180 sets / month',
		leadTime: '45 days',
		qualityScore: 78,
		complianceScore: 61,
		contact: 'Maya Kartika · Commercial Lead',
		certificates: ['SVLK scope pending', 'Fumigation partner available'],
		risks: ['SVLK scope must match shipment', 'CIF freight validity expires soon'],
		nextAudit: '2026-08-20'
	},
	{
		id: 'SUP-MEDAN-SNACKS',
		name: 'Medan Crispy Foods',
		location: 'North Sumatra, Indonesia',
		category: 'Processed food factory',
		status: 'Verified',
		capabilityScore: 93,
		productIds: ['PRD-SNK-006'],
		capacity: '75,000 pouches / month',
		leadTime: '14 days',
		qualityScore: 94,
		complianceScore: 95,
		contact: 'Sinta Lestari · QA Director',
		certificates: ['Halal', 'HACCP', 'Nutrition facts ready'],
		risks: ['Reorder planning depends on first delivery acceptance'],
		nextAudit: '2026-10-04'
	}
];

export const payments: Payment[] = [
	{
		id: 'PAY-JP-017',
		orderId: 'SO-2408-017',
		buyer: 'Hikari Foods Co.',
		status: 'Deposit Paid',
		currency: 'USD',
		amount: 42800,
		paid: 12840,
		dueDate: '2026-08-20',
		method: 'Bank Transfer',
		risk: 'Medium',
		milestones: [
			{ label: '30% deposit', amount: 12840, status: 'Done' },
			{ label: '70% before shipment', amount: 29960, status: 'Current' }
		]
	},
	{
		id: 'PAY-EU-021',
		orderId: 'SO-2408-021',
		buyer: 'Nordhaus Living',
		status: 'Due Soon',
		currency: 'USD',
		amount: 96500,
		paid: 0,
		dueDate: '2026-08-14',
		method: 'LC at sight',
		risk: 'High',
		milestones: [
			{ label: 'LC issuance', amount: 96500, status: 'Current' },
			{ label: 'Document presentation', amount: 96500, status: 'Pending' }
		]
	},
	{
		id: 'PAY-SG-026',
		orderId: 'SO-2408-026',
		buyer: 'Merlion Grocers',
		status: 'Settled',
		currency: 'USD',
		amount: 21800,
		paid: 21800,
		dueDate: '2026-09-19',
		method: 'Net Terms',
		risk: 'Low',
		milestones: [
			{ label: 'Delivery confirmation', amount: 0, status: 'Done' },
			{ label: 'Net 21 settlement', amount: 21800, status: 'Done' }
		]
	}
];

export const analyticsMetrics: AnalyticsMetric[] = [
	{ label: 'Active pipeline', value: '$161.1K', change: '+18% vs last month', tone: 'green' },
	{ label: 'Avg readiness', value: '82%', change: '+6 pts after catalog rollout', tone: 'blue' },
	{ label: 'Open risk items', value: '5', change: '2 critical compliance blockers', tone: 'orange' },
	{ label: 'On-time shipment', value: '67%', change: 'EU booking at risk', tone: 'red' }
];

export const workTasks: WorkTask[] = [
	{
		id: 'TSK-JP-LABEL',
		title: 'Upload Japanese label proof',
		module: 'Compliance',
		projectId: 'EXP-2408-017',
		owner: 'Exporter',
		priority: 'Critical',
		status: 'Blocked',
		due: 'Tomorrow',
		description: 'Japanese nutrition and allergen label proof is required before quotation approval and shipment document finalization.',
		checklist: [
			{ label: 'Translate nutrition facts', done: true },
			{ label: 'Attach Japanese artwork', done: false },
			{ label: 'Importer review confirmation', done: false }
		]
	},
	{
		id: 'TSK-EU-SVLK',
		title: 'Verify SVLK certificate scope',
		module: 'Supplier',
		projectId: 'EXP-2408-021',
		owner: 'Compliance Officer',
		priority: 'High',
		status: 'In Progress',
		due: '2 days',
		description: 'Rattan furniture shipment requires SVLK scope evidence before the EU quotation can be approved.',
		checklist: [
			{ label: 'Collect certificate scope page', done: true },
			{ label: 'Match supplier name and product', done: false },
			{ label: 'Attach due-diligence note', done: false }
		]
	},
	{
		id: 'TSK-SG-REORDER',
		title: 'Prepare Singapore reorder proposal',
		module: 'Payment',
		projectId: 'EXP-2408-026',
		owner: 'Sales Ops',
		priority: 'Medium',
		status: 'Open',
		due: 'Next week',
		description: 'First snack order is on track. Prepare reorder proposal tied to delivery confirmation and retail display carton option.',
		checklist: [
			{ label: 'Confirm delivery milestone', done: true },
			{ label: 'Draft monthly replenishment quote', done: false },
			{ label: 'Add display carton option', done: false }
		]
	}
];

export const tradeReports: TradeReport[] = [
	{
		id: 'RPT-EXEC-2408',
		title: 'August Export Executive Brief',
		type: 'Executive',
		status: 'Ready',
		period: 'August 2026',
		owner: 'Management',
		updatedAt: '2026-08-06 10:20',
		sections: ['Pipeline value', 'Buyer conversion', 'Compliance blockers', 'Shipment risk', 'Cash collection'],
		insights: ['Singapore snack lane is ready for reorder planning.', 'EU furniture margin is exposed to freight validity.', 'Japan coffee approval depends on label proof.']
	},
	{
		id: 'RPT-COMP-2408',
		title: 'Compliance Evidence Report',
		type: 'Compliance',
		status: 'Draft',
		period: 'Current projects',
		owner: 'Compliance Officer',
		updatedAt: '2026-08-05 17:05',
		sections: ['HS code rationale', 'Labeling evidence', 'Certificate coverage', 'Document validation'],
		insights: ['Two critical items remain unresolved.', 'System validation passed packing-list consistency checks.']
	},
	{
		id: 'RPT-FIN-2408',
		title: 'Receivables and Margin Report',
		type: 'Financial',
		status: 'Scheduled',
		period: 'Weekly',
		owner: 'Finance',
		updatedAt: '2026-08-06 08:50',
		sections: ['Collected deposits', 'Open receivables', 'Margin by Incoterm', 'FX sensitivity'],
		insights: ['Receivables remain concentrated in LC issuance for EU furniture.', 'Singapore order is settled in demo state.']
	}
];

export const auditEvents: AuditEvent[] = [
	{ id: 'AUD-1001', time: '2026-08-06 10:42', actor: 'AI Copilot', action: 'Generated market insight', module: 'Markets', entity: 'MKT-SG-SNK', severity: 'Info', detail: 'Singapore snack route scored 91 with low compliance complexity.' },
	{ id: 'AUD-1002', time: '2026-08-06 10:18', actor: 'Operations', action: 'Approved packing list', module: 'Documents', entity: 'DOC-JP-PL-001', severity: 'Info', detail: 'Carton count and gross weight checks passed.' },
	{ id: 'AUD-1003', time: '2026-08-06 09:55', actor: 'Compliance Officer', action: 'Flagged certificate risk', module: 'Suppliers', entity: 'SUP-CIREBON-RATTAN', severity: 'Warning', detail: 'SVLK scope page does not yet prove product coverage.' },
	{ id: 'AUD-1004', time: '2026-08-06 09:20', actor: 'Finance', action: 'Payment reminder prepared', module: 'Payments', entity: 'PAY-EU-021', severity: 'Critical', detail: 'LC issuance is due soon and tied to shipment booking approval.' }
];

export const teamMembers: TeamMember[] = [
	{ id: 'USR-OPS-001', name: 'Nadia Prameswari', role: 'Operations', status: 'Active', email: 'nadia@mauekspor.example', lastActive: '10 minutes ago', permissions: ['Orders', 'Documents', 'Shipments'], workload: 78 },
	{ id: 'USR-CMP-002', name: 'Arman Wijaya', role: 'Compliance', status: 'Active', email: 'arman@mauekspor.example', lastActive: '32 minutes ago', permissions: ['Compliance', 'Suppliers', 'Audit'], workload: 86 },
	{ id: 'USR-FIN-003', name: 'Leony Tan', role: 'Finance', status: 'Invited', email: 'leony@mauekspor.example', lastActive: 'Invitation pending', permissions: ['Payments', 'Reports', 'Costing'], workload: 34 },
	{ id: 'USR-SLS-004', name: 'Bima Hartono', role: 'Sales', status: 'Active', email: 'bima@mauekspor.example', lastActive: '1 hour ago', permissions: ['Buyers', 'RFQ', 'Quotations'], workload: 64 }
];

export const notifications: NotificationItem[] = [
	{ id: 'NTF-001', title: 'Japanese label proof blocked', description: 'Critical compliance task needs exporter evidence before quotation approval.', module: 'Compliance', severity: 'Critical', status: 'Unread', time: '8 min ago', href: '/tasks/TSK-JP-LABEL' },
	{ id: 'NTF-002', title: 'EU freight rate expires soon', description: 'CIF Hamburg booking approval should be completed before rate validity ends.', module: 'Shipments', severity: 'Warning', status: 'Unread', time: '24 min ago', href: '/shipments/SHP-EU-021' },
	{ id: 'NTF-003', title: 'Singapore payment settled', description: 'Payment record PAY-SG-026 is complete and ready for reorder follow-up.', module: 'Payments', severity: 'Info', status: 'Read', time: '1 hour ago', href: '/payments/PAY-SG-026' },
	{ id: 'NTF-004', title: 'Analytics refreshed', description: 'Executive dashboard updated with buyer, supplier, cashflow, and shipment signals.', module: 'Analytics', severity: 'Info', status: 'Archived', time: '3 hours ago', href: '/analytics' }
];

export const integrations: Integration[] = [
	{ id: 'INT-FORWARDER', name: 'Forwarder Rate Gateway', category: 'Logistics', status: 'Connected', description: 'Sync freight quotes, booking status, and route exceptions from logistics partners.', lastSync: '2026-08-06 10:30', scopes: ['Rates', 'Bookings', 'Milestones'] },
	{ id: 'INT-BANK', name: 'Bank Payment Tracker', category: 'Finance', status: 'Needs Auth', description: 'Match incoming deposits and settlement events against export payment milestones.', lastSync: 'Not connected', scopes: ['Payments', 'Receivables', 'Reminders'] },
	{ id: 'INT-CUSTOMS', name: 'Customs Reference Library', category: 'Compliance', status: 'Available', description: 'Lookup HS guidance, tariff references, and evidence source dates for target markets.', lastSync: 'Available on demand', scopes: ['HS Codes', 'Tariffs', 'Regulatory Sources'] },
	{ id: 'INT-AI', name: 'MauEkspor AI Copilot', category: 'AI', status: 'Connected', description: 'Generate market insights, catalog copy, task summaries, and report narratives.', lastSync: '2026-08-06 10:42', scopes: ['Market Insight', 'Catalog Copy', 'Reports'] }
];

export const templates: Template[] = [
	{ id: 'TPL-CI-001', title: 'Commercial Invoice Export Template', category: 'Document', status: 'Ready', description: 'Reusable invoice layout with HS code, Incoterm, buyer, and shipment references.', usedBy: 'Documents', updatedAt: '2026-08-06 10:05', fields: ['Invoice number', 'Buyer', 'Incoterm', 'HS code', 'Total value'] },
	{ id: 'TPL-RFQ-EMAIL', title: 'Buyer RFQ Follow-up Email', category: 'Email', status: 'Ready', description: 'Structured reply for importer questions, missing evidence, and quotation next steps.', usedBy: 'RFQ and Buyers', updatedAt: '2026-08-05 16:30', fields: ['Buyer name', 'Product', 'Deadline', 'Evidence request'] },
	{ id: 'TPL-SVLK-WF', title: 'SVLK Evidence Review Workflow', category: 'Workflow', status: 'Needs Review', description: 'Checklist template for supplier certificate collection, scope matching, and audit logging.', usedBy: 'Suppliers and Compliance', updatedAt: '2026-08-04 14:15', fields: ['Supplier', 'Certificate scope', 'Product match', 'Reviewer note'] },
	{ id: 'TPL-CATALOG-FNB', title: 'Food Export Catalog Template', category: 'Catalog', status: 'Draft', description: 'Buyer-facing catalog structure for packaged food products and retail distributors.', usedBy: 'Catalogs', updatedAt: '2026-08-03 09:45', fields: ['MOQ', 'Shelf life', 'Certificates', 'Packaging', 'Price range'] }
];

export const automationRules: AutomationRule[] = [
	{ id: 'AUT-LABEL-BLOCKER', name: 'Create task when label evidence is blocked', trigger: 'Compliance item becomes Blocked', action: 'Create critical task and notify exporter', status: 'Active', module: 'Compliance', runs: 12, lastRun: '2026-08-06 09:18', description: 'Keeps compliance blockers visible in Tasks and Notifications.' },
	{ id: 'AUT-DOC-VALIDATE', name: 'Validate documents after order confirmation', trigger: 'Sales order enters Document Prep', action: 'Run document consistency checks', status: 'Active', module: 'Documents', runs: 8, lastRun: '2026-08-05 17:42', description: 'Automatically checks invoice, packing list, and certificate references.' },
	{ id: 'AUT-PAY-REMINDER', name: 'Send payment reminder before due date', trigger: 'Payment due in 3 days', action: 'Notify finance and buyer owner', status: 'Paused', module: 'Payments', runs: 5, lastRun: '2026-08-04 11:10', description: 'Reduces receivable delays before shipment release.' },
	{ id: 'AUT-REPORT-WEEKLY', name: 'Generate weekly executive report', trigger: 'Every Monday 08:00', action: 'Create executive report draft', status: 'Draft', module: 'Reports', runs: 0, lastRun: 'Not run', description: 'Packages analytics, risks, receivables, and shipment exceptions for management.' }
];

export const knowledgeArticles: KnowledgeArticle[] = [
	{ id: 'KB-EXPORT-START', title: 'How to start an export project', category: 'Export Basics', status: 'Published', readTime: '6 min', updatedAt: '2026-08-01', summary: 'A practical flow from product readiness to buyer RFQ and first shipment.', steps: ['Create a trade project', 'Attach product master data', 'Review target market', 'Build catalog', 'Convert RFQ to quotation'] },
	{ id: 'KB-HS-CODE', title: 'HS code review checklist', category: 'Compliance', status: 'Published', readTime: '5 min', updatedAt: '2026-08-02', summary: 'How to document HS classification rationale and evidence sources.', steps: ['Describe product composition', 'Select candidate HS code', 'Attach customs source', 'Assign reviewer', 'Record confidence'] },
	{ id: 'KB-INCOTERM', title: 'Choosing Incoterms for quotations', category: 'Finance', status: 'Needs Review', readTime: '7 min', updatedAt: '2026-08-03', summary: 'Commercial implications of EXW, FOB, CIF, and DAP in MauEkspor costing.', steps: ['Start with EXW cost', 'Add origin handling', 'Compare freight and insurance', 'Model margin', 'Validate buyer payment terms'] },
	{ id: 'KB-SHIPMENT', title: 'Shipment exception playbook', category: 'Logistics', status: 'Draft', readTime: '4 min', updatedAt: '2026-08-04', summary: 'Operational steps for freight expiry, customs delay, and missing documents.', steps: ['Identify exception source', 'Assign owner', 'Notify buyer if needed', 'Update milestone', 'Log audit event'] }
];

export const calendarEvents: CalendarEvent[] = [
	{ id: 'CAL-JP-LABEL', title: 'Japanese label proof deadline', date: '2026-08-07', time: '10:00', type: 'Compliance', status: 'Blocked', projectId: 'EXP-2408-017', owner: 'Exporter', description: 'Label proof must be uploaded before quote approval.' },
	{ id: 'CAL-EU-LC', title: 'LC issuance follow-up', date: '2026-08-14', time: '15:00', type: 'Payment', status: 'Due Soon', projectId: 'EXP-2408-021', owner: 'Finance', description: 'Follow up with Nordhaus Living on LC issuance.' },
	{ id: 'CAL-SG-DEPART', title: 'Singapore shipment departure', date: '2026-08-13', time: '07:30', type: 'Shipment', status: 'Scheduled', projectId: 'EXP-2408-026', owner: 'Operations', description: 'Short-sea shipment planned to depart Belawan.' },
	{ id: 'CAL-SUP-AUDIT', title: 'Cirebon supplier evidence audit', date: '2026-08-20', time: '11:00', type: 'Supplier', status: 'Scheduled', projectId: 'EXP-2408-021', owner: 'Compliance Officer', description: 'Review SVLK scope and supplier declaration.' }
];

export const fileAssets: FileAsset[] = [
	{ id: 'FIL-CI-JP', name: 'INV-JP-2408-017.pdf', type: 'Document', status: 'Verified', projectId: 'EXP-2408-017', owner: 'Operations', updatedAt: '2026-08-05 10:42', size: '184 KB', tags: ['Commercial Invoice', 'Japan', 'Coffee'] },
	{ id: 'FIL-SVLK-EU', name: 'svlk-scope-cirebon-rattan.pdf', type: 'Certificate', status: 'Needs Review', projectId: 'EXP-2408-021', owner: 'Compliance Officer', updatedAt: '2026-08-05 13:20', size: '2.4 MB', tags: ['SVLK', 'Furniture', 'EU'] },
	{ id: 'FIL-CAT-SG', name: 'cassava-chips-catalog-images.zip', type: 'Image', status: 'Verified', projectId: 'EXP-2408-026', owner: 'Sales Ops', updatedAt: '2026-08-06 09:35', size: '18.6 MB', tags: ['Catalog', 'Snack', 'Singapore'] },
	{ id: 'FIL-LAB-JP', name: 'japan-coffee-lab-report', type: 'Evidence', status: 'Missing Metadata', projectId: 'EXP-2408-017', owner: 'Exporter', updatedAt: 'Draft placeholder', size: '-', tags: ['Lab Report', 'Blocked', 'Label'] }
];

export const messageThreads: MessageThread[] = [
	{ id: 'MSG-HIKARI-LABEL', subject: 'Label proof and lab report timing', party: 'Hikari Foods Co.', channel: 'Email', status: 'Waiting Reply', lastMessage: 'Please confirm if bilingual label artwork can be reviewed by Friday.', time: '18 min ago', linkedTo: 'EXP-2408-017', participants: ['Aya Nakamura', 'Nadia Prameswari', 'Exporter'] },
	{ id: 'MSG-NORDHAUS-LC', subject: 'LC issuance and CIF freight validity', party: 'Nordhaus Living', channel: 'Portal', status: 'Escalated', lastMessage: 'Freight validity expires soon. Finance approval required before booking.', time: '42 min ago', linkedTo: 'PAY-EU-021', participants: ['Lena Hartmann', 'Leony Tan', 'Operations'] },
	{ id: 'MSG-MERLION-REORDER', subject: 'Singapore reorder proposal', party: 'Merlion Grocers', channel: 'WhatsApp', status: 'Open', lastMessage: 'We will share reorder option after first shipment delivery confirmation.', time: '2 hours ago', linkedTo: 'TSK-SG-REORDER', participants: ['Daniel Tan', 'Bima Hartono'] },
	{ id: 'MSG-INTERNAL-SVLK', subject: 'SVLK scope review', party: 'Internal compliance', channel: 'Internal', status: 'Resolved', lastMessage: 'Scope evidence request has been sent to supplier.', time: 'Yesterday', linkedTo: 'SUP-CIREBON-RATTAN', participants: ['Arman Wijaya', 'Maya Kartika'] }
];

export const billingRecords: BillingRecord[] = [
	{
		id: 'BIL-ORG-001',
		plan: 'Growth',
		status: 'Active',
		amount: 249,
		currency: 'USD',
		period: 'August 2026',
		dueDate: '2026-08-28',
		usage: [
			{ label: 'Trade projects', used: 18, limit: 50 },
			{ label: 'AI generations', used: 642, limit: 1000 },
			{ label: 'Team seats', used: 4, limit: 10 }
		]
	}
];

export const supportTickets: SupportTicket[] = [
	{ id: 'SUPPORT-1041', subject: 'Need help configuring bank payment tracker', category: 'Integration', status: 'Open', priority: 'High', createdAt: '2026-08-06 11:05', owner: 'Leony Tan', description: 'Finance team needs help connecting bank payment tracker for LC and deposit matching.' },
	{ id: 'SUPPORT-1038', subject: 'Question about Japanese label evidence workflow', category: 'Operations', status: 'Waiting Reply', priority: 'Medium', createdAt: '2026-08-05 15:22', owner: 'Arman Wijaya', description: 'Clarify which label fields should be uploaded before buyer review.' },
	{ id: 'SUPPORT-1032', subject: 'Commercial invoice template field mismatch', category: 'Bug', status: 'Resolved', priority: 'Low', createdAt: '2026-08-04 09:10', owner: 'Nadia Prameswari', description: 'Invoice template previously duplicated HS code in generated preview.' }
];

export const apiKeys: ApiKey[] = [
	{ id: 'KEY-LOG-001', name: 'Forwarder webhook key', prefix: 'mek_live_log_', status: 'Active', scopes: ['shipments:write', 'rates:read'], createdAt: '2026-08-01', lastUsed: '2026-08-06 10:30', owner: 'Operations' },
	{ id: 'KEY-FIN-002', name: 'Finance reporting key', prefix: 'mek_live_fin_', status: 'Expiring Soon', scopes: ['payments:read', 'reports:write'], createdAt: '2026-07-12', lastUsed: '2026-08-05 18:42', owner: 'Finance' },
	{ id: 'KEY-OLD-003', name: 'Legacy sandbox key', prefix: 'mek_test_old_', status: 'Revoked', scopes: ['projects:read'], createdAt: '2026-06-02', lastUsed: '2026-07-01 08:00', owner: 'Admin' }
];

export const businessProfiles: BusinessProfile[] = [
	{ id: 'BIZ-ACEH-COF', companyName: 'PT Kopi Gayo Nusantara', address: 'Takengon, Aceh, Indonesia', productionCapacity: '12,000 retail bags / month', yearEstablished: 2018, certifications: ['Halal', 'Origin declaration', 'Organic in progress'], status: 'Needs Review', owner: 'Rizal Fahmi', readiness: 82 },
	{ id: 'BIZ-MEDAN-SNK', companyName: 'Medan Crispy Foods', address: 'Medan, North Sumatra, Indonesia', productionCapacity: '75,000 pouches / month', yearEstablished: 2020, certifications: ['Halal', 'HACCP', 'Nutrition facts ready'], status: 'Complete', owner: 'Sinta Lestari', readiness: 94 }
];

export const userAccounts: UserAccount[] = [
	{ id: 'U-001', email: 'admin@mauekspor.example', fullName: 'MauEkspor Admin', role: 'Admin', status: 'Active', createdAt: '2026-07-01', lastLogin: '2026-08-06 10:58' },
	{ id: 'U-002', email: 'rizal@kopigayo.example', fullName: 'Rizal Fahmi', role: 'UMKM', status: 'Active', createdAt: '2026-07-12', lastLogin: '2026-08-06 09:20' },
	{ id: 'U-003', email: 'aya@hikari.example', fullName: 'Aya Nakamura', role: 'Buyer', status: 'Invited', createdAt: '2026-08-03', lastLogin: 'Invitation pending' },
	{ id: 'U-004', email: 'ops@ngl.example', fullName: 'NGL Operations', role: 'Forwarder', status: 'Active', createdAt: '2026-07-20', lastLogin: '2026-08-05 16:12' }
];

export const buyerRequests: BuyerRequest[] = [
	{ id: 'BRQ-JP-COF-001', buyerId: 'BUY-HIKARI-JP', productId: 'PRD-COF-001', subject: 'Trial shipment for Gayo Arabica coffee', status: 'Matched', destination: 'Japan', quantity: '2,000 bags', deadline: '2026-08-12', requirements: ['Japanese label', 'Lab report', 'FOB quote'] },
	{ id: 'BRQ-DE-FUR-014', buyerId: 'BUY-NORDHAUS-DE', productId: 'PRD-FUR-014', subject: 'Rattan chair set CIF Hamburg', status: 'Quoted', destination: 'Germany', quantity: '120 sets', deadline: '2026-08-16', requirements: ['SVLK evidence', 'Fumigation', 'CIF Hamburg'] },
	{ id: 'BRQ-SG-SNK-006', buyerId: 'BUY-MERLION-SG', productId: 'PRD-SNK-006', subject: 'Recurring cassava chips replenishment', status: 'New', destination: 'Singapore', quantity: '10,000 pouches/month', deadline: '2026-08-24', requirements: ['Retail carton', 'DAP option', 'Shelf-life evidence'] }
];

export const forwarders: Forwarder[] = [
	{ id: 'FWD-NGL', name: 'Nusantara Global Logistics', coverage: 'Japan and North Asia', status: 'Verified', mode: 'Ocean', onTimeRate: 92, quoteSpeed: '4 hours', lanes: ['Tanjung Priok - Yokohama', 'Surabaya - Osaka'], contact: 'ops@ngl.example' },
	{ id: 'FWD-AFN', name: 'Archipelago Freight Network', coverage: 'Europe FCL and LCL', status: 'In Review', mode: 'Ocean', onTimeRate: 81, quoteSpeed: '1 day', lanes: ['Tanjung Perak - Hamburg', 'Tanjung Priok - Rotterdam'], contact: 'rates@afn.example' },
	{ id: 'FWD-MPE', name: 'Merah Putih Express', coverage: 'Singapore and Malaysia', status: 'Verified', mode: 'Multimodal', onTimeRate: 95, quoteSpeed: '2 hours', lanes: ['Belawan - Singapore', 'Jakarta - Port Klang'], contact: 'hello@mpe.example' }
];

export const educationalModules: EducationalModule[] = [
	{ id: 'EDU-START', title: 'Export Readiness Foundations', level: 'Beginner', status: 'Published', lessons: 8, completion: 72, summary: 'Learn product readiness, buyer discovery, documentation, and first shipment basics.' },
	{ id: 'EDU-COMPLIANCE', title: 'Compliance and HS Code Evidence', level: 'Intermediate', status: 'Published', lessons: 6, completion: 44, summary: 'Build evidence-backed compliance workflows for target markets.' },
	{ id: 'EDU-COSTING', title: 'Incoterms and Landed Costing', level: 'Advanced', status: 'Needs Review', lessons: 7, completion: 20, summary: 'Model EXW, FOB, CIF, DAP, margin, freight, insurance, and FX risk.' }
];

export const educationalLessons: EducationalLesson[] = [
	{ id: 'LSN-START-01', moduleId: 'EDU-START', title: 'Why export readiness matters', duration: '4 min', kind: 'Video', completed: true,
		content: 'Export readiness is the foundation that every other workflow in MauEkspor depends on. Before you can classify HS codes, quote a buyer, or generate a commercial invoice, your product data needs to be complete, consistent, and verifiable. In this lesson we walk through what "ready" actually means: structured specs, accurate weights and dimensions, packaging details, and any certificates that apply to your product category.',
		keyPoints: ['Structured product data speeds up every downstream step', 'Incomplete specs are the top cause of quotation delays', 'Certificates should be attached before requesting market analysis'] },
	{ id: 'LSN-START-02', moduleId: 'EDU-START', title: 'Capturing structured product data', duration: '6 min', kind: 'Reading', completed: true,
		content: 'A structured product record separates description, net/gross weight, dimensions, material composition, and packaging into distinct fields instead of a single free-text description. This lesson shows the minimum fields MauEkspor expects when you create a new product: name, category, origin, HS candidate, MOQ, lead time, and price range.',
		keyPoints: ['Split description from technical specifications', 'Always record net and gross weight separately', 'MOQ and lead time drive buyer-facing catalog copy'] },
	{ id: 'LSN-START-03', moduleId: 'EDU-START', title: 'Finding your first buyer', duration: '5 min', kind: 'Video', completed: true,
		content: 'Buyer discovery in MauEkspor starts with the Buyers CRM and Buyer Requests inbox. This lesson covers how to qualify a lead, what information to request before quoting, and how to track a buyer through Lead, Qualified, Active, and Churned stages.',
		keyPoints: ['Qualify buyers before investing in a full quotation', 'Buyer Requests often arrive with incomplete requirements', 'Track buyer stage to prioritize your sales pipeline'] },
	{ id: 'LSN-START-04', moduleId: 'EDU-START', title: 'Drafting your first RFQ response', duration: '7 min', kind: 'Reading', completed: true,
		content: 'When a buyer sends a Request for Quotation, your response should reference Incoterm, lead time, MOQ, and a validity window. This lesson walks through the RFQ to Quotation conversion flow inside MauEkspor and how costing data feeds into your quoted price.',
		keyPoints: ['Always state Incoterm and validity date in a quotation', 'Costing scenarios should be built before quoting, not after', 'Quotations convert directly into Orders once accepted'] },
	{ id: 'LSN-START-05', moduleId: 'EDU-START', title: 'Building a compliance checklist', duration: '5 min', kind: 'Video', completed: true,
		content: 'Every target market has its own compliance requirements — labeling language, lab reports, certificates of origin, or fumigation certificates. This lesson shows how to turn a market analysis into an actionable compliance checklist with owners and due dates.',
		keyPoints: ['Convert market analysis recommendations into tasks', 'Assign an owner and due date to every compliance item', 'Blocked compliance items should trigger a task automatically'] },
	{ id: 'LSN-START-06', moduleId: 'EDU-START', title: 'Preparing shipment documents', duration: '6 min', kind: 'Reading', completed: true,
		content: 'Commercial invoices, packing lists, and certificates of origin must be cross-validated before a shipment is booked. This lesson covers the document validation checks MauEkspor runs and how to resolve common mismatches between invoice values and packing list quantities.',
		keyPoints: ['Invoice and packing list quantities must reconcile', 'HS code on the invoice should match the export analysis', 'Missing metadata is the most common document rejection reason'] },
	{ id: 'LSN-START-07', moduleId: 'EDU-START', title: 'Booking your first shipment', duration: '4 min', kind: 'Video', completed: false,
		content: 'Once documents are validated, you can request forwarder quotes and book a shipment. This lesson explains how lane coverage, on-time rate, and quote speed help you choose the right forwarder for a first-time shipment.',
		keyPoints: ['Compare forwarder on-time rate before booking', 'Lane coverage determines route and transit time', 'Booking milestones should be tracked until departure'] },
	{ id: 'LSN-START-08', moduleId: 'EDU-START', title: 'Knowledge check: readiness basics', duration: '3 min', kind: 'Quiz', completed: false,
		content: 'A short knowledge check covering product readiness, buyer qualification, and document validation. Review the previous lessons if you are unsure of an answer before continuing to the Compliance module.',
		keyPoints: ['Review structured data requirements', 'Review buyer qualification stages', 'Review document validation checks'] },

	{ id: 'LSN-CMP-01', moduleId: 'EDU-COMPLIANCE', title: 'Understanding HS classification', duration: '6 min', kind: 'Video', completed: true,
		content: 'The Harmonized System classifies goods using a 6-digit global code, extended locally by each customs authority. This lesson explains how MauEkspor suggests HS candidates and why human confirmation is required before it feeds into duty calculation.',
		keyPoints: ['HS codes are 6 digits globally, then extended locally', 'AI-suggested HS codes require human confirmation', 'Wrong HS classification is a common cause of customs delay'] },
	{ id: 'LSN-CMP-02', moduleId: 'EDU-COMPLIANCE', title: 'Collecting evidence for each requirement', duration: '7 min', kind: 'Reading', completed: true,
		content: 'Every compliance requirement should map to a specific piece of evidence — a lab report, a certificate, or a declaration. This lesson shows how to attach evidence to a requirement and how confidence scoring works when evidence is partial.',
		keyPoints: ['One requirement should map to one clear evidence artifact', 'Partial evidence lowers the confidence score', 'Evidence should include an issue and expiry date when applicable'] },
	{ id: 'LSN-CMP-03', moduleId: 'EDU-COMPLIANCE', title: 'Working with rules of origin', duration: '8 min', kind: 'Video', completed: false,
		content: 'Preferential tariffs under trade agreements like IJEPA or ASEAN FTAs only apply when rules-of-origin evidence is correctly documented. This lesson covers how origin declarations are structured and why they matter for duty-free access.',
		keyPoints: ['Preferential duty requires a valid origin certificate', 'Rules-of-origin evidence must match the trade agreement format', 'Origin claims without evidence risk retroactive duty assessment'] },
	{ id: 'LSN-CMP-04', moduleId: 'EDU-COMPLIANCE', title: 'Labeling and language requirements', duration: '5 min', kind: 'Reading', completed: false,
		content: 'Many destination markets require labeling in the local language with specific mandatory fields such as net content, ingredients, and importer information. This lesson reviews common labeling pitfalls for Japan, the EU, and Singapore.',
		keyPoints: ['Local-language labeling is often mandatory, not optional', 'Mandatory fields vary by destination market', 'Label review should happen before quotation approval'] },
	{ id: 'LSN-CMP-05', moduleId: 'EDU-COMPLIANCE', title: 'Supplier certificate scope matching', duration: '6 min', kind: 'Video', completed: false,
		content: 'A supplier certificate is only valid evidence if its scope explicitly covers the product being exported. This lesson explains how to check certificate scope pages against your product catalog before relying on it as compliance evidence.',
		keyPoints: ['Certificate scope must explicitly cover the exported product', 'Expired or out-of-scope certificates should be flagged', 'Compliance officers should review supplier evidence periodically'] },
	{ id: 'LSN-CMP-06', moduleId: 'EDU-COMPLIANCE', title: 'Knowledge check: compliance evidence', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'A short knowledge check covering HS classification, rules of origin, and certificate scope matching before moving on to the Costing module.',
		keyPoints: ['Review HS classification confidence rules', 'Review rules-of-origin documentation', 'Review certificate scope matching process'] },

	{ id: 'LSN-CST-01', moduleId: 'EDU-COSTING', title: 'Incoterms explained: EXW to DAP', duration: '8 min', kind: 'Video', completed: true,
		content: 'Incoterms define who is responsible for freight, insurance, and risk at each stage of a shipment. This lesson compares EXW, FOB, CIF, and DAP and how each shifts cost and risk between exporter and buyer.',
		keyPoints: ['EXW shifts the most cost and risk to the buyer', 'FOB and CIF are the most common terms for ocean freight', 'DAP requires the exporter to manage the full logistics chain'] },
	{ id: 'LSN-CST-02', moduleId: 'EDU-COSTING', title: 'Modeling landed cost', duration: '9 min', kind: 'Reading', completed: false,
		content: 'Landed cost combines product cost, origin handling, freight, insurance, duties, and destination charges into a single per-unit figure. This lesson walks through building a costing scenario in MauEkspor step by step.',
		keyPoints: ['Landed cost should be modeled per unit, not per shipment', 'Freight and duties are the two most volatile cost components', 'Costing scenarios should be revisited when freight rates expire'] },
	{ id: 'LSN-CST-03', moduleId: 'EDU-COSTING', title: 'Managing FX and margin risk', duration: '6 min', kind: 'Video', completed: false,
		content: 'Currency fluctuation between quotation and payment can erode margin on international sales. This lesson covers simple hedging approaches and how to build an FX buffer into your quoted price.',
		keyPoints: ['FX movement between quote and payment affects realized margin', 'A small FX buffer protects margin on long payment terms', 'Reconfirm pricing if FX moves significantly before shipment'] },
	{ id: 'LSN-CST-04', moduleId: 'EDU-COSTING', title: 'Freight and insurance basics', duration: '7 min', kind: 'Reading', completed: false,
		content: 'Ocean and air freight rates vary by lane, season, and container availability. This lesson explains how to compare forwarder rates and when cargo insurance is worth the added cost.',
		keyPoints: ['Freight rates should be re-quoted if validity has expired', 'Cargo insurance is recommended for high-value shipments', 'Consolidate shipments where possible to reduce per-unit freight cost'] },
	{ id: 'LSN-CST-05', moduleId: 'EDU-COSTING', title: 'Reviewing quotation margins', duration: '5 min', kind: 'Video', completed: false,
		content: 'Before sending a quotation, review the margin against your costing scenario and target minimum margin. This lesson shows how to spot a quotation that is priced too aggressively before it goes to the buyer.',
		keyPoints: ['Compare quoted price against landed cost, not product cost alone', 'Set a minimum acceptable margin threshold per product line', 'Re-review margin if buyer negotiates payment terms'] },
	{ id: 'LSN-CST-06', moduleId: 'EDU-COSTING', title: 'Case study: CIF Hamburg furniture', duration: '8 min', kind: 'Reading', completed: false,
		content: 'A worked example showing how a rattan furniture exporter built a CIF Hamburg costing scenario, including SVLK compliance cost, fumigation, and EU import handling charges.',
		keyPoints: ['Compliance cost should be included in landed cost, not treated as overhead', 'CIF quotes must include insurance value basis', 'Destination handling charges vary significantly by port'] },
	{ id: 'LSN-CST-07', moduleId: 'EDU-COSTING', title: 'Knowledge check: costing and incoterms', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'A short knowledge check covering Incoterms, landed cost modeling, and margin review before completing the Costing module.',
		keyPoints: ['Review Incoterm risk transfer points', 'Review landed cost components', 'Review minimum margin thresholds'] }
];

export const chatConversations: ChatConversation[] = [
	{ id: 'CHAT-001', title: 'Japan coffee compliance guidance', status: 'Active', updatedAt: '2026-08-06 11:20', messages: [{ role: 'User', text: 'What is blocking the Japan coffee shipment?' }, { role: 'AI', text: 'The Japanese label proof and lab report timing are the main blockers before quote approval.' }] },
	{ id: 'CHAT-002', title: 'EU rattan freight risk', status: 'Active', updatedAt: '2026-08-06 10:15', messages: [{ role: 'User', text: 'Summarize EU rattan risk.' }, { role: 'AI', text: 'SVLK scope and CIF Hamburg freight validity are the highest priority risks.' }] }
];

export const exportAnalyses: ExportAnalysis[] = [
	{
		id: 'ANL-COF-001',
		productId: 'PRD-COF-001',
		productName: 'Gayo Arabica Coffee Beans',
		destination: 'Japan',
		status: 'Ready',
		hsCode: '0901.21',
		confidence: 91,
		score: 84,
		marketDemand: 'High',
		duties: '0% (JP-EPA tariff line vulnerable to rules-of-origin checks)',
		restrictions: ['Label must use Japanese local language', 'Lab report for pesticide residues within 12 months', 'Origin declaration required for tariff preference'],
		recommendations: [
			{ type: 'Certificate', title: 'Certificate of Origin (Indonesia-Japan EPA)', status: 'Required', detail: 'Needed to claim 0% duty; must match format AANZ-JEPA.' },
			{ type: 'Labeling', title: 'Japanese food label (PL/NL prefix)', status: 'Required', detail: 'Include ingredients, net content, importer, and expiry.' },
			{ type: 'Document', title: 'Pesticide residue lab report', status: 'Required', detail: 'Within 12 months of shipment date.' }
		],
		summary: 'Japan is a high-demand, 0% duty opportunity for Gayo Arabica, but labeling evidence and the origin certificate scope must be completed before quotation approval.'
	},
	{
		id: 'ANL-FUR-014',
		productId: 'PRD-FUR-014',
		productName: 'Handwoven Rattan Chair Set',
		destination: 'Germany',
		status: 'Needs Review',
		hsCode: '9401.52',
		confidence: 74,
		score: 61,
		marketDemand: 'Medium',
		duties: '0% (EU GSP with SVLK compliance)',
		restrictions: ['EUTR/SVLK legality evidence required', 'Fumigation certificate for wooden parts', 'CE safety basics for furniture'],
		recommendations: [
			{ type: 'Certificate', title: 'SVLK legality evidence', status: 'Required', detail: 'Traceability chain from forestry to manufacturer.' },
			{ type: 'Document', title: 'Fumigation certificate', status: 'Required', detail: 'ISPM-15 for wooden components in main container.' },
			{ type: 'Labeling', title: 'CE + care labeling', status: 'Recommended', detail: 'Stability and care labeling recommended for EU retail.' }
		],
		summary: 'EU market access exists under GSP once SVLK and fumigation evidence are prepared; EU safety checks remain the main review item.'
	}
];

export const educationalArticles: EducationalArticle[] = [
	{ id: 'ART-READY', title: 'How to prepare export-ready product data', status: 'Published', level: 'Beginner', readMinutes: 6, tags: ['Product', 'Readiness'],
 summary: 'Capture the minimum data set for HS classification, packaging, and certificates.',
 body: 'Start by splitting description, net and gross weights, dimensions, material composition, and packaging into structured specs. Clean, structured product data is the input every downstream AI step depends on - from HS suggestions to catalog and quotation.' },
	{ id: 'ART-HS', title: 'Reading HS codes and tariff schedules', status: 'Published', level: 'Intermediate', readMinutes: 8, tags: ['HS Code', 'Tariffs'], summary: 'Understand classification logic and where rules-of-origin applies.', body: 'The HS system classifies goods at 6 digits globally. Tariff numbers vary by market, and preference agreements (EPA, GSP) only apply when rules-of-origin evidence is correct.' },
	{ id: 'ART-COF', title: 'Coffee to Japan: what you need', status: 'Draft', level: 'Advanced', readMinutes: 10, tags: ['Japan', 'Coffee', 'Labeling'], summary: 'Inline, evidence, and the JEPA origin certificate.', body: 'Japan accepts coffee at 0% under the JEPA when the origin certificate is filed correctly. Labeling must be Japanese and the lab report has validity constraints.' }
];

export const products: Product[] = [
	{
		id: 'PRD-COF-001',
		name: 'Gayo Arabica Coffee Beans',
		category: 'Food & Beverage',
		status: 'Enriched',
		hs: '0901.21',
		origin: 'Aceh, Indonesia',
		packaging: '250g valve bag, 24 bags per carton',
		netWeight: '250g',
		grossWeight: '280g',
		moq: '2,000 bags',
		leadTime: '21 days',
		certificates: ['Halal', 'Organic in progress', 'Lab report required'],
		readiness: 86
	},
	{
		id: 'PRD-FUR-014',
		name: 'Handwoven Rattan Chair Set',
		category: 'Furniture',
		status: 'Needs HS Review',
		hs: '9401.53',
		origin: 'Cirebon, Indonesia',
		packaging: 'KD export carton with corner protection',
		netWeight: '18kg set',
		grossWeight: '22kg set',
		moq: '120 sets',
		leadTime: '45 days',
		certificates: ['SVLK', 'Fumigation required'],
		readiness: 74
	},
	{
		id: 'PRD-SNK-006',
		name: 'Cassava Chips Sea Salt',
		category: 'Processed Food',
		status: 'Ready',
		hs: '2005.99',
		origin: 'North Sumatra, Indonesia',
		packaging: '80g pouch, 48 pouches per carton',
		netWeight: '80g',
		grossWeight: '95g',
		moq: '5,000 pouches',
		leadTime: '14 days',
		certificates: ['Halal', 'HACCP', 'Nutrition facts ready'],
		readiness: 91
	}
];

export const activities: ActivityItem[] = [
	{
		title: 'Certificate of Origin needs review',
		description: 'Japan Coffee Trial Shipment has one document mismatch.',
		time: '12 min ago',
		tone: 'orange'
	},
	{
		title: 'Packing list validation passed',
		description: 'Commercial invoice quantities match carton data.',
		time: '38 min ago',
		tone: 'green'
	},
	{
		title: 'Forwarder quote expiring soon',
		description: 'CIF Hamburg rate validity ends in 2 days.',
		time: '1 hour ago',
		tone: 'red'
	},
	{
		title: 'AI market note generated',
		description: 'Singapore snack project received a new route recommendation.',
		time: '3 hours ago',
		tone: 'blue'
	}
];
