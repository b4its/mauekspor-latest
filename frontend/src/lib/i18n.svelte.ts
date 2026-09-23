// i18n ringan: kamus id/en + store lokal (localStorage) + fungsi t().
// Label default aplikasi memakai bahasa Inggris (navGroups, header),
// kamus memetakan label Inggris -> {id, en} sehingga ID = terjemahan.
export type Locale = 'id' | 'en';

type Entry = { id: string; en: string };

const dictionary: Record<string, Entry> = {
	// --- Sidebar: group & item labels (navGroups) ---
	Overview: { id: 'Ikhtisar', en: 'Overview' },
	Dashboard: { id: 'Dasbor', en: 'Dashboard' },
	About: { id: 'Tentang', en: 'About' },
	'Trade Operations': { id: 'Operasi Perdagangan', en: 'Trade Operations' },
	'Business Profile': { id: 'Profil Bisnis', en: 'Business Profile' },
	'Trade Projects': { id: 'Proyek Ekspor', en: 'Trade Projects' },
	Products: { id: 'Produk', en: 'Products' },
	'Export Analysis': { id: 'Analisis Ekspor', en: 'Export Analysis' },
	Markets: { id: 'Pasar', en: 'Markets' },
	Catalogs: { id: 'Katalog', en: 'Catalogs' },
	Commercial: { id: 'Komersial', en: 'Commercial' },
	Buyers: { id: 'Pembeli', en: 'Buyers' },
	'Buyer Requests': { id: 'Permintaan Pembeli', en: 'Buyer Requests' },
	Suppliers: { id: 'Pemasok', en: 'Suppliers' },
	Forwarders: { id: 'Forwarder', en: 'Forwarders' },
	RFQ: { id: 'RFQ', en: 'RFQ' },
	Quotations: { id: 'Penawaran Harga', en: 'Quotations' },
	Costing: { id: 'Kalkulasi Biaya', en: 'Costing' },
	Orders: { id: 'Pesanan', en: 'Orders' },
	Payments: { id: 'Pembayaran', en: 'Payments' },
	Fulfillment: { id: 'Pemenuhan', en: 'Fulfillment' },
	Compliance: { id: 'Kepatuhan', en: 'Compliance' },
	Tasks: { id: 'Tugas', en: 'Tasks' },
	Documents: { id: 'Dokumen', en: 'Documents' },
	Shipments: { id: 'Pengiriman', en: 'Shipments' },
	Insights: { id: 'Wawasan', en: 'Insights' },
	Analytics: { id: 'Analitik', en: 'Analytics' },
	Reports: { id: 'Laporan', en: 'Reports' },
	'Audit Log': { id: 'Log Audit', en: 'Audit Log' },
	Workspace: { id: 'Ruang Kerja', en: 'Workspace' },
	Team: { id: 'Tim', en: 'Team' },
	Calendar: { id: 'Kalender', en: 'Calendar' },
	Messages: { id: 'Pesan', en: 'Messages' },
	Chat: { id: 'Obrolan', en: 'Chat' },
	Files: { id: 'Berkas', en: 'Files' },
	Notifications: { id: 'Notifikasi', en: 'Notifications' },
	Automations: { id: 'Otomasi', en: 'Automations' },
	Integrations: { id: 'Integrasi', en: 'Integrations' },
	Templates: { id: 'Templat', en: 'Templates' },
	'Knowledge Base': { id: 'Basis Pengetahuan', en: 'Knowledge Base' },
	Educational: { id: 'Edukasi', en: 'Educational' },
	Marketing: { id: 'Pemasaran', en: 'Marketing' },
	Admin: { id: 'Admin', en: 'Admin' },
	Users: { id: 'Pengguna', en: 'Users' },
	Billing: { id: 'Penagihan', en: 'Billing' },
	Support: { id: 'Dukungan', en: 'Support' },
	'API Keys': { id: 'Kunci API', en: 'API Keys' },
	Settings: { id: 'Pengaturan', en: 'Settings' },

	// --- Header / chrome ---
	Search: { id: 'Cari', en: 'Search' },
	Activity: { id: 'Aktivitas', en: 'Activity' },
	'View projects': { id: 'Lihat proyek', en: 'View projects' },
	'New trade project': { id: 'Proyek baru', en: 'New trade project' },
	'New project': { id: 'Proyek baru', en: 'New project' },
	Logout: { id: 'Keluar', en: 'Logout' },
	Login: { id: 'Masuk', en: 'Login' },
	'Search everything': { id: 'Cari semua hal...', en: 'Search everything...' },

	// --- Dashboard ---
	'Checklist kesiapan ekspor': { id: 'Checklist kesiapan ekspor', en: 'Export readiness checklist' },
	'langkah selesai': { id: 'langkah selesai', en: 'steps done' },
	'Lengkapi profil bisnis': { id: 'Lengkapi profil bisnis', en: 'Complete business profile' },
	'Profil bisnis tersedia': { id: 'Profil bisnis tersedia', en: 'Business profile available' },
	'Tambahkan produk': { id: 'Tambahkan produk', en: 'Add products' },
	'produk terdaftar': { id: 'produk terdaftar', en: 'products registered' },
	'Jalankan AI enrichment': { id: 'Jalankan AI enrichment', en: 'Run AI enrichment' },
	'Enrich produk untuk HS & SKU': { id: 'Enrich produk untuk HS & SKU', en: 'Enrich products for HS & SKU' },
	'Buat export analysis': { id: 'Buat export analysis', en: 'Create export analysis' },
	'analisis pasar': { id: 'analisis pasar', en: 'market analyses' },
	'Publikasikan katalog': { id: 'Publikasikan katalog', en: 'Publish catalog' },
	'katalog dibuat': { id: 'katalog dibuat', en: 'catalogs created' },
	'Tambahkan profil & sertifikasi': { id: 'Tambahkan profil & sertifikasi', en: 'Add profile & certifications' },
	'Buat master data produk': { id: 'Buat master data produk', en: 'Create product master data' },
	'Analisis kepatuhan & pasar tujuan': { id: 'Analisis kepatuhan & pasar tujuan', en: 'Compliance & target market analysis' },
	'Bangun katalog buyer-facing': { id: 'Bangun katalog buyer-facing', en: 'Build buyer-facing catalog' },

	// --- Products ---
	'Add product': { id: 'Tambah produk', en: 'Add product' },
	'Export CSV': { id: 'Ekspor CSV', en: 'Export CSV' },
	'Excel (.xlsx)': { id: 'Excel (.xlsx)', en: 'Excel (.xlsx)' },
	'produk masih butuh AI enrichment': { id: 'produk masih butuh AI enrichment (HS code + SKU)', en: 'products still need AI enrichment (HS code + SKU)' },
	'Enrich semua': { id: 'Enrich semua', en: 'Enrich all' },
	'Enriching...': { id: 'Meng-enrich...', en: 'Enriching...' },
	'Hapus': { id: 'Hapus', en: 'Delete' },
	'Edit': { id: 'Edit', en: 'Edit' },

	// --- Costing ---
	'Create scenario': { id: 'Buat skenario', en: 'Create scenario' },
	'Compare': { id: 'Bandingkan', en: 'Compare' },
	'Membandingkan...': { id: 'Membandingkan...', en: 'Comparing...' },
	'Perbandingan': { id: 'Perbandingan', en: 'Comparison' },
	'skenario': { id: 'skenario', en: 'scenarios' },
	'Rekomendasi': { id: 'Rekomendasi', en: 'Recommendation' },
	'Tutup': { id: 'Tutup', en: 'Close' },
	'Skenario': { id: 'Skenario', en: 'Scenario' },
	'Negara tujuan': { id: 'Negara tujuan', en: 'Destination' },
	'Margin (%)': { id: 'Margin (%)', en: 'Margin (%)' },
	'Kurs (IDR/USD)': { id: 'Kurs (IDR/USD)', en: 'Rate (IDR/USD)' },
	'Status': { id: 'Status', en: 'Status' },

	// --- Trade projects ---
	'Search buyer, product, country...': { id: 'Cari pembeli, produk, negara...', en: 'Search buyer, product, country...' },
	'risk': { id: 'risiko', en: 'risk' },
	'Buyer': { id: 'Pembeli', en: 'Buyer' },
	'Destination': { id: 'Negara tujuan', en: 'Destination' },
	'Stage': { id: 'Tahap', en: 'Stage' },
	'Value': { id: 'Nilai', en: 'Value' }
};

let initial: Locale = 'id';
if (typeof window !== 'undefined') {
	try {
		const stored = window.localStorage.getItem('mauekspor.locale');
		if (stored === 'en' || stored === 'id') initial = stored;
	} catch {
		/* abaikan */
	}
}

export const i18n = $state<{ locale: Locale }>({ locale: initial });

/** Terjemahkan label (kunci kamus; kalau tidak ada, kembalikan aslinya). */
export function t(key: string): string {
	const entry = dictionary[key];
	if (!entry) return key;
	return entry[i18n.locale];
}

export function toggleLocale() {
	i18n.locale = i18n.locale === 'id' ? 'en' : 'id';
	if (typeof window !== 'undefined') {
		try {
			window.localStorage.setItem('mauekspor.locale', i18n.locale);
		} catch {
			/* abaikan */
		}
	}
}

export function nextLocale(): Locale {
	return i18n.locale === 'id' ? 'en' : 'id';
}
