// i18n ringan: kamus id/en + store lokal (localStorage) + fungsi t().
// Label default aplikasi memakai bahasa Inggris (navGroups, header),
// kamus memetakan label Inggris -> {id, en} sehingga ID = terjemahan.
export type Locale = 'id' | 'en';

type Entry = { id: string; en: string };

const dictionary: Record<string, Entry> = {
	'Pustaka bukti dan aset': { id: 'Pustaka bukti dan aset', en: 'Evidence and asset library' },
	'Kontrol file': { id: 'Kontrol file', en: 'File control' },
	'Jaga dokumen ekspor, bukti, sertifikat, dan aset tetap terorganisir.': { id: 'Jaga dokumen ekspor, bukti, sertifikat, dan aset tetap terorganisir.', en: 'Keep export documents, evidence, certificates, and assets organized.' },
	'Pusatkan file berdasarkan proyek, pemilik, jenis, status, dan tag operasional agar alur kerja kepatuhan dan dokumen tetap dapat ditelusuri.': { id: 'Pusatkan file berdasarkan proyek, pemilik, jenis, status, dan tag operasional agar alur kerja kepatuhan dan dokumen tetap dapat ditelusuri.', en: 'Centralize files by project, owner, type, status, and operational tags so compliance and document workflows stay traceable.' },
	'Mengunggah...': { id: 'Mengunggah...', en: 'Uploading...' },
	'Unggah file': { id: 'Unggah file', en: 'Upload file' },
	'Tinjauan': { id: 'Tinjauan', en: 'Review' },
	'File berhasil diunggah.': { id: 'File berhasil diunggah.', en: 'File uploaded.' },
	'tersimpan di backend.': { id: 'tersimpan di backend.', en: 'stored in the backend.' },
	'Dokumen': { id: 'Dokumen', en: 'Document' },
	'Sertifikat': { id: 'Sertifikat', en: 'Certificate' },
	'Gambar': { id: 'Gambar', en: 'Image' },
	'Laporan': { id: 'Laporan', en: 'Report' },
	'Bukti': { id: 'Bukti', en: 'Evidence' },
	'Terverifikasi': { id: 'Terverifikasi', en: 'Verified' },
	'Terunggah': { id: 'Terunggah', en: 'Uploaded' },
	'Menunggu': { id: 'Menunggu', en: 'Pending' },
	'Cari file, tag, pemilik...': { id: 'Cari file, tag, pemilik...', en: 'Search file, tag, owner...' },
	'Ukuran': { id: 'Ukuran', en: 'Size' },
	'Unduh': { id: 'Unduh', en: 'Download' },
	'Verifikasi file': { id: 'Verifikasi file', en: 'Verify file' },
	'Tidak ada file yang cocok dengan pencarian.': { id: 'Tidak ada file yang cocok dengan pencarian.', en: 'No file matched your search.' },
	'Gagal mengunggah file.': { id: 'Gagal mengunggah file.', en: 'Failed to upload file.' },
	'Gagal memverifikasi file.': { id: 'Gagal memverifikasi file.', en: 'Failed to verify file.' },
	'Menunggu balasan': { id: 'Menunggu balasan', en: 'Waiting Reply' },
	'Eskalasi': { id: 'Eskalasi', en: 'Escalated' },
	'Pusat alert': { id: 'Pusat alert', en: 'Alert center' },
	'Tangkap sinyal ekspor yang butuh tindakan sekarang.': { id: 'Tangkap sinyal ekspor yang butuh tindakan sekarang.', en: 'Catch the export signals that need action now.' },
	'Pantau blocker kritis, pengecualian pengiriman, peristiwa pembayaran, dan pembaruan buatan AI dari satu pusat notifikasi.': { id: 'Pantau blocker kritis, pengecualian pengiriman, peristiwa pembayaran, dan pembaruan buatan AI dari satu pusat notifikasi.', en: 'Monitor critical blockers, shipment exceptions, payment events, and AI-generated updates from one notification center.' },
	'Mark all read': { id: 'Tandai semua dibaca', en: 'Mark all read' },
	'Menandai...': { id: 'Menandai...', en: 'Marking...' },
	'Ditandai dibaca': { id: 'Ditandai dibaca', en: 'Marked read' },
	'Belum dibaca': { id: 'Belum dibaca', en: 'Unread' },
	'Dibaca': { id: 'Dibaca', en: 'Read' },
	'Diarsipkan': { id: 'Diarsipkan', en: 'Archived' },
	'Notifikasi ditandai dibaca.': { id: 'Notifikasi ditandai dibaca.', en: 'Notifications marked as read.' },
	'Notifikasi ditandai dibaca di backend.': { id: 'Notifikasi ditandai dibaca di backend.', en: 'Notifications marked as read in the backend.' },
	'Gagal menandai notifikasi.': { id: 'Gagal menandai notifikasi.', en: 'Failed to mark notification.' },
	'Gagal mengarsipkan notifikasi.': { id: 'Gagal mengarsipkan notifikasi.', en: 'Failed to archive notification.' },
	'Cari notifikasi, modul, tingkat keparahan...': { id: 'Cari notifikasi, modul, tingkat keparahan...', en: 'Search notification, module, severity...' },
	'Tidak ada notifikasi yang cocok dengan pencarian.': { id: 'Tidak ada notifikasi yang cocok dengan pencarian.', en: 'No notification matched your search.' },
	'Buka': { id: 'Buka', en: 'Open' },
	'Tandai dibaca': { id: 'Tandai dibaca', en: 'Mark as read' },
	'Arsip': { id: 'Arsip', en: 'Archive' },
	'Pusat komunikasi': { id: 'Pusat komunikasi', en: 'Communication center' },
	'Jaga percakapan dagang tetap terhubung dengan catatan ekspor.': { id: 'Jaga percakapan dagang tetap terhubung dengan catatan ekspor.', en: 'Keep trade conversations connected to the export record.' },
	'Lacak balasan buyer, penolakan bukti supplier, eskalasi internal, dan tindak lanjut order tanpa kehilangan konteks proyek.': { id: 'Lacak balasan buyer, penolakan bukti supplier, eskalasi internal, dan tindak lanjut order tanpa kehilangan konteks proyek.', en: 'Track buyer replies, supplier evidence requests, internal escalations, and order follow-ups without losing project context.' },
	'Kirim pesan': { id: 'Kirim pesan', en: 'Send message' },
	'Mengirim...': { id: 'Mengirim...', en: 'Sending...' },
	'Pesan terkirim': { id: 'Pesan terkirim', en: 'Message sent' },
	'Pesan terkirim.': { id: 'Pesan terkirim.', en: 'Message sent.' },
	'Pesan terkirim melalui backend.': { id: 'Pesan terkirim melalui backend.', en: 'Message sent through the backend.' },
	'Gagal mengirim pesan.': { id: 'Gagal mengirim pesan.', en: 'Failed to send message.' },
	'Menindaklanjuti order ekspor terbaru.': { id: 'Menindaklanjuti order ekspor terbaru.', en: 'Following up on the latest export order.' },
	'Selesaikan': { id: 'Selesaikan', en: 'Resolve' },
	'Tidak ada thread pesan yang cocok dengan pencarian.': { id: 'Tidak ada thread pesan yang cocok dengan pencarian.', en: 'No message thread matched your search.' },
	'Cari thread, pihak, partisipan...': { id: 'Cari thread, pihak, partisipan...', en: 'Search thread, party, participant...' },
	'Komunikasi buyer, supplier, dan internal': { id: 'Komunikasi buyer, supplier, dan internal', en: 'Buyer, supplier, and internal communication' },
	'Gagal menyelesaikan thread.': { id: 'Gagal menyelesaikan thread.', en: 'Failed to resolve thread.' },
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

	// --- Trade projects ---
	'Search buyer, product, country...': { id: 'Cari pembeli, produk, negara...', en: 'Search buyer, product, country...' },
	'risk': { id: 'risiko', en: 'risk' },
	'Buyer': { id: 'Pembeli', en: 'Buyer' },
	'Stage': { id: 'Tahap', en: 'Stage' },

	// --- Umum (filter & tombol lintas halaman) ---
	'All': { id: 'Semua', en: 'All' },
	'Updated': { id: 'Diperbarui', en: 'Updated' },
	'Category': { id: 'Kategori', en: 'Category' },
	'Scopes': { id: 'Cakupan', en: 'Scopes' },
	'Used by': { id: 'Dipakai oleh', en: 'Used by' },
	'Apply': { id: 'Terapkan', en: 'Apply' },
	'Applied': { id: 'Diterapkan', en: 'Applied' },
	'Last used': { id: 'Terakhir dipakai', en: 'Last used' },
	'Period': { id: 'Periode', en: 'Period' },
	'Due date': { id: 'Jatuh tempo', en: 'Due date' },
	'Monthly amount': { id: 'Biaya bulanan', en: 'Monthly amount' },
	'Open': { id: 'Terbuka', en: 'Open' },
	'Mark done': { id: 'Tandai selesai', en: 'Mark done' },
	'Resolve': { id: 'Selesaikan', en: 'Resolve' },
	'Resolved': { id: 'Selesai', en: 'Resolved' },
	'Revoke': { id: 'Cabut', en: 'Revoke' },
	'Revoking...': { id: 'Mencabut...', en: 'Revoking...' },
	'No template matched your search.': { id: 'Tidak ada templat yang cocok.', en: 'No template matched your search.' },
	'No calendar event matched your search.': { id: 'Tidak ada event kalender yang cocok.', en: 'No calendar event matched your search.' },
	'No article matched your search.': { id: 'Tidak ada artikel yang cocok.', en: 'No article matched your search.' },
	'No support ticket matched your search.': { id: 'Tidak ada tiket yang cocok.', en: 'No support ticket matched your search.' },
	'No API key matched your search.': { id: 'Tidak ada kunci API yang cocok.', en: 'No API key matched your search.' },

	// --- Templates ---
	'Reusable export assets': { id: 'Aset ekspor yang dapat dipakai ulang', en: 'Reusable export assets' },
	'Standardize export documents, emails, workflows, and catalogs.': { id: 'Standardisasi dokumen ekspor, email, alur kerja, dan katalog.', en: 'Standardize export documents, emails, workflows, and catalogs.' },
	'Use controlled templates to reduce manual work, keep evidence consistent, and speed up RFQ-to-shipment execution.': {
		id: 'Gunakan templat terkontrol untuk mengurangi pekerjaan manual, menjaga konsistensi bukti, dan mempercepat proses RFQ hingga pengiriman.',
		en: 'Use controlled templates to reduce manual work, keep evidence consistent, and speed up RFQ-to-shipment execution.'
	},
	'Use template': { id: 'Gunakan templat', en: 'Use template' },
	'Template used': { id: 'Templat terpakai', en: 'Template used' },
	'Ready': { id: 'Siap', en: 'Ready' },
	'Template applied.': { id: 'Templat diterapkan.', en: 'Template applied.' },
	'Search template, field, module...': { id: 'Cari templat, bidang, modul...', en: 'Search template, field, module...' },
	'Gagal menerapkan template.': { id: 'Gagal menerapkan template.', en: 'Failed to apply template.' },

	// --- Calendar ---
	'Trade milestone schedule': { id: 'Jadwal tonggak perdagangan', en: 'Trade milestone schedule' },
	'Keep every export deadline visible before it becomes a blocker.': {
		id: 'Pastikan setiap tenggat ekspor terlihat sebelum menjadi penghambat.',
		en: 'Keep every export deadline visible before it becomes a blocker.'
	},
	'Track compliance deadlines, shipment events, payment follow-ups, buyer meetings, and supplier evidence audits in one calendar view.': {
		id: 'Pantau tenggat kepatuhan, event pengiriman, tindak lanjut pembayaran, pertemuan pembeli, dan audit bukti pemasok dalam satu tampilan kalender.',
		en: 'Track compliance deadlines, shipment events, payment follow-ups, buyer meetings, and supplier evidence audits in one calendar view.'
	},
	'Create event': { id: 'Buat event', en: 'Create event' },
	'Creating...': { id: 'Membuat...', en: 'Creating...' },
	'Event created': { id: 'Event dibuat', en: 'Event created' },
	'Needs action': { id: 'Perlu tindakan', en: 'Needs action' },
	'Calendar event created.': { id: 'Event kalender dibuat.', en: 'Calendar event created.' },
	'Search event, owner, status...': { id: 'Cari event, pemilik, status...', en: 'Search event, owner, status...' },
	'Gagal membuat event kalender.': { id: 'Gagal membuat event kalender.', en: 'Failed to create calendar event.' },
	'Gagal menandai event selesai.': { id: 'Gagal menandai event selesai.', en: 'Failed to mark event done.' },

	// --- Knowledge Base ---
	'Export operating playbooks': { id: 'Panduan operasional ekspor', en: 'Export operating playbooks' },
	'Keep export know-how close to the workflow.': { id: 'Jaga pengetahuan ekspor tetap dekat dengan alur kerja.', en: 'Keep export know-how close to the workflow.' },
	'Publish practical playbooks for product readiness, HS review, Incoterms, shipment exceptions, finance, and platform usage.': {
		id: 'Terbitkan panduan praktis untuk kesiapan produk, tinjauan HS, Incoterms, pengecualian pengiriman, keuangan, dan penggunaan platform.',
		en: 'Publish practical playbooks for product readiness, HS review, Incoterms, shipment exceptions, finance, and platform usage.'
	},
	'Publish article': { id: 'Terbitkan artikel', en: 'Publish article' },
	'Article published': { id: 'Artikel diterbitkan', en: 'Article published' },
	'Article published.': { id: 'Artikel diterbitkan.', en: 'Article published.' },
	'Search article, step, category...': { id: 'Cari artikel, langkah, kategori...', en: 'Search article, step, category...' },
	'Gagal mempublikasikan artikel.': { id: 'Gagal mempublikasikan artikel.', en: 'Failed to publish article.' },

	// --- Support ---
	'Help desk and product support': { id: 'Help desk dan dukungan produk', en: 'Help desk and product support' },
	'Get help with export workflows, integrations, billing, and platform issues.': {
		id: 'Dapatkan bantuan untuk alur kerja ekspor, integrasi, penagihan, dan masalah platform.',
		en: 'Get help with export workflows, integrations, billing, and platform issues.'
	},
	'Track support tickets from creation to resolution while keeping each request tied to a clear category and owner.': {
		id: 'Pantau tiket dukungan dari pembuatan hingga penyelesaian, dengan setiap permintaan terhubung ke kategori dan pemilik yang jelas.',
		en: 'Track support tickets from creation to resolution while keeping each request tied to a clear category and owner.'
	},
	'Create ticket': { id: 'Buat tiket', en: 'Create ticket' },
	'Ticket created': { id: 'Tiket dibuat', en: 'Ticket created' },
	'Support ticket created.': { id: 'Tiket dukungan dibuat.', en: 'Support ticket created.' },
	'Search ticket, owner, issue...': { id: 'Cari tiket, pemilik, masalah...', en: 'Search ticket, owner, issue...' },
	'Gagal membuat tiket.': { id: 'Gagal membuat tiket.', en: 'Failed to create ticket.' },
	'Gagal menyelesaikan tiket.': { id: 'Gagal menyelesaikan tiket.', en: 'Failed to resolve ticket.' },

	// --- Billing ---
	'Subscription and usage': { id: 'Langganan dan pemakaian', en: 'Subscription and usage' },
	'plan for export operations.': { id: 'rencana untuk operasi ekspor.', en: 'plan for export operations.' },
	'Monitor subscription status, usage limits, invoice period, and upgrade needs for your MauEkspor workspace.': {
		id: 'Pantau status langganan, batas pemakaian, periode invoice, dan kebutuhan upgrade untuk workspace MauEkspor Anda.',
		en: 'Monitor subscription status, usage limits, invoice period, and upgrade needs for your MauEkspor workspace.'
	},
	'Change plan': { id: 'Ubah plan', en: 'Change plan' },
	'Plan updated': { id: 'Plan diperbarui', en: 'Plan updated' },
	'Download invoice': { id: 'Unduh invoice', en: 'Download invoice' },
	'Invoice ready': { id: 'Invoice siap', en: 'Invoice ready' },
	'Plan change simulated.': { id: 'Perubahan plan disimulasikan.', en: 'Plan change simulated.' },
	'Invoice download prepared.': { id: 'Unduhan invoice disiapkan.', en: 'Invoice download prepared.' },
	'Gagal mengubah plan.': { id: 'Gagal mengubah plan.', en: 'Failed to change plan.' },
	'Gagal mengunduh invoice.': { id: 'Gagal mengunduh invoice.', en: 'Failed to download invoice.' },

	// --- API Keys ---
	'Developer access controls': { id: 'Kontrol akses pengembang', en: 'Developer access controls' },
	'Manage API credentials for logistics, finance, and reporting integrations.': {
		id: 'Kelola kredensial API untuk integrasi logistik, keuangan, dan laporan.',
		en: 'Manage API credentials for logistics, finance, and reporting integrations.'
	},
	'Create scoped API keys, monitor usage, and revoke old credentials before they become integration or security risks.': {
		id: 'Buat kunci API ber-scope, pantau pemakaian, dan cabut kredensial lama sebelum menjadi risiko integrasi atau keamanan.',
		en: 'Create scoped API keys, monitor usage, and revoke old credentials before they become integration or security risks.'
	},
	'Create API key': { id: 'Buat kunci API', en: 'Create API key' },
	'Key created': { id: 'Kunci dibuat', en: 'Key created' },
	'API key created.': { id: 'Kunci API dibuat.', en: 'API key created.' },
	'Search key, scope, owner...': { id: 'Cari kunci, scope, pemilik...', en: 'Search key, scope, owner...' },
	'Gagal membuat API key.': { id: 'Gagal membuat API key.', en: 'Failed to create API key.' },
	'Gagal mencabut API key.': { id: 'Gagal mencabut API key.', en: 'Failed to revoke API key.' },

	// --- Analytics ---
	'Executive trade intelligence': { id: 'Intelijen perdagangan eksekutif', en: 'Executive trade intelligence' },
	'One executive view across pipeline, readiness, cash, risk, and delivery.': {
		id: 'Satu tampilan eksekutif untuk pipeline, kesiapan, kas, risiko, dan pengiriman.',
		en: 'One executive view across pipeline, readiness, cash, risk, and delivery.'
	},
	'Aggregate signals from projects, buyers, suppliers, compliance, payments, documents, and shipments to prioritize the next trade actions.': {
		id: 'Gabungkan sinyal dari proyek, pembeli, pemasok, kepatuhan, pembayaran, dokumen, dan pengiriman untuk memprioritaskan aksi perdagangan berikutnya.',
		en: 'Aggregate signals from projects, buyers, suppliers, compliance, payments, documents, and shipments to prioritize the next trade actions.'
	},
	'Refresh analytics': { id: 'Segarkan analitik', en: 'Refresh analytics' },
	'Refreshing...': { id: 'Menyegarkan...', en: 'Refreshing...' },
	'Analytics refreshed': { id: 'Analitik disegarkan', en: 'Analytics refreshed' },
	'Network': { id: 'Jaringan', en: 'Network' },
	'Analytics refreshed.': { id: 'Analitik disegarkan.', en: 'Analytics refreshed.' },
	'Commercial Snapshot': { id: 'Ringkasan Komersial', en: 'Commercial Snapshot' },
	'Project pipeline': { id: 'Pipeline proyek', en: 'Project pipeline' },
	'Open receivable': { id: 'Piutang terbuka', en: 'Open receivable' },
	'Active buyers': { id: 'Pembeli aktif', en: 'Active buyers' },
	'Verified suppliers': { id: 'Pemasok terverifikasi', en: 'Verified suppliers' },
	'Risk Concentration': { id: 'Konsentrasi Risiko', en: 'Risk Concentration' },
	'critical compliance blockers': { id: 'penghambat kepatuhan kritis', en: 'critical compliance blockers' },
	'shipment exception': { id: 'pengecualian pengiriman', en: 'shipment exception' },
	'high-risk payment': { id: 'pembayaran berisiko tinggi', en: 'high-risk payment' },
	'Readiness by Export Lane': { id: 'Kesiapan per Jalur Ekspor', en: 'Readiness by Export Lane' },
	'Trade lanes': { id: 'Jalur perdagangan', en: 'Trade lanes' },
	'% ready': { id: '% siap', en: '% ready' },

	// --- Pesan hasil aksi (ID default, EN = terjemahan) ---
	'Template diterapkan di backend.': { id: 'Template diterapkan di backend.', en: 'Template applied in backend.' },
	'Event tersimpan di backend.': { id: 'Event tersimpan di backend.', en: 'Event saved in backend.' },
	'Artikel dipublikasikan di backend.': { id: 'Artikel dipublikasikan di backend.', en: 'Article published in backend.' },
	'Tiket tersimpan di backend.': { id: 'Tiket tersimpan di backend.', en: 'Ticket saved in backend.' },
	'Perubahan plan tersimpan di backend.': { id: 'Perubahan plan tersimpan di backend.', en: 'Plan change saved in backend.' },
	'Invoice diekspor dari backend.': { id: 'Invoice diekspor dari backend.', en: 'Invoice exported from backend.' },
	'Data disegarkan dari backend.': { id: 'Data disegarkan dari backend.', en: 'Data refreshed from backend.' },
	'Key tersimpan di backend; simpan nilai rahasia di tempat aman.': {
		id: 'Key tersimpan di backend; simpan nilai rahasia di tempat aman.',
		en: 'Key saved in backend; keep the secret value in a safe place.'
	},

	// --- Buyers ---
	'Export buyer CRM': { id: 'CRM pembeli ekspor', en: 'Export buyer CRM' },
	'Buyer pipeline': { id: 'Pipeline pembeli', en: 'Buyer pipeline' },
	'Manage importer relationships from market signal to repeat order.': {
		id: 'Kelola hubungan importir dari sinyal pasar hingga pesanan berulang.',
		en: 'Manage importer relationships from market signal to repeat order.'
	},
	'Qualify buyers, track contact context, connect accounts to projects, and prioritize the next action that moves export deals forward.': {
		id: 'Kualifikasi pembeli, pantau konteks kontak, hubungkan akun ke proyek, dan prioritaskan aksi berikutnya yang mendorong deal ekspor.',
		en: 'Qualify buyers, track contact context, connect accounts to projects, and prioritize the next action that moves export deals forward.'
	},
	'Add buyer lead': { id: 'Tambah lead pembeli', en: 'Add buyer lead' },
	'Adding...': { id: 'Menambahkan...', en: 'Adding...' },
	'Lead captured': { id: 'Lead ditangkap', en: 'Lead captured' },
	'Buyer lead captured.': { id: 'Lead pembeli ditangkap.', en: 'Buyer lead captured.' },
	'Lead tersimpan di backend.': { id: 'Lead tersimpan di backend.', en: 'Lead saved in backend.' },
	'Search buyer, country, segment...': { id: 'Cari pembeli, negara, segmen...', en: 'Search buyer, country, segment...' },
	'Buyer accounts': { id: 'Akun pembeli', en: 'Buyer accounts' },
	'Annual pipeline': { id: 'Pipeline tahunan', en: 'Annual pipeline' },
	'Average fit': { id: 'Rata-rata kecocokan', en: 'Average fit' },
	'Pipeline': { id: 'Pipeline', en: 'Pipeline' },
	'Payment': { id: 'Pembayaran', en: 'Payment' },
	'Next step': { id: 'Langkah berikut', en: 'Next step' },
	'No buyer matched your search.': { id: 'Tidak ada pembeli yang cocok.', en: 'No buyer matched your search.' },
	'Gagal menambahkan buyer.': { id: 'Gagal menambahkan buyer.', en: 'Failed to add buyer.' },

	// --- Suppliers ---
	'Exporter and supplier network': { id: 'Jaringan eksportir dan pemasok', en: 'Exporter and supplier network' },
	'Supplier readiness': { id: 'Kesiapan pemasok', en: 'Supplier readiness' },
	'Verify supplier capability before RFQ matching and order execution.': {
		id: 'Verifikasi kapabilitas pemasok sebelum pencocokan RFQ dan eksekusi pesanan.',
		en: 'Verify supplier capability before RFQ matching and order execution.'
	},
	'Track capacity, certificates, quality signals, compliance evidence, and operational risks across the export supplier network.': {
		id: 'Pantau kapasitas, sertifikat, sinyal kualitas, bukti kepatuhan, dan risiko operasional di seluruh jaringan pemasok ekspor.',
		en: 'Track capacity, certificates, quality signals, compliance evidence, and operational risks across the export supplier network.'
	},
	'Request evidence': { id: 'Minta bukti', en: 'Request evidence' },
	'Requesting...': { id: 'Meminta...', en: 'Requesting...' },
	'Evidence requested': { id: 'Bukti diminta', en: 'Evidence requested' },
	'Permintaan bukti dikirim ke backend.': { id: 'Permintaan bukti dikirim ke backend.', en: 'Evidence request sent to backend.' },
	'Search supplier, product, location...': { id: 'Cari pemasok, produk, lokasi...', en: 'Search supplier, product, location...' },
	'Verified': { id: 'Terverifikasi', en: 'Verified' },
	'Avg capability': { id: 'Rata-rata kapabilitas', en: 'Avg capability' },
	'Capacity': { id: 'Kapasitas', en: 'Capacity' },
	'Lead time': { id: 'Waktu produksi', en: 'Lead time' },
	'Next audit': { id: 'Audit berikutnya', en: 'Next audit' },
	'No supplier matched your search.': { id: 'Tidak ada pemasok yang cocok.', en: 'No supplier matched your search.' },
	'Gagal meminta bukti kepatuhan.': { id: 'Gagal meminta bukti kepatuhan.', en: 'Failed to request compliance evidence.' },

	// --- Orders ---
	'Accepted quotation to execution': { id: 'Dari quotation diterima hingga eksekusi', en: 'Accepted quotation to execution' },
	'Sales order control': { id: 'Kontrol sales order', en: 'Sales order control' },
	'Convert accepted quotations into executable export orders.': {
		id: 'Ubah quotation yang diterima menjadi pesanan ekspor yang dapat dieksekusi.',
		en: 'Convert accepted quotations into executable export orders.'
	},
	'Track payment terms, delivery windows, order lines, document readiness, and shipment handoff from one operational view.': {
		id: 'Pantau syarat pembayaran, jendela pengiriman, baris pesanan, kesiapan dokumen, dan serah terima pengiriman dari satu tampilan operasional.',
		en: 'Track payment terms, delivery windows, order lines, document readiness, and shipment handoff from one operational view.'
	},
	'Create order': { id: 'Buat pesanan', en: 'Create order' },
	'Order draft created': { id: 'Draf pesanan dibuat', en: 'Order draft created' },
	'Order draft ready.': { id: 'Draf pesanan siap.', en: 'Order draft ready.' },
	'Order tersimpan di backend.': { id: 'Order tersimpan di backend.', en: 'Order saved in backend.' },
	'Search order, buyer, supplier...': { id: 'Cari pesanan, pembeli, pemasok...', en: 'Search order, buyer, supplier...' },
	'Total value': { id: 'Total nilai', en: 'Total value' },
	'Value': { id: 'Nilai', en: 'Value' },
	'Incoterm': { id: 'Incoterm', en: 'Incoterm' },
	'Delivery': { id: 'Pengiriman', en: 'Delivery' },
	'No order matched your search.': { id: 'Tidak ada pesanan yang cocok.', en: 'No order matched your search.' },
	'Gagal membuat order.': { id: 'Gagal membuat order.', en: 'Failed to create order.' },

	// --- Quotations ---
	'Commercial offer management': { id: 'Manajemen penawaran komersial', en: 'Commercial offer management' },
	'Incoterm clarity': { id: 'Kejelasan Incoterm', en: 'Incoterm clarity' },
	'Create traceable export quotations with cost and validity control.': {
		id: 'Buat quotation ekspor yang dapat dilacak dengan kendali biaya dan masa berlaku.',
		en: 'Create traceable export quotations with cost and validity control.'
	},
	'Separate EXW, FOB, CIF, landed-cost assumptions, freight validity, currency, named place, margin, and revision history.': {
		id: 'Pisahkan asumsi EXW, FOB, CIF, landed cost, masa berlaku freight, mata uang, tempat tujuan, margin, dan riwayat revisi.',
		en: 'Separate EXW, FOB, CIF, landed-cost assumptions, freight validity, currency, named place, margin, and revision history.'
	},
	'Create quotation': { id: 'Buat quotation', en: 'Create quotation' },
	'Quotation draft created': { id: 'Draf quotation dibuat', en: 'Quotation draft created' },
	'Quotation draft ready.': { id: 'Draf quotation siap.', en: 'Quotation draft ready.' },
	'Quotation tersimpan di backend.': { id: 'Quotation tersimpan di backend.', en: 'Quotation saved in backend.' },
	'Search quotation, buyer, incoterm...': { id: 'Cari quotation, pembeli, incoterm...', en: 'Search quotation, buyer, incoterm...' },
	'Valid until': { id: 'Berlaku hingga', en: 'Valid until' },
	'No quotation matched your search.': { id: 'Tidak ada quotation yang cocok.', en: 'No quotation matched your search.' },
	'Gagal membuat quotation.': { id: 'Gagal membuat quotation.', en: 'Failed to create quotation.' },

	// --- Shipments ---
	'Logistics milestone tracking': { id: 'Pelacakan tonggak logistik', en: 'Logistics milestone tracking' },
	'Forwarder operations': { id: 'Operasi forwarder', en: 'Forwarder operations' },
	'Track bookings, customs, cargo movement, and delivery exceptions.': {
		id: 'Pantau booking, bea cukai, pergerakan kargo, dan pengecualian pengiriman.',
		en: 'Track bookings, customs, cargo movement, and delivery exceptions.'
	},
	'Coordinate cargo readiness, pickup, warehouse receipt, customs clearance, vessel departure, arrival, destination processing, and issue ownership.': {
		id: 'Koordinasi kesiapan kargo, pickup, tanda terima gudang, bea cukai, keberangkatan kapal, kedatangan, pemrosesan tujuan, dan kepemilikan masalah.',
		en: 'Coordinate cargo readiness, pickup, warehouse receipt, customs clearance, vessel departure, arrival, destination processing, and issue ownership.'
	},
	'Request freight quote': { id: 'Minta kuotasi freight', en: 'Request freight quote' },
	'Requesting quote...': { id: 'Meminta kuotasi...', en: 'Requesting quote...' },
	'Freight RFQ drafted': { id: 'RFQ freight dibuat', en: 'Freight RFQ drafted' },
	'Avg progress': { id: 'Rata-rata progres', en: 'Avg progress' },
	'Freight RFQ draft ready.': { id: 'Draf RFQ freight siap.', en: 'Freight RFQ draft ready.' },
	'Kuotasi diminta ke backend.': { id: 'Kuotasi diminta ke backend.', en: 'Freight quote requested in backend.' },
	'Search route, forwarder, booking...': { id: 'Cari rute, forwarder, booking...', en: 'Search route, forwarder, booking...' },
	'Active shipments': { id: 'Pengiriman aktif', en: 'Active shipments' },
	'Exceptions': { id: 'Pengecualian', en: 'Exceptions' },
	'Average progress': { id: 'Rata-rata progres', en: 'Average progress' },
	'Forwarder': { id: 'Forwarder', en: 'Forwarder' },
	'Mode': { id: 'Moda', en: 'Mode' },
	'Booking': { id: 'Booking', en: 'Booking' },
	'ETA': { id: 'ETA', en: 'ETA' },
	'No shipment matched your search.': { id: 'Tidak ada pengiriman yang cocok.', en: 'No shipment matched your search.' },
	'Gagal meminta kuotasi pengiriman.': { id: 'Gagal meminta kuotasi pengiriman.', en: 'Failed to request freight quote.' },

	// --- Payments ---
	'Export receivables and settlement': { id: 'Piutang dan penyelesaian ekspor', en: 'Export receivables and settlement' },
	'Cashflow control': { id: 'Kontrol arus kas', en: 'Cashflow control' },
	'Track deposits, LC milestones, and export receivables before shipment release.': {
		id: 'Pantau deposit, tonggak LC, dan piutang ekspor sebelum pengiriman dilepas.',
		en: 'Track deposits, LC milestones, and export receivables before shipment release.'
	},
	'Keep payment terms connected to orders, document release, and buyer risk so operations never ships without commercial control.': {
		id: 'Jaga syarat pembayaran terhubung dengan pesanan, pelepasan dokumen, dan risiko pembeli sehingga operasi tidak pernah mengirim tanpa kendali komersial.',
		en: 'Keep payment terms connected to orders, document release, and buyer risk so operations never ships without commercial control.'
	},
	'Send reminders': { id: 'Kirim pengingat', en: 'Send reminders' },
	'Sending...': { id: 'Mengirim...', en: 'Sending...' },
	'Reminder sent': { id: 'Pengingat terkirim', en: 'Reminder sent' },
	'Risk': { id: 'Risiko', en: 'Risk' },
	'Payment reminders sent.': { id: 'Pengingat pembayaran terkirim.', en: 'Payment reminders sent.' },
	'Pengingat dikirim melalui backend.': { id: 'Pengingat dikirim melalui backend.', en: 'Reminders sent through backend.' },
	'Search payment, buyer, order...': { id: 'Cari pembayaran, pembeli, pesanan...', en: 'Search payment, buyer, order...' },
	'Collected': { id: 'Terkumpul', en: 'Collected' },
	'Receivable': { id: 'Piutang', en: 'Receivable' },
	'Tracked payments': { id: 'Pembayaran terpantau', en: 'Tracked payments' },
	'Total': { id: 'Total', en: 'Total' },
	'Paid': { id: 'Terbayar', en: 'Paid' },
	'Method': { id: 'Metode', en: 'Method' },
	'No payment matched your search.': { id: 'Tidak ada pembayaran yang cocok.', en: 'No payment matched your search.' },
	'Gagal mengirim pengingat pembayaran.': { id: 'Gagal mengirim pengingat pembayaran.', en: 'Failed to send payment reminder.' },

	// --- Compliance ---
	'Evidence-based export readiness': { id: 'Kesiapan ekspor berbasis bukti', en: 'Evidence-based export readiness' },
	'Source-backed workflow': { id: 'Alur kerja berbasis sumber', en: 'Source-backed workflow' },
	'Turn regulatory gaps into verified action items.': {
		id: 'Ubah celah regulasi menjadi item aksi terverifikasi.',
		en: 'Turn regulatory gaps into verified action items.'
	},
	'Track source, severity, owner, evidence, human verification, and confidence for each export requirement before documents or quotation are finalized.': {
		id: 'Pantau sumber, tingkat keparahan, pemilik, bukti, verifikasi manusia, dan tingkat keyakinan untuk setiap persyaratan ekspor sebelum dokumen atau quotation difinalisasi.',
		en: 'Track source, severity, owner, evidence, human verification, and confidence for each export requirement before documents or quotation are finalized.'
	},
	'Critical': { id: 'Kritis', en: 'Critical' },
	'Search requirement, source, project...': { id: 'Cari persyaratan, sumber, proyek...', en: 'Search requirement, source, project...' },
	'Owner': { id: 'Pemilik', en: 'Owner' },
	'Due': { id: 'Jatuh tempo', en: 'Due' },
	'Confidence': { id: 'Tingkat keyakinan', en: 'Confidence' },
	'Source: {item.source}': { id: 'Sumber: {item.source}', en: 'Source: {item.source}' },
	'No compliance requirement matched your search.': { id: 'Tidak ada persyaratan kepatuhan yang cocok.', en: 'No compliance requirement matched your search.' },

	// --- Documents ---
	'Trade document center': { id: 'Pusat dokumen perdagangan', en: 'Trade document center' },
	'Document control': { id: 'Kontrol dokumen', en: 'Document control' },
	'Generate, validate, approve, and version trade documents.': {
		id: 'Buat, validasi, setujui, dan versikan dokumen perdagangan.',
		en: 'Generate, validate, approve, and version trade documents.'
	},
	'Keep invoice, packing list, certificate of origin, lab reports, insurance, and shipment documents consistent with product, quotation, and shipment data.': {
		id: 'Jaga invoice, packing list, sertifikat asal, laporan lab, asuransi, dan dokumen pengiriman konsisten dengan data produk, quotation, dan pengiriman.',
		en: 'Keep invoice, packing list, certificate of origin, lab reports, insurance, and shipment documents consistent with product, quotation, and shipment data.'
	},
	'Generate document': { id: 'Buat dokumen', en: 'Generate document' },
	'Generating...': { id: 'Membuat...', en: 'Generating...' },
	'Document generated': { id: 'Dokumen dibuat', en: 'Document generated' },
	'Avg validation': { id: 'Rata-rata validasi', en: 'Avg validation' },
	'Generated draft ready.': { id: 'Draf hasil generate siap.', en: 'Generated draft ready.' },
	'Dokumen berhasil dibuat di backend.': { id: 'Dokumen berhasil dibuat di backend.', en: 'Document created in backend.' },
	'Search document, owner, project...': { id: 'Cari dokumen, pemilik, proyek...', en: 'Search document, owner, project...' },
	'Total documents': { id: 'Total dokumen', en: 'Total documents' },
	'Need attention': { id: 'Perlu perhatian', en: 'Need attention' },
	'Validation score': { id: 'Skor validasi', en: 'Validation score' },
	'Version': { id: 'Versi', en: 'Version' },
	'ID': { id: 'ID', en: 'ID' },
	'No document matched your search.': { id: 'Tidak ada dokumen yang cocok.', en: 'No document matched your search.' },
	'Gagal generate dokumen.': { id: 'Gagal generate dokumen.', en: 'Failed to generate document.' },

	// --- Tasks ---
	'Operational work queue': { id: 'Antrean kerja operasional', en: 'Operational work queue' },
	'Next actions': { id: 'Aksi berikutnya', en: 'Next actions' },
	'Prioritize the work that unblocks export execution.': {
		id: 'Prioritaskan pekerjaan yang membuka hambatan eksekusi ekspor.',
		en: 'Prioritize the work that unblocks export execution.'
	},
	'Convert compliance gaps, supplier evidence, payments, documents, and shipment exceptions into accountable operational tasks.': {
		id: 'Ubah celah kepatuhan, bukti pemasok, pembayaran, dokumen, dan pengecualian pengiriman menjadi tugas operasional yang dapat dipertanggungjawabkan.',
		en: 'Convert compliance gaps, supplier evidence, payments, documents, and shipment exceptions into accountable operational tasks.'
	},
	'Create task': { id: 'Buat tugas', en: 'Create task' },
	'Task created': { id: 'Tugas dibuat', en: 'Task created' },
	'Blocked': { id: 'Terhambat', en: 'Blocked' },
	'Task created.': { id: 'Tugas dibuat.', en: 'Task created.' },
	'Tugas dibuat di backend.': { id: 'Tugas dibuat di backend.', en: 'Task created in backend.' },
	'Search task, module, owner...': { id: 'Cari tugas, modul, pemilik...', en: 'Search task, module, owner...' },
	'Total tasks': { id: 'Total tugas', en: 'Total tasks' },
	'Checklist': { id: 'Ceklis', en: 'Checklist' },
	'Priority': { id: 'Prioritas', en: 'Priority' },
	'No task matched your search.': { id: 'Tidak ada tugas yang cocok.', en: 'No task matched your search.' },
	'Gagal membuat tugas.': { id: 'Gagal membuat tugas.', en: 'Failed to create task.' },

	// --- Markets ---
	'Market intelligence and country selection': { id: 'Intelijen pasar dan pemilihan negara', en: 'Market intelligence and country selection' },
	'Country opportunity radar': { id: 'Radar peluang negara', en: 'Country opportunity radar' },
	'Prioritize export markets before committing compliance and logistics cost.': {
		id: 'Prioritaskan pasar ekspor sebelum mengeluarkan biaya kepatuhan dan logistik.',
		en: 'Prioritize export markets before committing compliance and logistics cost.'
	},
	'Compare market attractiveness, compliance complexity, logistics feasibility, margin potential, and source-backed risks by product.': {
		id: 'Bandingkan daya tarik pasar, kompleksitas kepatuhan, kelayakan logistik, potensi margin, dan risiko berbasis sumber per produk.',
		en: 'Compare market attractiveness, compliance complexity, logistics feasibility, margin potential, and source-backed risks by product.'
	},
	'Generate insight': { id: 'Generate insight', en: 'Generate insight' },
	'Insight generated': { id: 'Insight dibuat', en: 'Insight generated' },
	'Avg score': { id: 'Rata-rata skor', en: 'Avg score' },
	'Market insight draft ready.': { id: 'Draf insight pasar siap.', en: 'Market insight draft ready.' },
	'Insight dibuat di backend.': { id: 'Insight dibuat di backend.', en: 'Insight created in backend.' },
	'Search country, product, strategy...': { id: 'Cari negara, produk, strategi...', en: 'Search country, product, strategy...' },
	'Markets tracked': { id: 'Pasar terpantau', en: 'Markets tracked' },
	'Recommended': { id: 'Direkomendasikan', en: 'Recommended' },
	'Average score': { id: 'Rata-rata skor', en: 'Average score' },
	'Logistics': { id: 'Logistik', en: 'Logistics' },
	'Margin': { id: 'Margin', en: 'Margin' },
	'Growth': { id: 'Pertumbuhan', en: 'Growth' },
	'No market insight matched your search.': { id: 'Tidak ada insight pasar yang cocok.', en: 'No market insight matched your search.' },
	'Gagal generate insight pasar.': { id: 'Gagal generate insight pasar.', en: 'Failed to generate market insight.' },

	// --- RFQ ---
	'Buyer demand workspace': { id: 'Ruang kerja permintaan pembeli', en: 'Buyer demand workspace' },
	'Smart matching': { id: 'Pencocokan cerdas', en: 'Smart matching' },
	'Match buyer requirements with verified exporter capabilities.': {
		id: 'Cocokkan kebutuhan pembeli dengan kapabilitas eksportir terverifikasi.',
		en: 'Match buyer requirements with verified exporter capabilities.'
	},
	'Manage RFQs, destination terms, required certificates, deadlines, and transparent supplier matching explanations.': {
		id: 'Kelola RFQ, ketentuan tujuan, sertifikat yang diperlukan, tenggat, dan penjelasan pencocokan pemasok yang transparan.',
		en: 'Manage RFQs, destination terms, required certificates, deadlines, and transparent supplier matching explanations.'
	},
	'Create RFQ': { id: 'Buat RFQ', en: 'Create RFQ' },
	'RFQ draft created': { id: 'Draf RFQ dibuat', en: 'RFQ draft created' },
	'Avg match': { id: 'Rata-rata kecocokan', en: 'Avg match' },
	'RFQ draft ready.': { id: 'Draf RFQ siap.', en: 'RFQ draft ready.' },
	'RFQ tersimpan di backend.': { id: 'RFQ tersimpan di backend.', en: 'RFQ saved in backend.' },
	'Search buyer, product, destination...': { id: 'Cari pembeli, produk, tujuan...', en: 'Search buyer, product, destination...' },
	'Quantity': { id: 'Jumlah', en: 'Quantity' },
	'Deadline': { id: 'Tenggat', en: 'Deadline' },
	'No RFQ matched your search.': { id: 'Tidak ada RFQ yang cocok.', en: 'No RFQ matched your search.' },
	'Gagal membuat RFQ.': { id: 'Gagal membuat RFQ.', en: 'Failed to create RFQ.' },

	// --- Catalogs ---
	'Buyer-facing export catalog': { id: 'Katalog ekspor untuk pembeli', en: 'Buyer-facing export catalog' },
	'Commercial presentation': { id: 'Presentasi komersial', en: 'Commercial presentation' },
	'Turn verified product data into buyer-ready export catalogs.': {
		id: 'Ubah data produk terverifikasi menjadi katalog ekspor siap-pembeli.',
		en: 'Turn verified product data into buyer-ready export catalogs.'
	},
	'Package product specifications, MOQ, lead time, Incoterms, certificates, images, and AI-assisted B2B descriptions for buyer discovery and RFQ conversion.': {
		id: 'Kemas spesifikasi produk, MOQ, lead time, Incoterms, sertifikat, gambar, dan deskripsi B2B berbantuan AI untuk penemuan pembeli dan konversi RFQ.',
		en: 'Package product specifications, MOQ, lead time, Incoterms, certificates, images, and AI-assisted B2B descriptions for buyer discovery and RFQ conversion.'
	},
	'Create catalog': { id: 'Buat katalog', en: 'Create catalog' },
	'Published': { id: 'Diterbitkan', en: 'Published' },
	'Readiness': { id: 'Kesiapan', en: 'Readiness' },
	'Search catalog, market, product...': { id: 'Cari katalog, pasar, produk...', en: 'Search catalog, market, product...' },
	'Market': { id: 'Pasar', en: 'Market' },
	'MOQ': { id: 'MOQ', en: 'MOQ' },
	'Images': { id: 'Gambar', en: 'Images' },
	'No catalog matched your search.': { id: 'Tidak ada katalog yang cocok.', en: 'No catalog matched your search.' },
	'Gagal menghapus katalog.': { id: 'Gagal menghapus katalog.', en: 'Failed to delete catalog.' },
	'Hapus katalog "': { id: 'Hapus katalog "', en: 'Delete catalog "' },

	// --- Forwarders ---
	'Freight partner network': { id: 'Jaringan mitra freight', en: 'Freight partner network' },
	'Logistics network': { id: 'Jaringan logistik', en: 'Logistics network' },
	'Verified freight partners for your export lanes.': {
		id: 'Mitra freight terverifikasi untuk jalur ekspor Anda.',
		en: 'Verified freight partners for your export lanes.'
	},
	'Compare on-time rates, quote speed, and covered lanes, then request a quote for active shipments.': {
		id: 'Bandingkan tingkat on-time, kecepatan kuotasi, dan jalur yang dilayani, lalu minta kuotasi untuk pengiriman aktif.',
		en: 'Compare on-time rates, quote speed, and covered lanes, then request a quote for active shipments.'
	},
	'Search forwarder, lane, coverage...': { id: 'Cari forwarder, jalur, cakupan...', en: 'Search forwarder, lane, coverage...' },
	'On-time': { id: 'Tepat waktu', en: 'On-time' },
	'Quote speed': { id: 'Kecepatan kuotasi', en: 'Quote speed' },
	'Lanes': { id: 'Jalur', en: 'Lanes' },
	'No forwarder matched your filter.': { id: 'Tidak ada forwarder yang cocok.', en: 'No forwarder matched your filter.' },

	// --- Buyer Requests ---
	'Inbound demand': { id: 'Permintaan masuk', en: 'Inbound demand' },
	'Inbound lead flow': { id: 'Aliran lead masuk', en: 'Inbound lead flow' },
	'Act on buyer demand before it cools.': {
		id: 'Tanggapi permintaan pembeli sebelum mendingin.',
		en: 'Act on buyer demand before it cools.'
	},
	'Review request subject, destination, quantity, deadline, and requirements, then match products or send a quotation.': {
		id: 'Tinjau subjek permintaan, tujuan, jumlah, tenggat, dan persyaratan, lalu cocokkan produk atau kirim quotation.',
		en: 'Review request subject, destination, quantity, deadline, and requirements, then match products or send a quotation.'
	},
	'Log buyer request': { id: 'Catat permintaan pembeli', en: 'Log buyer request' },
	'new': { id: 'baru', en: 'new' },
	'Search subject, destination, product...': { id: 'Cari subjek, tujuan, produk...', en: 'Search subject, destination, product...' },
	'wants': { id: 'ingin', en: 'wants' },
	'for': { id: 'untuk', en: 'for' },
	'Product': { id: 'Produk', en: 'Product' },
	'Destination': { id: 'Negara tujuan', en: 'Destination' },
	'No buyer request matched your filter.': { id: 'Tidak ada permintaan pembeli yang cocok.', en: 'No buyer request matched your filter.' },

	// --- Team ---
	'Roles and workspace access': { id: 'Peran dan akses ruang kerja', en: 'Roles and workspace access' },
	'Access control': { id: 'Kontrol akses', en: 'Access control' },
	'Coordinate export operations with clear roles, permissions, and workload.': {
		id: 'Koordinasi operasi ekspor dengan peran, izin, dan beban kerja yang jelas.',
		en: 'Coordinate export operations with clear roles, permissions, and workload.'
	},
	'Manage team members across operations, compliance, finance, and sales while keeping access scoped to each trade workflow.': {
		id: 'Kelola anggota tim di operasi, kepatuhan, keuangan, dan penjualan dengan akses terbatas pada setiap alur kerja perdagangan.',
		en: 'Manage team members across operations, compliance, finance, and sales while keeping access scoped to each trade workflow.'
	},
	'Invite member': { id: 'Undang anggota', en: 'Invite member' },
	'Inviting...': { id: 'Mengundang...', en: 'Inviting...' },
	'Invite sent': { id: 'Undangan terkirim', en: 'Invite sent' },
	'Team invitation sent.': { id: 'Undangan tim terkirim.', en: 'Team invitation sent.' },
	'Undangan terkirim melalui backend.': { id: 'Undangan terkirim melalui backend.', en: 'Invitation sent through backend.' },
	'Search member, role, permission...': { id: 'Cari anggota, peran, izin...', en: 'Search member, role, permission...' },
	'Members': { id: 'Anggota', en: 'Members' },
	'Avg workload': { id: 'Rata-rata beban kerja', en: 'Avg workload' },
	'Last active': { id: 'Aktif terakhir', en: 'Last active' },
	'Workload': { id: 'Beban kerja', en: 'Workload' },
	'Update role': { id: 'Perbarui peran', en: 'Update role' },
	'Updating...': { id: 'Memperbarui...', en: 'Updating...' },
	'No team member matched your search.': { id: 'Tidak ada anggota tim yang cocok.', en: 'No team member matched your search.' },
	'Gagal mengirim undangan.': { id: 'Gagal mengirim undangan.', en: 'Failed to send invitation.' },
	'Gagal memperbarui peran.': { id: 'Gagal memperbarui peran.', en: 'Failed to update role.' },

	// --- Audit Log ---
	'Traceability and governance': { id: 'Ketertelusuran dan tata kelola', en: 'Traceability and governance' },
	'Governance': { id: 'Tata kelola', en: 'Governance' },
	'Trace important operational and AI-assisted export actions.': {
		id: 'Telusuri aksi ekspor operasional dan berbantuan AI yang penting.',
		en: 'Trace important operational and AI-assisted export actions.'
	},
	'Keep a searchable event trail for compliance, document approvals, supplier risk, payment reminders, and AI-generated insights.': {
		id: 'Simpan jejak event yang dapat dicari untuk kepatuhan, persetujuan dokumen, risiko pemasok, pengingat pembayaran, dan insight hasil AI.',
		en: 'Keep a searchable event trail for compliance, document approvals, supplier risk, payment reminders, and AI-generated insights.'
	},
	'Export audit trail': { id: 'Ekspor audit trail', en: 'Export audit trail' },
	'Exporting...': { id: 'Mengekspor...', en: 'Exporting...' },
	'Audit exported': { id: 'Audit diekspor', en: 'Audit exported' },
	'Download CSV': { id: 'Unduh CSV', en: 'Download CSV' },
	'Events': { id: 'Event', en: 'Events' },
	'Audit export prepared.': { id: 'Ekspor audit disiapkan.', en: 'Audit export prepared.' },
	'Export dijalankan di backend.': { id: 'Export dijalankan di backend.', en: 'Export ran in backend.' },
	'Search actor, module, entity...': { id: 'Cari aktor, modul, entitas...', en: 'Search actor, module, entity...' },
	'No audit event matched your search.': { id: 'Tidak ada event audit yang cocok.', en: 'No audit event matched your search.' },
	'Gagal mengekspor audit trail.': { id: 'Gagal mengekspor audit trail.', en: 'Failed to export audit trail.' },

	// --- Users ---
	'Account management': { id: 'Manajemen akun', en: 'Account management' },
	'Admin only': { id: 'Khusus admin', en: 'Admin only' },
	'Manage the accounts in your export workspace.': {
		id: 'Kelola akun di workspace ekspor Anda.',
		en: 'Manage the accounts in your export workspace.'
	},
	'Filter by role, search by email or full name, and open a user to inspect account detail.': {
		id: 'Filter berdasarkan peran, cari berdasarkan email atau nama lengkap, dan buka pengguna untuk memeriksa detail akun.',
		en: 'Filter by role, search by email or full name, and open a user to inspect account detail.'
	},
	'Total users': { id: 'Total pengguna', en: 'Total users' },
	'Search email or name...': { id: 'Cari email atau nama...', en: 'Search email or name...' },
	'User': { id: 'Pengguna', en: 'User' },
	'Role': { id: 'Peran', en: 'Role' },
	'Status': { id: 'Status', en: 'Status' },
	'Created': { id: 'Dibuat', en: 'Created' },
	'Memuat...': { id: 'Memuat...', en: 'Loading...' },
	'No user matched your filter.': { id: 'Tidak ada pengguna yang cocok.', en: 'No user matched your filter.' },
	'Gagal menghapus akun.': { id: 'Gagal menghapus akun.', en: 'Failed to delete account.' },
	'Hapus akun "': { id: 'Hapus akun "', en: 'Delete account "' },
	'beserta data terkaitnya?': { id: 'beserta data terkaitnya?', en: 'and its related data?' },
	'Sebelumnya': { id: 'Sebelumnya', en: 'Previous' },
	'Berikutnya': { id: 'Berikutnya', en: 'Next' }
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
