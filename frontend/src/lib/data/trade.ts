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
	hsConfidence?: number;
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
	is_village_priority?: boolean;
	commodity_group?: string;
	village_id?: string;
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
	sections: (string | { title: string; value: string; detail: string })[];
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
	status: 'Connected' | 'Available' | 'Needs Auth' | 'Error' | 'Disconnected';
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
	role: 'Admin' | 'Exporter' | 'Buyer' | 'Forwarder' | 'CustomsBroker' | 'Finance';
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
	selectedCatalogId?: string;
	selectedCatalog?: string;
	selectedUmkm?: string;
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

export type QuizQuestion = {
	id: string;
	question: string;
	options: string[];
	correctIndex: number;
	explanation: string;
};

export type EducationalModule = {
	id: string;
	title: string;
	level: 'Beginner' | 'Intermediate' | 'Advanced' | string;
	status: 'Published' | 'Draft' | 'Needs Review' | string;
	lessons: number;
	completion: number;
	summary: string;
	// Field backend
	description?: string;
	orderIndex?: number;
	articleCount?: number;
	articles?: EducationalArticle[];
	lessonsList?: EducationalLesson[];
	lessonCount?: number;
	quizCount?: number;
	createdAt?: string;
	updatedAt?: string;
};

export type EducationalLesson = {
	id: string;
	moduleId: string;
	title: string;
	duration: string;
	kind: 'Video' | 'Reading' | 'Quiz' | string;
	completed: boolean;
	content: string;
	videoUrl?: string;
	keyPoints: string[];
	quizQuestions?: QuizQuestion[];
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
	recommendations:
		| string
		| Array<{
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
	fileId?: string;
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
	{ label: 'Village Potential', href: '/villages' },
	{ label: 'Export Analysis', href: '/export-analysis' },
	{ label: 'Compliance', href: '/compliance' },
	{ label: 'Markets', href: '/markets' },
	{ label: 'Catalogs', href: '/catalogs' },
	{ label: 'Buyers', href: '/buyers' },
	{ label: 'Buyer Portal', href: '/buyers/portal' },
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
	{ label: 'Admin Panel', href: '/admin' },
	{ label: 'Countries & Regulations', href: '/admin/countries' },
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
			{ label: 'Village Potential', href: '/villages' },
			{ label: 'Export Analysis', href: '/export-analysis' },
			{ label: 'Markets', href: '/markets' },
			{ label: 'Countries', href: '/countries' },
			{ label: 'Catalogs', href: '/catalogs' },
			{ label: 'Public Catalog', href: '/catalogs/public' }
		]
	},
	{
		label: 'Commercial',
		items: [
			{ label: 'Buyers', href: '/buyers' },
			{ label: 'Buyer Portal', href: '/buyers/portal' },
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
			{ label: 'Admin Panel', href: '/admin' },
			{ label: 'Users', href: '/users' },
			{ label: 'Billing', href: '/billing' },
			{ label: 'Support', href: '/support' },
			{ label: 'API Keys', href: '/api-keys' },
			{ label: 'Countries & Regulations', href: '/admin/countries' },
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
		source: 'Japan Customs tariff schedule / BTKI 2022',
		sourceDate: '2026-09-29',
		requiredEvidence: 'Classification rationale and product composition statement',
		currentEvidence: 'AI candidate code available; reviewer note missing',
		confidence: 84
	},
	{
		id: 'CMP-JP-002',
		projectId: 'EXP-2408-017',
		productId: 'PRD-COF-001',
		title: 'Japanese nutrition and allergen label proof (28 mandatory allergens)',
		category: 'Labeling',
		severity: 'Critical',
		status: 'Blocked',
		owner: 'Exporter',
		due: 'Tomorrow',
		source: 'Consumer Affairs Agency Japan food labeling guidance',
		sourceDate: '2026-09-29',
		requiredEvidence: 'Japanese label artwork, nutrition facts, 28 allergens declaration, importer review',
		currentEvidence: 'English label only',
		confidence: 85
	},
	{
		id: 'CMP-EU-004',
		projectId: 'EXP-2408-021',
		productId: 'PRD-FUR-014',
		title: 'EUDR Geolocation Coordinates & Due Diligence Statement (DDS)',
		category: 'Certificate',
		severity: 'Critical',
		status: 'Evidence Uploaded',
		owner: 'Exporter',
		due: '2 days',
		source: 'Regulation (EU) 2023/1115 (EUDR)',
		sourceDate: '2026-09-29',
		requiredEvidence: 'Polygon GPS coordinates of timber source + EU Deforestation Information System DDS reference',
		currentEvidence: 'SVLK certificate uploaded; GPS polygon mapping in progress',
		confidence: 88
	},
	{
		id: 'CMP-US-005',
		projectId: 'EXP-2408-017',
		productId: 'PRD-COF-001',
		title: 'US-Indonesia ART Schedule 2B Tariff Exemption Proof',
		category: 'Document',
		severity: 'Critical',
		status: 'In Review',
		owner: 'Exporter',
		due: '3 days',
		source: 'US-Indonesia Agreement on Reciprocal Trade (ART)',
		sourceDate: '2026-09-29',
		requiredEvidence: 'Certificate of origin verifying Indonesian production under Schedule 2B',
		currentEvidence: 'Exporter origin statement drafted; CBP broker review pending',
		confidence: 86
	},
	{
		id: 'CMP-ID-006',
		projectId: 'EXP-2408-017',
		productId: 'PRD-COF-001',
		title: 'Kepatuhan Rekening Khusus DHE SDA Himbara (PP 21/2026)',
		category: 'Document',
		severity: 'Major',
		status: 'Verified',
		owner: 'Finance',
		due: 'Done',
		source: 'PP No. 21 Tahun 2026',
		sourceDate: '2026-09-29',
		requiredEvidence: 'Rekening khusus DHE SDA di bank devisa Himbara terhubung CEISA/INSW',
		currentEvidence: 'Rekening Khusus DHE Bank Mandiri terdaftar aktif',
		confidence: 100
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
	{ id: 'AUD-1001', time: '2026-08-06 10:42', actor: 'Nuxim AI', action: 'Generated market insight', module: 'Markets', entity: 'MKT-SG-SNK', severity: 'Info', detail: 'Singapore snack route scored 91 with low compliance complexity.' },
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
	{ id: 'INT-AI', name: 'Nuxim AI', category: 'AI', status: 'Connected', description: 'Generate market insights, catalog copy, task summaries, and report narratives.', lastSync: '2026-08-06 10:42', scopes: ['Market Insight', 'Catalog Copy', 'Reports'] }
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
	{ id: 'KB-REGULASI-2026', title: 'Panduan Regulasi Ekspor-Impor Global 2026 & HS 2028', category: 'Compliance', status: 'Published', readTime: '8 min', updatedAt: '2026-09-29', summary: 'Acuan komprehensif rezim tarif AS (Section 301/232 & ART), regulasi EUDR/CBAM Uni Eropa, deregulasi Permendag 16/2025, dan DHE SDA PP 21/2026 per 29 September 2026.', steps: ['Cek pos tarif BTKI 2022 & persiapan HS 2028', 'Periksa pembebasan tarif ART Schedule 2B ke AS', 'Lengkapi geolokasi & DDS untuk EUDR', 'Buka rekening DHE SDA Himbara untuk retensi 100%'] },
	{ id: 'KB-EUDR-DDS', title: 'Kepatuhan EUDR: Geolokasi Lahan & Due Diligence Statement', category: 'Compliance', status: 'Published', readTime: '6 min', updatedAt: '2026-09-29', summary: 'Panduan pemetaan koordinat kebun kopi, kakao, karet, dan kayu untuk menghindari penolakan masuk Uni Eropa per 30 Desember 2026.', steps: ['Petakan poligon batas lahan budidaya', 'Verifikasi bebas deforestasi setelah 31 Des 2020', 'Terbitkan Due Diligence Statement via EU Information System', 'Kirimkan referensi DDS ke importir'] },
	{ id: 'KB-DHE-SDA', title: 'Kewajiban DHE SDA PP 21/2026: Retensi 100% 12 Bulan di Himbara', category: 'Finance', status: 'Published', readTime: '5 min', updatedAt: '2026-09-29', summary: 'Ketentuan penempatan devisa hasil ekspor SDA bagi eksportir non-migas dan migas dengan insentif PPh deposito hingga 0%.', steps: ['Identifikasi nilai ekspor >= USD 250,000', 'Buka rekening khusus di bank Himbara', 'Tempatkan 100% devisa non-migas selama 12 bulan', 'Hindari sanksi blokir ekspor CEISA/INSW'] },
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
	{ id: 'U-002', email: 'rizal@kopigayo.example', fullName: 'Rizal Fahmi', role: 'Exporter', status: 'Active', createdAt: '2026-07-12', lastLogin: '2026-08-06 09:20' },
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
	{ id: 'EDU-START', title: 'Dasar Kesiapan Ekspor & Verifikasi Spesifikasi Produk', level: 'Beginner', status: 'Published', lessons: 4, completion: 75, summary: 'Fondasi kesiapan ekspor: struktur data teknis produk, kualifikasi buyer global, rekonsiliasi dokumen kepabeanan, dan uji kuis kesiapan.' },
	{ id: 'EDU-COMPLIANCE', title: 'Regulasi Global 2026: EUDR, CBAM, PPWR & Amandemen HS 2028', level: 'Intermediate', status: 'Published', lessons: 4, completion: 50, summary: 'Kuasai regulasi bebas deforestasi EUDR (cut-off 2020), deklarasi emisi CBAM Uni Eropa, serta peta transisi amandemen WCO HS 2028.' },
	{ id: 'EDU-COSTING', title: 'Incoterms® 2020 & Landed Costing Ekspor Realistis', level: 'Advanced', status: 'Published', lessons: 4, completion: 30, summary: 'Pemodelan biaya EXW, FOB, CIF, DAP, margin bersih per unit, mitigasi fluktuasi kurs valas (FX buffer), dan asuransi kargo laut.' },
	{ id: 'EDU-TARIFFS-2026', title: 'Rezim Tarif AS, Bilateral ART & Devisa DHE SDA (PP 21/2026)', level: 'Advanced', status: 'Published', lessons: 4, completion: 25, summary: 'Strategi pembebasan tarif Section 301/232 AS via ART Schedule 2B dan kepatuhan retensi 100% 12 bulan DHE SDA di bank devisa Himbara.' },
	{ id: 'EDU-DES-PANEN-01', title: 'Ekspor Hasil Panen Segar & Karantina Pertanian (PP 28/2024)', level: 'Beginner', status: 'Published', lessons: 4, completion: 0, summary: 'Prosedur penerbitan Sertifikat Kesehatan Tumbuhan (Phytosanitary Certificate) Barantin, uji bebas Organisme Pengganggu Tumbuhan Karantina (OPTK).' },
	{ id: 'EDU-DES-HALAL-02', title: 'Panduan Sertifikasi Halal BPJPH & Akses Pasar Timur Tengah', level: 'Beginner', status: 'Published', lessons: 4, completion: 0, summary: 'Langkah pendaftaran SIHALAL, Sistem Jaminan Produk Halal (SJPH), pengakuan standar GSO/SASO, dan penandaan label halal ekspor.' },
	{ id: 'EDU-DES-NIB-04', title: 'Legalitas BUMDes, NIB OSS-RBA, & Fasilitas Kepabeanan UMK', level: 'Beginner', status: 'Published', lessons: 5, completion: 0, summary: 'Transformasi kelembagaan BUMDes berbadan hukum, pemetaan KBLI 5 digit di OSS-RBA, akses pembiayaan LPEI, dan fasilitas Permendag 16/2025.' },
	{ id: 'EDU-DES-DOC-05', title: 'Daftar Dokumen Wajib Ekspor ke Singapura dan Jepang (Khusus Pertanian)', level: 'Intermediate', status: 'Published', lessons: 4, completion: 0, summary: 'Standar pemenuhan dokumen pangan segar SFA Singapura & MAFF Jepang: Phytosanitary Certificate, Health Certificate, Certificate of Analysis (CoA) residu pestisida, dan e-Form D/IJEPA.' },
	{ id: 'EDU-DES-KARANTINA-06', title: 'PP 28/2024: Karantina Pertanian untuk Petani & Pelaku Usaha Desa', level: 'Beginner', status: 'Published', lessons: 4, completion: 0, summary: 'Implementasi Peraturan Pemerintah No. 28 Tahun 2024: integrasi layanan satu pintu Badan Karantina Indonesia (Barantin), pemeriksaan pre-border di kebun sentra produksi desa, perlakuan fumigasi, dan sertifikasi digital e-Phyto.' },
	{ id: 'EDU-DES-CITES-07', title: 'CITES & Dokumen Asal Bahan Baku untuk Kriya Berbahan Alam', level: 'Intermediate', status: 'Published', lessons: 4, completion: 0, summary: 'Panduan legalitas ekspor kerajinan berbahan flora/fauna liar: pengurusan izin SATS-LN CITES (Appendix II & III), verifikasi Sistem Verifikasi Kelestarian Kayu (SVLK), dan Deklarasi Kesesuaian Pemasok (DKP).' }
];

export const educationalLessons: EducationalLesson[] = [
	// EDU-START
	{ id: 'LSN-START-01', moduleId: 'EDU-START', title: 'Standar Data Produk Ekspor & Spesifikasi Teknis', duration: '5 min', kind: 'Reading', completed: true,
		content: 'Kesiapan ekspor menuntut pemisahan deskripsi bebas menjadi data terstruktur: nama latin/botanis, bobot bersih (net weight), bobot kotor (gross weight), dimensi kemasan (PxLxT), standar mutu (grade, moisture content, defect rate), dan dokumen sertifikasi. Data yang rapi memastikan penentuan HS Code otomatis akurat dan mempercepat respons terhadap RFQ pembeli internasional.',
		keyPoints: ['Pisahkan spesifikasi teknis dari deskripsi pemasaran', 'Catat berat bersih dan berat kotor secara terpisah per kemasan', 'Sertakan toleransi mutu (kadar air, ukuran biji/screen size, sertifikat)'] },
	{ id: 'LSN-START-02', moduleId: 'EDU-START', title: 'Kualifikasi Buyer Internasional & Validasi RFQ', duration: '6 min', kind: 'Video', completed: true,
		videoUrl: 'https://www.youtube.com/watch?v=C7VLuiVPIQM',
		content: 'Sebelum memberikan penawaran harga resmi (Quotation), eksportir wajib memvalidasi profil calon pembeli: keabsahan perusahaan (nomor registrasi bisnis, situs resmi, referensi perdagangan), riwayat pembayaran, estimasi volume tahunan, serta Incoterm yang diminta. Hindari memberikan harga DDP ke negara yang mengenakan bea masuk dinamis tanpa klausul penyesuaian tarif.',
		keyPoints: ['Validasi legalitas dan rekam jejak buyer sebelum menyusun quotation', 'Pastikan kuantitas minimum order (MOQ) dan lead time produksi realistis', 'Tentukan masa berlaku penawaran harga (quotation validity) maksimal 14–30 hari'] },
	{ id: 'LSN-START-03', moduleId: 'EDU-START', title: 'Validasi Dokumen Ekspor & Rekonsiliasi Faktur', duration: '6 min', kind: 'Reading', completed: true,
		content: 'Tiga pilar dokumen pengapalan ekspor: Commercial Invoice, Packing List, dan Bill of Lading (B/L) atau Air Waybill (AWB). Seluruh angka kuantitas, nilai satuan, deskripsi barang, dan nomor pos tarif HS wajib 100% konsisten. Inkonsistensi berat antara packing list dan manifest pelabuhan dapat memicu pemeriksaan fisik jalur merah oleh Bea Cukai.',
		keyPoints: ['Jumlah koli dan berat kotor pada Packing List wajib persis sama dengan B/L', 'Cantumkan nomor HS Code 8 digit (AHTN/BTKI) pada Commercial Invoice', 'Simpan arsip pemberitahuan ekspor barang (PEB) minimal 10 tahun untuk audit kepabeanan'] },
	{ id: 'LSN-START-04', moduleId: 'EDU-START', title: 'Kuis Evaluasi: Dasar Kesiapan Ekspor', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pemahaman Anda mengenai standardisasi data produk ekspor, kualifikasi calon buyer, dan rekonsiliasi dokumen kepabeanan.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Skor kelulusan minimal 70% untuk sertifikasi modul', 'Penjelasan kunci jawaban disertakan langsung setelah pengiriman kuis'],
		quizQuestions: [
			{ id: 'QZ-START-1', question: 'Mengapa berat bersih (net weight) dan berat kotor (gross weight) wajib dicantumkan terpisah pada dokumen ekspor?', options: ['Hanya untuk memenuhi estetika faktur komersial', 'Untuk perhitungan bea masuk dan kalkulasi payload kontainer/freight muatan kapal', 'Agar buyer bisa membedakan warna kemasan produk', 'Tidak wajib jika pengiriman menggunakan pesawat udara'], correctIndex: 1, explanation: 'Customs dan shipping line memerlukan gross weight untuk keselamatan pemuatan kontainer (VGM/SOLAS), sedangkan net weight digunakan untuk dasar perhitungan nilai pabean dan sertifikasi mutu.' },
			{ id: 'QZ-START-2', question: 'Berapa lama masa berlaku wajar untuk surat penawaran harga ekspor (Quotation)?', options: ['Tanpa batas waktu (berlaku selamanya)', 'Maksimal 12 bulan tanpa penyesuaian', 'Umumnya 14 hingga 30 hari karena risiko fluktuasi freight dan kurs valas', 'Hanya 24 jam di semua industri'], correctIndex: 2, explanation: 'Freight pelayaran laut dan nilai tukar valas berfluktuasi secara berkala, sehingga masa berlaku penawaran 14–30 hari melindungi eksportir dari kerugian margin.' },
			{ id: 'QZ-START-3', question: 'Apa dampak utama jika terjadi ketidakcocokan jumlah koli antara Commercial Invoice dan Packing List?', options: ['Barang langsung dilelang oleh otoritas pelabuhan', 'Penetapan jalur merah kepabeanan, denda administrasi, dan penahanan kontainer di pelabuhan tujuan', 'Pembeli mendapatkan diskon 50%', 'Tidak ada konsekuensi apapun'], correctIndex: 1, explanation: 'Inkonsistensi data dokumen pengapalan merupakan pemicu utama pemeriksaan fisik (jalur merah) oleh otoritas pabean dan potensi denda demurrage akibat penahanan kontainer.' }
		] },

	// EDU-COMPLIANCE
	{ id: 'LSN-CMP-01', moduleId: 'EDU-COMPLIANCE', title: 'Kepatuhan EUDR: Geolokasi Titik/Poligon Lahan Kebun & Due Diligence', duration: '7 min', kind: 'Reading', completed: true,
		content: 'Regulasi Bebas Deforestasi Uni Eropa (EUDR — Regulation EU 2023/1115) mewajibkan komoditas kopi, kakao, kelapa sawit, karet, kayu, dan kedelai membuktikan bebas deforestasi setelah cut-off date 31 Desember 2020. Eksportir wajib mengumpulkan koordinat GPS (titik untuk kebun <4 hektare, poligon untuk kebun >=4 hektare) dan menerbitkan Due Diligence Statement (DDS) di portal TRACES Komisi Eropa sebelum kapal sandar di pelabuhan UE.',
		keyPoints: ['Cut-off date bebas deforestasi adalah 31 Desember 2020', 'Kebun >= 4 hektare wajib poligon koordinat lengkap, bukan satu titik', 'Due Diligence Statement (DDS) wajib diserahkan sebelum impor disetujui'] },
	{ id: 'LSN-CMP-02', moduleId: 'EDU-COMPLIANCE', title: 'Transisi Fase Definitif CBAM 2026 & Sertifikasi Emisi', duration: '8 min', kind: 'Reading', completed: true,
		content: 'Carbon Border Adjustment Mechanism (CBAM) Uni Eropa memasuki fase definitif pada 1 Januari 2026. Produk besi, baja, aluminium, semen, dan pupuk tidak lagi cukup hanya melaporkan emisi triwulanan. Importir wajib membeli sertifikat CBAM berdasarkan emisi tertanam aktual (embedded emissions) yang diverifikasi oleh verifikator terakreditasi ISO 14065.',
		keyPoints: ['Fase definitif aktif 1 Januari 2026: importir wajib menyerahkan sertifikat CBAM', 'Eksportir wajib menghitung emisi lingkup 1 (langsung) dan lingkup 2 (listrik pabrik)', 'Data emisi yang tidak lengkap akan dikenai nilai default emisi tertinggi oleh Komisi Eropa'] },
	{ id: 'LSN-CMP-03', moduleId: 'EDU-COMPLIANCE', title: 'Persiapan Nomenklatur WCO HS 2028 (Edisi ke-8)', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=-I2EJ5MUVkY',
		content: 'World Customs Organization (WCO) telah mengesahkan 299 set amandemen HS 2028 yang berlaku per 1 Januari 2028. Perubahan vital meliputi: pemindahan vaksin ke pos 30.07 & 30.08, pos baru 21.07 untuk suplemen makanan dan nutraseutikal, serta restrukturisasi pos 39.15 untuk limbah dan barang plastik sekali pakai (single-use plastics). Eksportir disarankan mengaudit master data HS pada tahun 2027.',
		keyPoints: ['HS 2028 memuat 1.229 pos dan 5.852 subpos internasional', 'Suplemen makanan dipisahkan tegas ke pos 21.07 untuk mengakhiri sengketa klasifikasi', 'Plastik sekali pakai mendapatkan Catatan Bab 39 baru dan subpos khusus'] },
	{ id: 'LSN-CMP-04', moduleId: 'EDU-COMPLIANCE', title: 'Kuis Evaluasi: Kepatuhan Regulasi Ekspor 2026', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pengetahuan Anda mengenai kepatuhan regulasi lingkungan global, EUDR, CBAM fase definitif, dan transisi klasifikasi HS 2028.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Mencakup aturan cut-off date EUDR, verifikasi CBAM, dan pos suplemen HS 2028', 'Pembahasan komprehensif diberikan setelah kuis selesai'],
		quizQuestions: [
			{ id: 'QZ-CMP-1', question: 'Berapakah tanggal cut-off deforestasi yang ditetapkan oleh regulasi EUDR (Regulation EU 2023/1115)?', options: ['31 Desember 2015', '31 Desember 2020', '1 Januari 2024', '30 Desember 2026'], correctIndex: 1, explanation: 'Berdasarkan Pasal 2 regulasi EUDR, lahan budidaya komoditas tidak boleh mengalami deforestasi atau degradasi hutan setelah tanggal 31 Desember 2020.' },
			{ id: 'QZ-CMP-2', question: 'Apa kewajiban baru importir Uni Eropa saat CBAM memasuki fase definitif sejak 1 Januari 2026?', options: ['Hanya mengisi formulir deklarasi sederhana tanpa perhitungan emisi', 'Wajib membeli dan menyerahkan sertifikat CBAM berdasarkan emisi aktual yang terverifikasi', 'Mendapatkan pembebasan pajak penuh untuk komoditas logam', 'Menutup pabrik lokal di seluruh kawasan Eropa'], correctIndex: 1, explanation: 'Mulai fase definitif 2026, importir UE wajib membeli sertifikat CBAM seharga kuota ETS dan menyerahkannya setiap tahun berdasarkan emisi karbon tertanam pada produk impor.' },
			{ id: 'QZ-CMP-3', question: 'Pada edisi Harmonized System 2028 (HS 2028), suplemen makanan dialokasikan ke pos baru nomor berapa?', options: ['Pos 09.01', 'Pos 21.07', 'Pos 30.02', 'Pos 85.04'], correctIndex: 1, explanation: 'WCO menetapkan pos baru 21.07 pada HS 2028 beserta Catatan Bab baru untuk menyelesaikan sengketa klasifikasi suplemen pangan antara bab makanan olahan (21) dan farmasi (30).' }
		] },

	// EDU-COSTING
	{ id: 'LSN-CST-01', moduleId: 'EDU-COSTING', title: 'Perbedaan Risiko & Tanggung Jawab: EXW, FOB, CIF, dan DAP', duration: '8 min', kind: 'Reading', completed: true,
		content: 'Incoterms® 2020 ICC mengatur titik peralihan risiko (risk transfer) dan pembagian ongkos logistik antara penjual dan pembeli. Pada EXW, seluruh risiko dan biaya berada di tempat penjual. Pada FOB, risiko beralih saat barang melintasi geladak kapal di pelabuhan muat. Pada CIF, penjual membayar ongkos angkut dan asuransi laut minimal Klausul C hingga pelabuhan tujuan, namun risiko beralih sejak barang dimuat di kapal asal. Untuk kontainer, ICC menganjurkan FCA/CPT/CIP.',
		keyPoints: ['FOB dan CIF hanya berlaku untuk moda transportasi laut dan perairan pedalaman', 'Untuk muatan peti kemas (kontainer), ICC merekomendasikan penggunaan FCA/CPT/CIP', 'Nilai pabean impor Indonesia dihitung berbasis CIF, sedangkan AS berbasis nilai transaksi FOB-like'] },
	{ id: 'LSN-CST-02', moduleId: 'EDU-COSTING', title: 'Kalkulasi Landed Cost per Unit & Buffer Risiko Fluktuasi Kurs', duration: '9 min', kind: 'Reading', completed: false,
		content: 'Landed Cost adalah akumulasi seluruh pengeluaran riil hingga barang tiba di gudang tujuan: HPP produk, handling asal, biaya karantina/sertifikasi, ocean freight, asuransi, bea masuk negara tujuan, handling pelabuhan bongkar (THC/demurrage reserve), dan margin laba bersih. Eksportir wajib memasukkan buffer fluktuasi nilai tukar valas (mis. 2–3% FX buffer) untuk melindungi margin kontrak pembayaran berjangka 60–90 hari.',
		keyPoints: ['Hitung biaya kepatuhan dan sertifikasi ke dalam landed cost per unit', 'Sertakan bantalan deviasi kurs (FX buffer) pada skema pembayaran tempo', 'Simulasikan skenario kontainer FCL (20ft / 40ft) vs konsolidasi LCL'] },
	{ id: 'LSN-CST-03', moduleId: 'EDU-COSTING', title: 'Memilih Forwarder, Perhitungan Muatan Kontainer & Asuransi Kargo', duration: '7 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=7g7IC4IzjDM',
		content: 'Evaluasi forwarder tidak boleh hanya berpatokan pada harga termurah. Parameter penting: ketepatan jadwal sandar (on-time reliability), alokasi ruang kapal (space guarantee) saat peak season, kejelasan biaya lokal (local charges origin & destination), dan responsivitas saat timbul kendala transit. Asuransi kargo Institute Cargo Clauses (ICC A) wajib dipilih untuk barang berharga tinggi atau mudah rusak.',
		keyPoints: ['Bandingkan on-time performance dan lane coverage sebelum booking', 'Minta konfirmasi total breakdown local charges di pelabuhan bongkar tujuan', 'Pilih asuransi ICC A (All Risks) untuk barang bernilai tinggi'] },
	{ id: 'LSN-CST-04', moduleId: 'EDU-COSTING', title: 'Kuis Evaluasi: Incoterms & Strategi Harga Ekspor', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pemahaman Anda mengenai ketentuan Incoterms® 2020, pembagian biaya dan risiko, serta kalkulasi harga landed cost ekspor.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Evaluasi peralihan risiko FOB/CIF dan rekomendasi peti kemas', 'Skor dan evaluasi instan setelah pengiriman'],
		quizQuestions: [
			{ id: 'QZ-CST-1', question: 'Pada kontrak pengapalan dengan syarat CIF (Cost, Insurance & Freight), kapan titik peralihan risiko terjadi dari penjual ke pembeli?', options: ['Saat barang tiba di gudang pembeli di negara tujuan', 'Saat barang sudah dimuat di atas kapal di pelabuhan muat asal', 'Saat pembeli melunasi pembayaran L/C di bank', 'Saat kapal membongkar muatan di pelabuhan tujuan'], correctIndex: 1, explanation: 'Meskipun penjual menanggung biaya tambang laut dan polis asuransi sampai pelabuhan tujuan, risiko kerusakan/kehilangan barang beralih ke pembeli segera setelah barang dimuat di atas kapal di pelabuhan asal.' },
			{ id: 'QZ-CST-2', question: 'Manakah Incoterm yang paling direkomendasikan oleh ICC untuk pengiriman barang dalam peti kemas (kontainer)?', options: ['EXW (Ex Works)', 'FOB (Free On Board)', 'FCA / CPT / CIP', 'DDP (Delivered Duty Paid)'], correctIndex: 2, explanation: 'ICC secara eksplisit merekomendasikan FCA/CPT/CIP untuk kontainer karena penyerahan peti kemas dilakukan di terminal darat (CY/CFS) sebelum barang dinaikkan ke kapal.' },
			{ id: 'QZ-CST-3', question: 'Mengapa eksportir perlu memasukkan "FX buffer" (bantalan kurs) ke dalam pemodelan harga ekspor?', options: ['Untuk menghindari pembayaran pajak penghasilan', 'Melindungi margin laba bersih dari pelemahan kurs valas selama masa kredit pembayaran', 'Sebagai komisi wajib bagi forwarder pelayaran', 'Untuk membayar denda kelebihan muatan kontainer'], correctIndex: 1, explanation: 'Pada transaksi dengan termin pembayaran tempo (Net 30/60/90), fluktuasi nilai tukar valas dapat menggerus marjin laba bila tidak diantisipasi dengan bantalan kurs wajar.' }
		] },

	// EDU-TARIFFS-2026
	{ id: 'LSN-TRF-01', moduleId: 'EDU-TARIFFS-2026', title: 'Mitigasi Tarif Section 301/232 AS via Perjanjian Bilateral ART Schedule 2B', duration: '8 min', kind: 'Reading', completed: true,
		content: 'Pemerintah Amerika Serikat memberlakukan rezim tarif dinamis sepanjang 2025–2026: tarif Section 301, Section 232 (baja 25%, aluminium 10%), serta kenaikan tarif barang strategis. Indonesia dan AS menyepakati Agreement on Reciprocal Trade (ART) pada 19 Februari 2026, di mana komoditas kopi, kakao, dan rempah Indonesia yang memenuhi kriteria Schedule 2B dibebaskan dari tarif tambahan 10%. Eksportir wajib mencantumkan deklarasi ART pada dokumen pabean AS CBP 7501.',
		keyPoints: ['Periksa apakah produk Anda tercantum dalam Schedule 2B Agreement on Reciprocal Trade', 'Lampirkan bukti sertifikasi asal ART Schedule 2B untuk pembuktian pembebasan tarif 10%', 'Pantau de minimis threshold AS ($800) yang mengalami pengetatan pengawasan pada produk tekstil/garment'] },
	{ id: 'LSN-TRF-02', moduleId: 'EDU-TARIFFS-2026', title: 'Kewajiban Devisa Hasil Ekspor (DHE SDA) PP 21/2026: Retensi 100% 12 Bulan', duration: '7 min', kind: 'Reading', completed: false,
		content: 'Pemerintah RI menerbitkan PP No. 21 Tahun 2026 (berlaku mulai 1 Juni 2026) sebagai pengetatan aturan devisa hasil ekspor sumber daya alam. Ketentuan kunci: setiap ekspor sektor SDA (pertambangan, perkebunan, kehutanan, perikanan) dengan nilai FOB pada PEB minimal USD 250.000 wajib memasukkan 100% devisanya ke dalam Rekening Khusus DHE SDA di bank devisa dalam negeri (Himbara) dan dipertahankan minimal selama 12 bulan (untuk non-migas). Sanksi pelanggaran adalah penolakan layanan ekspor dan pemblokiran sistem CEISA/INSW Bea Cukai.',
		keyPoints: ['Threshold ekspor SDA: nilai FOB pada dokumen PEB minimal USD 250.000', 'Retensi 100% selama minimal 12 bulan di bank devisa domestik (Himbara)', 'Pemerintah memberikan insentif PPh final bunga deposito DHE hingga 0%'] },
	{ id: 'LSN-TRF-03', moduleId: 'EDU-TARIFFS-2026', title: 'Tata Cara Pembukaan Rekening Khusus DHE & Insentif Pajak Bunga Deposito', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=S0T09u1T8kY',
		content: 'Langkah kepatuhan DHE SDA: 1) Buka Rekening Khusus (Reksus) DHE SDA di bank Himbara (Mandiri, BRI, BNI, BTN) sebelum pengapalan; 2) Pastikan buyer mentransfer dana devisa ke Reksus tersebut; 3) Manfaatkan instrumen penempatan term deposit valas Bank Indonesia dengan tarif PPh final bunga deposito 0% untuk tenor di atas 6 bulan; 4) Sistem CEISA dan Bank Indonesia melakukan rekonsiliasi data PEB secara otomatis.',
		keyPoints: ['Buka rekening khusus berlabel DHE SDA sebelum mengajukan PEB', 'Gunakan instrumen Term Deposit Valas BI untuk insentif pembebasan PPh bunga', 'Data devisa masuk direkonsiliasi otomatis oleh Bank Indonesia dan DJBC'] },
	{ id: 'LSN-TRF-04', moduleId: 'EDU-TARIFFS-2026', title: 'Kuis Evaluasi: Kebijakan Tarif & Kepatuhan Devisa DHE SDA', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji penguasaan Anda mengenai mitigasi tarif ekspor AS dan kepatuhan hukum Devisa Hasil Ekspor SDA PP 21/2026.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Mencakup batas minimal PEB DHE SDA, durasi retensi, dan mitigasi tarif ART', 'Penjelasan yuridis lengkap setelah pengiriman'],
		quizQuestions: [
			{ id: 'QZ-TRF-1', question: 'Berapa ambang batas nilai ekspor (FOB pada PEB) yang mewajibkan penempatan DHE SDA menurut PP No. 21 Tahun 2026?', options: ['Minimal USD 50,000', 'Minimal USD 100,000', 'Minimal USD 250,000', 'Minimal USD 1,000,000'], correctIndex: 2, explanation: 'Berdasarkan ketentuan PP No. 21 Tahun 2026, kewajiban penempatan DHE SDA berlaku bagi eksportir dengan nilai ekspor pada dokumen PEB sebesar minimal USD 250,000 atau ekuivalennya.' },
			{ id: 'QZ-TRF-2', question: 'Berapa persentase dan durasi minimal penempatan DHE SDA non-migas di bank devisa domestik berdasarkan PP 21/2026?', options: ['30% selama minimal 3 bulan', '50% selama minimal 6 bulan', '100% selama minimal 12 bulan', '100% tanpa batas waktu penempatan'], correctIndex: 2, explanation: 'PP 21/2026 memperketat kewajiban DHE SDA non-migas menjadi penempatan 100% selama jangka waktu paling singkat 12 bulan di rekening khusus bank devisa dalam negeri.' },
			{ id: 'QZ-TRF-3', question: 'Bagaimana cara eksportir kopi Indonesia membebaskan diri dari tarif tambahan 10% saat mengekspor ke Amerika Serikat?', options: ['Mengubah nama produk menjadi produk lokal AS', 'Membuktikan pemenuhan kriteria Schedule 2B pada perjanjian bilateral US-Indonesia ART', 'Mengirimkan barang lewat negara transit tanpa dokumen asal', 'Membayar uang jaminan tunai ke otoritas pelabuhan AS'], correctIndex: 1, explanation: 'Berdasarkan Perjanjian Bilateral US-Indonesia Agreement on Reciprocal Trade (ART) 19 Februari 2026, produk Indonesia yang terdaftar di Schedule 2B dikecualikan dari tarif 10% melalui pembuktian sertifikasi asal pada deklarasi CBP 7501.' }
		] },

	// EDU-DES-PANEN-01
	{ id: 'LSN-PAN-01', moduleId: 'EDU-DES-PANEN-01', title: 'Prosedur Sertifikat Kesehatan Tumbuhan (Phytosanitary) Barantin', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Pemerintah melalui Badan Karantina Indonesia (Barantin) berdasarkan UU 21/2019 dan PP 28/2024 mewajibkan setiap komoditas pertanian segar (buah, sayur, rempah basah, bibit) memiliki Sertifikat Kesehatan Tumbuhan (KT-1 / Phytosanitary Certificate). Pengajuan dilakukan melalui portal PPK Online Barantin minimal 3 hari sebelum pemuatan kontainer. Petugas karantina akan mengambil sampel acak untuk uji laboratorium bebas OPTK (Organisme Pengganggu Tumbuhan Karantina).',
		keyPoints: ['Ajukan permohonan pemeriksaan karantina (PPK Online) sebelum barang dimuat ke kontainer', 'Ketahui daftar OPTK golongan I dan II yang dilarang oleh negara tujuan ekspor', 'Sertifikat KT-1 wajib menyertai dokumen pengapalan fisik dan pertukaran data e-Phyto'] },
	{ id: 'LSN-PAN-02', moduleId: 'EDU-DES-PANEN-01', title: 'Standar Mutu Kopi Gayo, Kakao, & Vanila untuk Buyer Jepang dan Uni Eropa', duration: '7 min', kind: 'Reading', completed: false,
		content: 'Komoditas perkebunan desa memiliki potensi pasar premium di Jepang dan Uni Eropa bila memenuhi batas ambang residu pestisida (MRL - Maximum Residue Limit) dan standar mikotoksin (Aflatoksin & Ochratoxin A). Untuk biji kopi, kadar air maksimal adalah 12,5%, dengan defect rate maksimal grade 1 (maksimal 11 nilai cacat menurut SCAA). Biji vanila wajib memiliki kadar vanilin minimal 1,8% dengan kadar air 25–30%.',
		keyPoints: ['Uji batas residu pestisida di laboratorium terakreditasi KAN sebelum shipment', 'Jaga kadar air biji kopi di bawah 12,5% untuk mencegah timbulnya jamur Ochratoxin A', 'Gunakan kemasan kedap udara (mis. GrainPro liner) di dalam karung goni'] },
	{ id: 'LSN-PAN-03', moduleId: 'EDU-DES-PANEN-01', title: 'Pengemasan Higienis & Perlakuan Fumigasi Bebas Serangga untuk Hasil Kebun', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=JnMtuZTjV6Q',
		content: 'Seluruh hasil panen pertanian yang diangkut menggunakan palet kayu wajib memenuhi standar internasional ISPM 15 (perlakuan panas Heat Treatment atau fumigasi). Kemasan primer karung goni wajib dilapisi kantong hermetik (seperti GrainPro) untuk menjaga kadar air dan mematikan serangga hama gudang (seperti kumbang bubuk kopi Hypothenemus hampei) selama pelayaran 30 hari.',
		keyPoints: ['Wajib sertifikat fumigasi atau tanda cap stempel ISPM 15 pada setiap palet kayu', 'Kemasan hermetik mencegah penyerapan kelembapan udara laut di dalam kontainer', 'Lakukan pemeriksaan visual menyeluruh sebelum segel pabean kontainer dipasang'] },
	{ id: 'LSN-PAN-04', moduleId: 'EDU-DES-PANEN-01', title: 'Kuis Evaluasi: Karantina Pertanian & Standar Mutu Panen', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji penguasaan Anda mengenai pengurusan sertifikat karantina tumbuhan, standar batas residu, dan kemasan hasil kebun desa.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Standar karantina Barantin PP 28/2024 dan ambang batas mutu internasional', 'Penjelasan kunci jawaban instan'],
		quizQuestions: [
			{ id: 'QZ-PAN-1', question: 'Lembaga resmi pemerintah Indonesia yang menerbitkan Sertifikat Kesehatan Tumbuhan (Phytosanitary Certificate) adalah:', options: ['Kementerian Pariwisata', 'Badan Karantina Indonesia (Barantin)', 'Dinas Perhubungan Laut', 'Kamar Dagang dan Industri (KADIN)'], correctIndex: 1, explanation: 'Berdasarkan UU 21/2019 dan penataan kelembagaan PP 28/2024, Badan Karantina Indonesia (Barantin) adalah lembaga tunggal yang berwenang menerbitkan sertifikat karantina hewan, ikan, dan tumbuhan.' },
			{ id: 'QZ-PAN-2', question: 'Berapakah kadar air maksimal standar ekspor untuk biji kopi arabika agar terhindar dari jamur mikotoksin?', options: ['Maksimal 25%', 'Maksimal 18%', 'Maksimal 12,5%', 'Bebas tanpa batasan'], correctIndex: 2, explanation: 'Standar Nasional Indonesia (SNI) dan International Coffee Organization menetapkan kadar air biji kopi ekspor maksimal 12,5% guna mencegah pertumbuhan jamur penghasil mikotoksin berbahaya Ochratoxin A.' },
			{ id: 'QZ-PAN-3', question: 'Apa fungsi utama penggunaan kantong pelindung hermetik (seperti GrainPro) di dalam karung goni ekspor?', options: ['Menambah berat barang agar harga jual lebih mahal', 'Mengunci kadar air konstan dan mematikan serangga hama akibat kondisi atmosfer anaerobik', 'Hanya untuk mempercantik tampilan luar karung', 'Sebagai pengganti Bill of Lading'], correctIndex: 1, explanation: 'Kantong hermetik menahan pertukaran uap air dan oksigen dari luar sehingga kualitas rasa terjaga serta serangga hama gudang mati secara alami selama perjalanan kapal.' }
		] },

	// EDU-DES-HALAL-02
	{ id: 'LSN-HAL-01', moduleId: 'EDU-DES-HALAL-02', title: 'Transformasi Regulasi Halal & Registrasi SIHALAL BPJPH', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Berdasarkan UU No. 33 Tahun 2014 jo. Perppu No. 2 Tahun 2022, seluruh produk makanan dan minuman yang beredar dan diekspor wajib bersertifikat halal. Badan Penyelenggara Jaminan Produk Halal (BPJPH) mengelola perizinan terintegrasi via portal SIHALAL (ptsp.halal.go.id). Eksportir desa dapat memanfaatkan jalur Sertifikasi Halal Reguler maupun Fasilitasi Self-Declare bagi pelaku Usaha Mikro dan Kecil (UMK).',
		keyPoints: ['Pendaftaran dilakukan secara daring melalui sistem SIHALAL BPJPH', 'Tunjuk minimal satu orang Penyelia Halal bersertifikat di internal BUMDes', 'Dokumentasikan manual Sistem Jaminan Produk Halal (SJPH) secara tertulis'] },
	{ id: 'LSN-HAL-02', moduleId: 'EDU-DES-HALAL-02', title: 'Kesepakatan Saling Pengakuan (MRA) untuk Pasar Timur Tengah & ASEAN', duration: '7 min', kind: 'Reading', completed: false,
		content: 'Untuk menembus pasar Arab Saudi, Uni Emirat Arab, dan kawasan Teluk (GCC), sertifikat halal Indonesia diakui melalui Mutual Recognition Agreement (MRA) antara BPJPH dan lembaga halal akreditasi setempat (seperti SASO dan SFDA di Arab Saudi, serta ESMA/MoIAT di UEA). Pastikan bahan baku kritis (seperti perisa, gelatin, enzim, emulsifier) memiliki sertifikat halal yang diakui secara timbal balik.',
		keyPoints: ['Periksa status akreditasi MRA lembaga pemeriksa halal negara tujuan', 'Gunakan label halal resmi Indonesia beserta nomor registrasi yang terverifikasi', 'Produk olahan pangan desa wajib bebas dari kontaminasi silang fasilitas non-halal'] },
	{ id: 'LSN-HAL-03', moduleId: 'EDU-DES-HALAL-02', title: 'Audit Lapangan Lembaga Pemeriksa Halal (LPH) & Penerbitan Sertifikat', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=UaPPWKAYj7E',
		content: 'Tahapan sertifikasi halal reguler: 1) Pemilihan Lembaga Pemeriksa Halal (LPH seperti LPPOM MUI, Sucofindo, Surveyor Indonesia); 2) Verifikasi dokumen bahan baku dan diagram alir proses produksi; 3) Audit lapangan oleh auditor halal di tempat pengolahan produk desa; 4) Sidang Fatwa Halal Komite Fatwa MUI; 5) Penerbitan Ketetapan Halal dan Sertifikat Halal BPJPH berjangka waktu 4 tahun.',
		keyPoints: ['Siapkan logbook harian penerimaan bahan baku dan catatan produksi halal', 'Auditor memeriksa kebersihan lini produksi, wadah simpan, dan kemasan', 'Sertifikat halal kini berlaku seumur hidup selama tidak ada perubahan komposisi bahan'] },
	{ id: 'LSN-HAL-04', moduleId: 'EDU-DES-HALAL-02', title: 'Kuis Evaluasi: Sertifikasi Halal Ekspor', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pengetahuan Anda mengenai regulasi jaminan produk halal, proses pendaftaran SIHALAL, dan pengakuan standar halal di pasar internasional.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Mencakup peran BPJPH, MRA sertifikasi, dan persyaratan penyelia halal', 'Pembahasan detail untuk setiap jawaban'],
		quizQuestions: [
			{ id: 'QZ-HAL-1', question: 'Lembaga pemerintah yang berwenang menerbitkan Sertifikat Halal resmi di Indonesia adalah:', options: ['Kementerian Luar Negeri', 'Badan Penyelenggara Jaminan Produk Halal (BPJPH) Kemenag', 'Kementerian BUMN', 'Badan Koordinasi Penanaman Modal (BKPM)'], correctIndex: 1, explanation: 'Berdasarkan amanat UU No. 33 Tahun 2014, BPJPH adalah badan pemerintah di bawah Kemenag yang berwenang menerbitkan sertifikat halal, bekerja sama dengan LPH dan Komisi Fatwa.' },
			{ id: 'QZ-HAL-2', question: 'Apa fungsi dari Mutual Recognition Agreement (MRA) dalam sertifikasi halal antarnegara?', options: ['Untuk mengenakan tarif bea masuk ganda', 'Saling mengakui kesetaraan standar sertifikat halal sehingga produk tidak perlu sertifikasi ulang di negara tujuan', 'Membatalkan seluruh sertifikat lokal di negara pengimpor', 'Menghapus kewajiban pemeriksaan pabean'], correctIndex: 1, explanation: 'MRA halal memungkinkan sertifikat halal yang diterbitkan BPJPH diakui secara sah oleh otoritas pangan negara tujuan (misal SFDA Arab Saudi), mempercepat proses izin edar impor.' },
			{ id: 'QZ-HAL-3', question: 'Siapakah personil kunci yang wajib ditunjuk oleh pelaku usaha di internal perusahaan untuk mengawal proses sertifikasi halal?', options: ['Pialang bea cukai eksternal', 'Penyelia Halal yang beragama Islam dan memahami syariat jaminan produk halal', 'Supir truk ekspedisi', 'Kepala kantor imigrasi pelabuhan'], correctIndex: 1, explanation: 'UU JPH mewajibkan setiap pelaku usaha memiliki minimal seorang Penyelia Halal internal yang bertugas memimpin dan mengawasi implementasi Sistem Jaminan Produk Halal.' }
		] },

	// EDU-DES-KEMAS-03
	{ id: 'LSN-KMS-01', moduleId: 'EDU-DES-KEMAS-03', title: 'Teknik Moisture Barrier & Kalkulasi Silica Gel Kontainer', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Pengiriman laut melintasi zona tropis menuju negara 4 musim menghasilkan fenomena "hujan kontainer" (container rain) akibat kondensasi udara dingin pada langit-langit peti kemas. Untuk produk kerajinan rotan, kayu, dan anyaman serat alam, eksportir wajib menggunakan desiccant pole kalsium klorida (bukan silica gel kecil biasa) dengan rasio minimal 1 unit (1 kg) per 5 meter kubik volume kontainer, serta membungkus barang dengan plastik barrier kedap uap air.',
		keyPoints: ['Gunakan container desiccant kalsium klorida berkemampuan serap 200–300% berat kering', 'Bungkus kriya dengan kertas krep dan plastik pelindung kelembapan (moisture barrier)', 'Hindari memasukkan kardus karton yang basah atau lembap saat stuffing kontainer'] },
	{ id: 'LSN-KMS-02', moduleId: 'EDU-DES-KEMAS-03', title: 'Perlindungan Sudut (Corner Protectors) & Fumigasi Palet ISPM 15', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=tK-V0wXk-V0',
		content: 'Kerusakan fisik terbesar pada kriya furnitur rotan dan kayu terjadi akibat guncangan gelombang laut (pitching & rolling). Pasang edge corner protectors karton tebal pada seluruh sudut kemasan luar. Seluruh palet kayu penopang wajib memiliki cap logo gandum resmi ISPM 15 (menandakan perlakuan Heat Treatment HT atau Methyl Bromide MB) dari perusahaan fumigasi teregistrasi Barantin.',
		keyPoints: ['Corner protector melindungi sudut karton dari tindihan strapping band', 'Palet tanpa cap ISPM 15 akan ditolak masuk dan diperintahkan re-ekspor oleh customs tujuan', 'Beri bantalan dunnage air bag di sela-sela palet agar muatan tidak bergeser saat kapal berlayar'] },
	{ id: 'LSN-KMS-03', moduleId: 'EDU-DES-KEMAS-03', title: 'SOP Dokumentasi Pre-Loading Foto untuk Validasi Klaim Asuransi', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Lebih dari 60% klaim asuransi kargo ditolak perusahaan penjamin karena eksportir tidak memiliki bukti kondisi awal muatan sebelum berangkat. Terapkan SOP foto wajib: 1) Foto kondisi lantai dan dinding kontainer kosong (pastikan bersih, kering, tidak bocor cahaya); 2) Foto lapisan pertama pemuatan barang; 3) Foto desiccant pole terpasang; 4) Foto saat kontainer terisi 100%; 5) Foto penutupan pintu sebelah kanan kontainer beserta nomor segel (seal number).',
		keyPoints: ['Pemeriksaan "light check" kontainer kosong: masuk dan tutup pintu, pastikan tiada lubang cahaya', 'Dokumentasikan nomor seri segel kontainer (bolt seal) secara berdampingan dengan B/L', 'Bukti foto pre-loading adalah syarat mutlak persetujuan klaim surveyor asuransi maritim'] },
	{ id: 'LSN-KMS-04', moduleId: 'EDU-DES-KEMAS-03', title: 'Kuis Evaluasi: Pengemasan Kriya & Proteksi Kontainer', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pemahaman Anda mengenai mitigasi risiko kelembapan laut, standar palet ISPM 15, dan dokumentasi klaim asuransi kriya.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Standar pengemasan kriya rotan/kayu dan regulasi ISPM 15', 'Penjelasan kunci jawaban praktis'],
		quizQuestions: [
			{ id: 'QZ-KMS-1', question: 'Apakah penyebab utama fenomena "container rain" (hujan kontainer) yang sering merusak produk kerajinan alam?', options: ['Air laut yang merembes melalui celah pintu kontainer', 'Kondensasi udara lembap di dalam kontainer akibat perbedaan suhu ekstrem siang dan malam', 'Pencucian kontainer yang tidak dikeringkan', 'Kesalahan awak kapal menyiram atap kapal'], correctIndex: 1, explanation: 'Udara hangat dan lembap di dalam kontainer mengalami pengembunan saat dinding luar kontainer mendingin drastis di perairan dingin, menjatuhkan tetesan air ke muatan kriya.' },
			{ id: 'QZ-KMS-2', question: 'Tanda standar internasional apakah yang wajib tercantum pada palet kayu penopang ekspor menurut aturan karantina dunia?', options: ['Label SNI', 'Cap Logo Gandum ISPM 15', 'Tanda barcode toko ritel', 'Stempel tanda lunas bea cukai'], correctIndex: 1, explanation: 'Standar ISPM 15 (International Standards for Phytosanitary Measures) mewajibkan palet kayu diberi cap logo gandum bertuliskan kode negara dan jenis perlakuan (HT/MB) untuk mencegah penyebaran hama kayu lintas benua.' },
			{ id: 'QZ-KMS-3', question: 'Mengapa foto nomor segel kontainer (bolt seal) pada pintu peti kemas wajib diambil sebelum kontainer diberangkatkan?', options: ['Hanya untuk koleksi dokumentasi media sosial eksportir', 'Sebagai bukti hukum bahwa kontainer tertutup rapat dan belum pernah dibuka sejak pemuatan awal, krusial bagi klaim asuransi jika terjadi pencurian/kerusakan', 'Syarat untuk mendapatkan diskon tol laut', 'Sebagai pengganti nota pajak pertambahan nilai'], correctIndex: 1, explanation: 'Foto segel utuh membuktikan muatan berada dalam kondisi aman saat diserahkan ke pengangkut, menjadi dasar klaim asuransi bila segel tiba di tujuan dalam kondisi rusak atau berganti nomor.' }
		] },

	// EDU-DES-NIB-04
	{ id: 'LSN-NIB-01', moduleId: 'EDU-DES-NIB-04', title: 'Transformasi BUMDes Berbadan Hukum & Pengurusan NIB di OSS-RBA', duration: '6 min', kind: 'Reading', completed: false,
		content: 'UU Cipta Kerja dan PP No. 11 Tahun 2021 menetapkan BUMDes (Badan Usaha Milik Desa) dan BUMDes Bersama resmi berstatus sebagai badan hukum. Pendaftaran dilakukan ke Kementerian Desa, dilanjutkan dengan pendaftaran Nomor Induk Berusaha (NIB) secara daring melalui sistem Online Single Submission Risk-Based Approach (OSS-RBA). NIB kini berlaku sebagai identitas legal tunggal, Tanda Daftar Perusahaan (TDP), dan Angka Pengenal Impor/Ekspor (API).',
		keyPoints: ['BUMDes memiliki legalitas badan hukum setara perseroan terbatas setelah terdaftar di Kemendes', 'NIB di OSS-RBA secara otomatis berfungsi sebagai identitas kepabeanan ekspor-impor', 'Pilih Klasifikasi Baku Lapangan Usaha Indonesia (KBLI) 5 digit yang tepat untuk kegiatan perdagangan ekspor'] },
	{ id: 'LSN-NIB-02', moduleId: 'EDU-DES-NIB-04', title: 'Pendaftaran KBLI Perdagangan Ekspor & Fasilitas Pembebasan Bea Masuk UMK', duration: '7 min', kind: 'Reading', completed: false,
		content: 'Pelaku usaha desa wajib memilih KBLI perdagangan besar atau ekspor sesuai komoditasnya (contoh: KBLI 46201 untuk perdagangan besar hasil pertanian, 46311 untuk kopi/teh/kakao). Berdasarkan Permendag 16/2025 dan kebijakan Kementerian Keuangan, pelaku UMK desa berhak mendapatkan fasilitas Kemudahan Impor Tujuan Ekspor (KITE IKM), pembebasan bea masuk bahan baku penolong, serta asistensi klinik ekspor Bea Cukai.',
		keyPoints: ['KBLI 5 digit menentukan izin teknis dan rekomendasi kementerian terkait', 'Fasilitas KITE IKM memberikan pembebasan bea masuk dan PPN tidak dipungut untuk bahan baku olahan ekspor', 'Manfaatkan fasilitas pembiayaan modal kerja ekspor berbunga rendah dari LPEI (Indonesia Eximbank)'] },
	{ id: 'LSN-NIB-03', moduleId: 'EDU-DES-NIB-04', title: 'Tata Kelola Keuangan Ekspor & Pembayaran L/C untuk Koperasi Desa', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=3-1hUZ6EZn0',
		content: 'Manajemen keuangan ekspor bagi BUMDes dan koperasi tani: 1) Pemilihan metode pembayaran aman: Irrevocable Letter of Credit (L/C) at Sight untuk buyer baru, atau Telegraphic Transfer (T/T) dengan uang muka minimal 30–50%; 2) Hindari skema Open Account untuk pembeli perdana tanpa penjaminan asuransi ekspor (seperti Asuransi Pembayaran Askrindo/LPEI); 3) Pisahkan rekening kas operasional BUMDes dengan rekening transaksi ekspor valas.',
		keyPoints: ['Letter of Credit (L/C) at sight menjamin pembayaran dari bank pembeli setelah dokumen pengapalan valid', 'Mitigasi risiko gagal bayar pembeli luar negeri dengan asuransi piutang dagang ekspor LPEI', 'Tertib pembukuan keuangan desa memperkuat kelayakan kredit perbankan nasional'] },
	{ id: 'LSN-NIB-04', moduleId: 'EDU-DES-NIB-04', title: 'Kuis Evaluasi: Legalitas Usaha & Fasilitas Ekspor Desa', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji penguasaan Anda mengenai status badan hukum BUMDes, fungsi NIB OSS-RBA, dan tata kelola pembayaran ekspor internasional.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Mencakup kedudukan hukum BUMDes, sistem OSS-RBA, dan instrumen pembayaran L/C', 'Evaluasi skor dan ulasan jawaban benar'],
		quizQuestions: [
			{ id: 'QZ-NIB-1', question: 'Berdasarkan regulasi terkini di Indonesia, apakah kedudukan hukum resmi Badan Usaha Milik Desa (BUMDes)?', options: ['Bukan badan hukum, hanya unit informal desa', 'Resmi berkedudukan sebagai Badan Hukum mandiri setelah mendapatkan sertifikat dari kementerian terkait', 'Hanya bagian dari kepanitiaan pemilihan kepala desa', 'Organisasi sosial kemasyarakatan tanpa hak berbisnis'], correctIndex: 1, explanation: 'UU Cipta Kerja dan PP 11/2021 menegaskan bahwa BUMDes dan BUMDes Bersama adalah badan hukum mandiri yang berhak mengadakan kontrak bisnis internasional dan membuka rekening perbankan ekspor.' },
			{ id: 'QZ-NIB-2', question: 'Apakah fungsi utama Nomor Induk Berusaha (NIB) yang diterbitkan melalui portal OSS-RBA bagi eksportir pemula?', options: ['Hanya tanda bukti bayar pajak kendaraan bermotor', 'Berfungsi sebagai identitas berusaha tunggal sekaligus hak akses kepabeanan ekspor (Angka Pengenal Impor/Ekspor)', 'Sebagai tiket masuk pelabuhan bongkar muat', 'Kartu identitas pegawai BUMDes'], correctIndex: 1, explanation: 'Sistem OSS-RBA mengintegrasikan berbagai perizinan, di mana satu nomor NIB otomatis berlaku sebagai identitas legalitas, TDP, dan identitas kepabeanan untuk aktivitas ekspor-impor.' },
			{ id: 'QZ-NIB-3', question: 'Metode pembayaran perdagangan internasional manakah yang memberikan kepastian jaminan bayar tertinggi dari bank pembeli bagi eksportir desa?', options: ['Open Account (bayar belakangan setelah barang laku)', 'Konsinyasi titip jual', 'Irrevocable Letter of Credit (L/C) at Sight', 'Cek tunai lewat pos surat'], correctIndex: 2, explanation: 'Irrevocable L/C at sight memberikan komitmen tanpa syarat dari bank penerbit (issuing bank) untuk membayar eksportir segera setelah dokumen pengapalan yang sah dan sesuai syarat L/C diserahkan.' }
		] },

	// Alias IDs untuk kompatibilitas kurikulum desa seeder
	{ id: 'LSN-DES-PANEN-01', moduleId: 'EDU-DES-PANEN-01', title: 'Kenali komoditas & hama karantina', duration: '5 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=JnMtuZTjV6Q',
		content: 'Hasil panen segar wajib melewati karantina pertanian. Kenali media pembawa, hama penyakit, dan syarat phytosanitary negara tujuan.',
		keyPoints: ['Identifikasi jenis komoditas & hama', 'Karantina pertanian menerbitkan phytosanitary', 'Sampel & pemeriksaan lapangan'] },
	{ id: 'LSN-DES-HALAL-01', moduleId: 'EDU-DES-HALAL-02', title: 'Bahan & proses produksi halal', duration: '5 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=UaPPWKAYj7E',
		content: 'Sertifikasi halal menilai bahan, pemasok, dan proses produksi (PPH). Pahami requirement negara tujuan seperti GAC/SMAS di Timur Tengah.',
		keyPoints: ['Kumpulkan daftar bahan & pemasok', 'Amankan proses produksi halal', 'Cek requirement negara tujuan'] },
	{ id: 'LSN-DES-NIB-01', moduleId: 'EDU-DES-NIB-04', title: 'Registrasi OSS-RBA & KBLI', duration: '5 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=3-1hUZ6EZn0',
		content: 'Urusan legalitas dasar: Nomor Induk Berusaha (NIB) dan IUMK lewat OSS-RBA, isi KBLI sesuai komoditas, dan fasilitas kepabeanan bagi UMK.',
		keyPoints: ['Siapkan akta & NPWP', 'Isi KBLI 5 digit', 'Unduh NIB & IUMK'] },
	{ id: 'LSN-DES-KARANTINA-01', moduleId: 'EDU-DES-KARANTINA-06', title: 'PP 28/2024 & tindakan karantina', duration: '5 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=JnMtuZTjV6Q',
		content: 'Memahami PP 28/2024 tentang karantina hewan, ikan, dan tumbuhan: penggolongan media pembawa, wilayah karantina, dan tindakan P4/PK/PKHP.',
		keyPoints: ['Golongan MHK/MKH/TIK', 'Tindakan karantina P4/PK/PKHP', 'Biaya & layanan cepat karantina'] },

	// EDU-DES-DOC-05
	{ id: 'LSN-DOC-01', moduleId: 'EDU-DES-DOC-05', title: 'Spesifikasi Dokumen Wajib Ekspor Pangan ke SFA Singapura & MAFF Jepang', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Regulasi impor pangan segar di Singapura diawasi oleh SFA berdasarkan Sale of Food Act, sedangkan di Jepang diatur oleh MAFF dan MHLW. Dokumen inti meliputi: Phytosanitary Certificate Barantin, Health Certificate, Certificate of Origin (Form D / Form IJEPA), CoA residu pestisida lab terakreditasi ISO 17025, serta invoice & packing list bilingual.',
		keyPoints: ['SFA Singapura mewajibkan registrasi establishment dan CoA batas residu pestisida', 'Jepang menerapkan Positive List System untuk 800+ jenis bahan kimia pertanian', 'Sertifikat Fitosanitari Barantin wajib diterbitkan maksimal 14 hari sebelum waktu muat kapal'] },
	{ id: 'LSN-DOC-02', moduleId: 'EDU-DES-DOC-05', title: 'Prosedur Pengurusan SKA Elektronik (e-Form D/IJEPA) & Health Certificate', duration: '6 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=C7VLuiVPIQM',
		content: 'Pelajari alur pendaftaran dan penerbitan Surat Keterangan Asal (SKA) secara elektronik melalui sistem e-SKA Kementerian Perdagangan RI guna mengamankan tarif bea masuk preferensi 0% ke negara mitra dagang.',
		keyPoints: ['Pendaftaran akun e-SKA menggunakan NIB berbasis risiko', 'Kalkulasi Regional Value Content (RVC) minimal 40% untuk preferensi tarif ASEAN', 'Pengiriman dokumen e-Form D terintegrasi melalui ASEAN Single Window (ASW)'] },
	{ id: 'LSN-DOC-03', moduleId: 'EDU-DES-DOC-05', title: 'Standar Uji Residu Laboratorium (CoA) & Traceability Lot Panen', duration: '5 min', kind: 'Reading', completed: false,
		content: 'Hasil uji Certificate of Analysis (CoA) wajib dikeluarkan oleh laboratorium uji pangan yang diakui KAN berstandar ISO/IEC 17025. Data nomor lot panen, tanggal panen, nama kebun, dan jenis pestisida yang digunakan wajib identik dengan penandaan fisik pada tiap kemasan box ekspor.',
		keyPoints: ['Laboratorium penguji wajib mengantongi akreditasi KAN ISO/IEC 17025', 'Patuhi Maximum Residue Limit (MRL) spesifik negara tujuan', 'Nomor batch pada CoA wajib tertelusur (traceable) ke catatan kebun petani'] },
	{ id: 'LSN-DOC-04', moduleId: 'EDU-DES-DOC-05', title: 'Kuis Evaluasi: Dokumen Ekspor Pertanian Singapura & Jepang', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji kompetensi Anda mengenai standardisasi dokumen pangan segar, pengurusan SKA elektronik, dan uji laboratorium residu pestisida.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Mencakup otoritas SFA, batas RVC pada e-Form D, dan fungsi Certificate of Analysis', 'Evaluasi skor dan kunci jawaban pembuktian dokumen'],
		quizQuestions: [
			{ id: 'QZ-DOC-1', question: 'Otoritas manakah di Singapura yang bertindak sebagai pengawas gerbang impor produk pangan segar?', options: ['Maritime and Port Authority (MPA)', 'Singapore Food Agency (SFA)', 'Singapore Police Force', 'Civil Aviation Authority of Singapore'], correctIndex: 1, explanation: 'Singapore Food Agency (SFA) adalah otoritas tunggal di bawah Kementerian Keberlanjutan dan Lingkungan Hidup Singapura yang mengawasi keamanan pangan dan inspeksi impor produk pertanian.' },
			{ id: 'QZ-DOC-2', question: 'Berapakah batas ambang minimal Regional Value Content (RVC) agar komoditas berhak menikmati tarif 0% via skema SKA Form D (ATIGA)?', options: ['Minimal 10%', 'Minimal 25%', 'Minimal 40%', 'Wajib 100% tanpa kompromi'], correctIndex: 2, explanation: 'Skema ASEAN Trade in Goods Agreement (ATIGA) menetapkan aturan asal barang standar dengan nilai kandungan lokal ASEAN (Regional Value Content / RVC) minimal 40%.' },
			{ id: 'QZ-DOC-3', question: 'Mengapa nomor batch atau lot pada Certificate of Analysis (CoA) wajib dicocokkan dengan label kemasan produk?', options: ['Hanya untuk memenuhi warna desain kemasan', 'Sebagai syarat mutlak ketertelusuran (traceability) keamanan pangan apabila terjadi penarikan produk (recall)', 'Agar pengemudi truk ekspedisi tidak tersesat', 'Tidak ada pengaruhnya terhadap kepatuhan pabean'], correctIndex: 1, explanation: 'Otoritas karantina dan pangan internasional mewajibkan traceability penuh: nomor lot pada CoA membuktikan bahwa produk fisik yang dikirim adalah spesimen yang sama dengan yang diuji di laboratorium.' }
		] },

	// EDU-DES-KARANTINA-06
	{ id: 'LSN-KARANTINA-02', moduleId: 'EDU-DES-KARANTINA-06', title: '8 Tindakan Karantina (8P) & Kategori Media Pembawa OPTK', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Peraturan Pemerintah No. 28 Tahun 2024 menyatukan mandat penyelenggaraan karantina hewan, ikan, dan tumbuhan ke dalam 8 Tindakan Karantina (8P): Pemeriksaan, Pengasingan, Pengamatan, Perlakuan, Penahanan, Penolakan, Pemusnahan, dan Pembebasan. Komoditas pertanian desa diklasifikasikan sebagai Media Pembawa OPTK yang wajib steril dari tanah, gulma invasif, maupun larva serangga hidup.',
		keyPoints: ['8 Tindakan Karantina (8P) dijalankan secara proporsional sesuai analisis risiko', 'Larangan mutlak kontaminasi tanah liat/media tanam mentah pada produk segar', 'Sertifikat Kesehatan Tumbuhan diterbitkan sebagai bukti tindakan pembebasan karantina'] },
	{ id: 'LSN-KARANTINA-03', moduleId: 'EDU-DES-KARANTINA-06', title: 'Fasilitas Periksa Lapangan di Tempat Produksi (In-Line Inspection)', duration: '5 min', kind: 'Reading', completed: false,
		content: 'Badan Karantina Indonesia menyediakan mekanisme pemeriksaan karantina di tempat produksi atau packing house desa (In-Line Inspection). Pejabat karantina meninjau SOP kebersihan, perlakuan pascapanen, dan sanitasi ruang kemas sebelum barang dikirim ke pelabuhan muat, sehingga mengeliminasi risiko penolakan kargo di dermaga ekspor.',
		keyPoints: ['Pengajuan pemeriksaan karantina sebelum barang diberangkatkan dari desa', 'Pemberian perlakuan teknis seperti pencucian, fumigasi, atau perlakuan panas terkendali', 'Pengawalan kargo berpendingin berstatus segel karantina menuju pelabuhan laut/udara'] },
	{ id: 'LSN-KARANTINA-04', moduleId: 'EDU-DES-KARANTINA-06', title: 'Kuis Evaluasi: Regulasi Karantina Pertanian PP 28/2024', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pemahaman Anda mengenai prinsip 8 Tindakan Karantina, mitigasi risiko OPTK, dan fasilitas In-Line Inspection Barantin.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Membahas integrasi Barantin, tindakan perlakuan karantina, dan keuntungan inspeksi di desa', 'Skor langsung dan evaluasi pembahasan resmi'],
		quizQuestions: [
			{ id: 'QZ-KARANTINA-1', question: 'Apa peran strategis pembentukan Badan Karantina Indonesia (Barantin) menurut PP 28/2024?', options: ['Menetapkan tarif pajak penghasilan badan', 'Mengintegrasikan seluruh fungsi karantina hewan, ikan, dan tumbuhan ke dalam satu lembaga terpadu', 'Mengambil alih fungsi operasional kapal kargo niaga', 'Menyediakan bibit tanaman gratis bagi petani'], correctIndex: 1, explanation: 'PP 28/2024 menyatukan otoritas karantina pertanian dan perikanan ke bawah Badan Karantina Indonesia (Barantin) sebagai institusi karantina satu pintu nasional.' },
			{ id: 'QZ-KARANTINA-2', question: 'Manakah tindakan karantina yang diterapkan bila kargo buah ditemukan membawa serangga hidup namun jenisnya masih dapat dibasmi?', options: ['Pemusnahan seketika di tempat', 'Tindakan Perlakuan (Treatment), seperti fumigasi atau perlakuan uap panas (Vapour Heat Treatment)', 'Dibiarkan lolos tanpa tindakan', 'Denda tunai tanpa pembersihan hama'], correctIndex: 1, explanation: 'Tindakan Perlakuan (Treatment) dilakukan untuk mengeliminasi hama penyakit target tanpa merusak mutu fisik komoditas, sebelum sertifikat karantina diterbitkan.' },
			{ id: 'QZ-KARANTINA-3', question: 'Apa manfaat utama skema In-Line Inspection bagi pelaku usaha desa?', options: ['Bebas dari seluruh pemeriksaan bea cukai', 'Pemeriksaan dan sertifikasi dilakukan di packing house desa sehingga mencegah risiko penahanan kontainer di pelabuhan', 'Ongkos kirim kapal laut digratiskan oleh otoritas pabean', 'Komoditas tidak perlu dikemas dengan rapi'], correctIndex: 1, explanation: 'In-Line Inspection memastikan komoditas telah memenuhi standar sebelum kargo berangkat, meminimalkan demurrage kontainer dan pembongkaran ulang di pelabuhan.' }
		] },

	// EDU-DES-CITES-07
	{ id: 'LSN-CITES-01', moduleId: 'EDU-DES-CITES-07', title: 'Verifikasi Legalitas Kayu SVLK & Sertifikasi Ekspor Kriya Alam', duration: '5 min', kind: 'Video', completed: false,
		videoUrl: 'https://www.youtube.com/watch?v=tK-V0wXk-V0',
		content: 'Pelajari tata cara pemenuhan standar Sistem Verifikasi Kelestarian Kayu (SVLK) untuk produk kerajinan berbahan kayu, rotan, dan bambu desa serta rantai pasok lacak balak berkelanjutan.',
		keyPoints: ['Pentingnya dokumen V-Legal untuk menembus pasar Eropa, AS, dan Australia', 'Audit lacak balak (chain of custody) dari sumber bahan baku ke produk jadi', 'Standar kemasan kayu palet ISPM 15 anti rayap dan serangga perusak kayu'] },
	{ id: 'LSN-CITES-02', moduleId: 'EDU-DES-CITES-07', title: 'Ketentuan Appendix CITES untuk Komoditas Kerajinan & Satwa/Tumbuhan', duration: '6 min', kind: 'Reading', completed: false,
		content: 'Konvensi Perdagangan Internasional Spesies Terancam Punah (CITES) mengatur lalu lintas flora dan fauna liar. Komoditas seperti kayu gaharu (Aquilaria), sonokeling (Dalbergia latifolia), ramin, serta kulit reptil budidaya masuk dalam Appendix II CITES. Ekspor komersial diperbolehkan namun wajib mengantongi kuota tangkap/panen dan Surat Angkut Tumbuhan dan Satwa Liar Luar Negeri (SATS-LN) dari Ditjen KSDAE Kementerian Lingkungan Hidup dan Kehutanan (KLHK).',
		keyPoints: ['Appendix I mutlak dilarang untuk ekspor komersial', 'Appendix II mewajibkan izin SATS-LN KLHK dan verifikasi kuota resmi', 'Cantumkan nama ilmiah botani/zoologi pada invoice dan dokumen pengapalan'] },
	{ id: 'LSN-CITES-03', moduleId: 'EDU-DES-CITES-07', title: 'Deklarasi Kesesuaian Pemasok (DKP) bagi Pengrajin Kriya Desa', duration: '5 min', kind: 'Reading', completed: false,
		content: 'Untuk pengrajin mikro di desa yang mengolah kayu dari kebun rakyat atau hutan hak, pemerintah menyediakan skema Deklarasi Kesesuaian Pemasok (DKP). Pengrajin cukup mengisi formulir DKP yang melampirkan bukti kepemilikan pohon atau nota angkutan desa, yang kemudian dapat digunakan oleh eksportir mitra untuk menerbitkan Dokumen V-Legal tanpa beban biaya audit industri besar.',
		keyPoints: ['DKP memberikan fasilitas kepatuhan legalitas yang ramah biaya bagi UMK desa', 'Wajib dilengkapi surat kepemilikan pohon/tanah rakyat yang sah', 'Menjadi dasar penerbitan Dokumen V-Legal kepabeanan oleh Lembaga Verifikasi'] },
	{ id: 'LSN-CITES-04', moduleId: 'EDU-DES-CITES-07', title: 'Kuis Evaluasi: Regulasi CITES & Legalitas Kayu SVLK', duration: '4 min', kind: 'Quiz', completed: false,
		content: 'Uji pengetahuan Anda mengenai klasifikasi Appendix CITES, penerbitan izin SATS-LN KLHK, dan dokumen legalitas kayu SVLK.',
		keyPoints: ['Kuis 3 pertanyaan pilihan ganda', 'Memvalidasi pemahaman Appendix II, dokumen SATS-LN, dan dokumen V-Legal', 'Penjelasan kunci jawaban disertakan langsung'],
		quizQuestions: [
			{ id: 'QZ-CITES-1', question: 'Pada kategori Appendix manakah flora/fauna yang terdaftar CITES boleh diperdagangkan secara komersial dengan izin ekspor khusus?', options: ['Appendix I', 'Appendix II', 'Appendix Nol', 'Tidak ada yang boleh diperdagangkan sama sekali'], correctIndex: 1, explanation: 'Spesies yang terdaftar dalam Appendix II CITES dapat diperdagangkan secara komersial selama memiliki kuota tangkap/panen yang berkelanjutan dan izin ekspor resmi (SATS-LN).' },
			{ id: 'QZ-CITES-2', question: 'Dokumen apakah yang diterbitkan oleh KLHK sebagai izin resmi ekspor spesimen tumbuhan atau satwa liar yang diatur CITES?', options: ['Surat Izin Mengemudi Kapal (SIM-K)', 'Surat Angkut Tumbuhan dan Satwa Liar Luar Negeri (SATS-LN)', 'Kartu Tanda Penduduk Pengrajin', 'Kwitansi Belanja Pasar Tradisional'], correctIndex: 1, explanation: 'SATS-LN (Surat Angkut Tumbuhan dan Satwa Liar Luar Negeri) adalah dokumen izin ekspor resmi yang diterbitkan oleh Management Authority CITES di Indonesia (Ditjen KSDAE KLHK).' },
			{ id: 'QZ-CITES-3', question: 'Apakah fungsi utama Dokumen V-Legal pada pengapalan ekspor kerajinan kayu Indonesia?', options: ['Memberikan diskon pajak pertambahan nilai bagi buyer', 'Membuktikan bahwa kayu dipanen dan diolah dari sumber legal yang terverifikasi secara sah sesuai standar SVLK', 'Sebagai pengganti asuransi kapal laut', 'Sebagai tanda lunas pembayaran kontainer'], correctIndex: 1, explanation: 'Dokumen V-Legal merupakan lisensi ekspor resmi yang membuktikan seluruh rantai pasok kayu memenuhi standar legalitas dan kelestarian (SVLK), diakui secara internasional seperti di Uni Eropa (FLEGT License).' }
		] }
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
		duties: '0% (IJEPA preferential tariff line vulnerable to rules-of-origin checks)',
		restrictions: [
			'Label wajib Bahasa Jepang dengan deklarasi 28 alergen (Food Sanitation Act)',
			'Laporan uji residu pestisida terakreditasi dalam 12 bulan',
			'Sertifikat asal e-SKA untuk tarif preferensi 0% IJEPA',
			'Kepatuhan penempatan DHE SDA 100% 12 bulan di Himbara bila nilai >= USD 250k (PP 21/2026)'
		],
		recommendations: [
			{ type: 'Certificate', title: 'Certificate of Origin (IJEPA)', status: 'Required', detail: 'Form e-SKA IJEPA untuk klaim tarif preferensi 0% di bea cukai Jepang.' },
			{ type: 'Labeling', title: 'Label pangan Bahasa Jepang (28 alergen)', status: 'Required', detail: 'Cantumkan komposisi, produsen, importir resmi Jepang, dan deklarasi 28 alergen.' },
			{ type: 'Document', title: 'Laporan lab residu pestisida', status: 'Required', detail: 'Sesuai regulasi Positive List System Jepang dalam 12 bulan terakhir.' },
			{ type: 'Document', title: 'Rekening Khusus DHE SDA Himbara (PP 21/2026)', status: 'Required', detail: 'Wajib dipenuhi eksportir non-migas untuk transaksi >= USD 250,000 agar tidak terkena blokir CEISA.' }
		],
		summary: 'Jepang adalah peluang permintaan tinggi dengan tarif 0% via IJEPA; bukti label 28 alergen, laporan lab, dan kepatuhan DHE SDA wajib dipenuhi sebelum persetujuan kuotasi.'
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
		duties: '0% (EU GSP / persiapan ratifikasi IEU-CEPA)',
		restrictions: [
			'EUDR compliance: geolokasi poligon kebun/hutan dan bukti bebas deforestasi post-31 Des 2020',
			'Due Diligence Statement (DDS) via EU Deforestation Information System',
			'Legalitas kayu SVLK / V-Legal terverifikasi',
			'Sertifikat fumigasi ISPM-15 untuk kemasan & komponen kayu',
			'Kepatuhan kemasan daur ulang bebas PFAS (EU PPWR)'
		],
		recommendations: [
			{ type: 'Certificate', title: 'EUDR Due Diligence Statement (DDS)', status: 'Required', detail: 'Wajib diserahkan ke importir Jerman sebelum batas waktu kepatuhan 30 Des 2026.' },
			{ type: 'Certificate', title: 'Sertifikat Legalitas Kayu (SVLK / V-Legal)', status: 'Required', detail: 'Bukti rantai pasok kayu legal dari hulu kehutanan ke manufaktur.' },
			{ type: 'Document', title: 'Sertifikat Fumigasi ISPM-15', status: 'Required', detail: 'Standar perlakuan panas / fumigasi kemasan kayu kargo ekspor.' },
			{ type: 'Labeling', title: 'Label Kemasan Daur Ulang EU PPWR', status: 'Recommended', detail: 'Pastikan kemasan karton dan pengikat bebas PFAS dan dapat didaur ulang.' }
		],
		summary: 'Akses pasar Uni Eropa memerlukan pemenuhan regulasi EUDR (geolokasi lahan & DDS) per 30 Desember 2026 di samping sertifikasi SVLK dan ISPM-15; negosiasi IEU-CEPA yang rampung substansi akan memperkuat akses masa depan.'
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

// ---------- Seed direktori negara (fallback saat server offline) ----------
export type CountrySeed = {
	country_code: string;
	country_name: string;
	region: string;
	subregion?: string;
	customs_system?: string;
	has_details?: boolean;
	risk_level?: string;
	regulationsCount?: number;
};

export const seedCountries: CountrySeed[] = [
	{ country_code: 'ID', country_name: 'Indonesia', region: 'Asia', subregion: 'South-Eastern Asia', customs_system: 'ASEAN', has_details: true, risk_level: 'Moderate', regulationsCount: 9 },
	{ country_code: 'JP', country_name: 'Japan', region: 'Asia', subregion: 'Eastern Asia', customs_system: 'PRODCOM', has_details: true, risk_level: 'Moderate', regulationsCount: 8 },
	{ country_code: 'US', country_name: 'United States', region: 'Americas', subregion: 'Northern America', customs_system: 'PRODCOM', has_details: true, risk_level: 'Elevated', regulationsCount: 8 },
	{ country_code: 'CN', country_name: 'China', region: 'Asia', subregion: 'Eastern Asia', customs_system: 'PRODCOM', has_details: true, risk_level: 'Elevated', regulationsCount: 7 },
	{ country_code: 'KR', country_name: 'South Korea', region: 'Asia', subregion: 'Eastern Asia', customs_system: 'PRODCOM', has_details: true, risk_level: 'Moderate', regulationsCount: 8 },
	{ country_code: 'DE', country_name: 'Germany', region: 'Europe', subregion: 'Western Europe', customs_system: 'EU', has_details: true, risk_level: 'Moderate', regulationsCount: 7 },
	{ country_code: 'GB', country_name: 'United Kingdom', region: 'Europe', subregion: 'Northern Europe', customs_system: 'PRODCOM', has_details: true, risk_level: 'Moderate', regulationsCount: 7 },
	{ country_code: 'CA', country_name: 'Canada', region: 'Americas', subregion: 'Northern America', customs_system: 'PRODCOM', has_details: true, risk_level: 'Moderate', regulationsCount: 6 },
	{ country_code: 'AU', country_name: 'Australia', region: 'Oceania', subregion: 'Australia and New Zealand', customs_system: 'PRODCOM', has_details: true, risk_level: 'Moderate', regulationsCount: 7 },
	{ country_code: 'SG', country_name: 'Singapore', region: 'Asia', subregion: 'South-Eastern Asia', customs_system: 'ASEAN', has_details: true, risk_level: 'Low', regulationsCount: 6 },
];
