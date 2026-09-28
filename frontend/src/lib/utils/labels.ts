import { t } from '$lib/i18n.svelte';

/**
 * Penerjemah label domain (status, peran, prioritas, severity).
 *
 * Sebelumnya ~40 halaman menampilkan nilai mentah berbahasa Inggris dari
 * backend (mis. "In Progress", "Operations", "High"). Helper ini memusatkan
 * pemetaan agar konsisten di seluruh aplikasi dan mudah dilokalkan.
 */
const LABELS: Record<string, [string, string]> = {
	// Status umum
	Active: ['Aktif', 'Active'],
	Suspended: ['Ditangguhkan', 'Suspended'],
	Invited: ['Diundang', 'Invited'],
	Pending: ['Menunggu', 'Pending'],
	Open: ['Terbuka', 'Open'],
	'In Progress': ['Sedang Dikerjakan', 'In Progress'],
	Done: ['Selesai', 'Done'],
	Complete: ['Selesai', 'Complete'],
	Completed: ['Selesai', 'Completed'],
	Resolved: ['Terselesaikan', 'Resolved'],
	Closed: ['Ditutup', 'Closed'],
	Archived: ['Diarsipkan', 'Archived'],
	Read: ['Dibaca', 'Read'],
	Unread: ['Belum dibaca', 'Unread'],
	Blocked: ['Terhambat', 'Blocked'],
	Cancelled: ['Dibatalkan', 'Cancelled'],
	Approved: ['Disetujui', 'Approved'],
	Draft: ['Draf', 'Draft'],
	Published: ['Dipublikasikan', 'Published'],
	Ready: ['Siap', 'Ready'],
	Verified: ['Terverifikasi', 'Verified'],
	'Needs Review': ['Perlu Ditinjau', 'Needs Review'],
	Failed: ['Gagal', 'Failed'],
	// Status alur ekspor
	Confirmed: ['Terkonfirmasi', 'Confirmed'],
	'Document Prep': ['Persiapan Dokumen', 'Document Prep'],
	'In Shipment': ['Dalam Pengiriman', 'In Shipment'],
	'Booking Requested': ['Booking Diminta', 'Booking Requested'],
	'Customs Submitted': ['Diajukan ke Bea Cukai', 'Customs Submitted'],
	Loaded: ['Dimuat', 'Loaded'],
	Exception: ['Pengecualian', 'Exception'],
	'Deposit Paid': ['Deposit Dibayar', 'Deposit Paid'],
	'Due Soon': ['Segera Jatuh Tempo', 'Due Soon'],
	Overdue: ['Jatuh Tempo', 'Overdue'],
	Settled: ['Lunas', 'Settled'],
	'Evidence Uploaded': ['Bukti Diunggah', 'Evidence Uploaded'],
	'Revision Needed': ['Perlu Revisi', 'Revision Needed'],
	Accepted: ['Diterima', 'Accepted'],
	Matching: ['Dicocokkan', 'Matching'],
	Matched: ['Cocok', 'Matched'],
	Negotiating: ['Negosiasi', 'Negotiating'],
	'At Risk': ['Berisiko', 'At Risk'],
	Qualified: ['Terkualifikasi', 'Qualified'],
	Lead: ['Prospek', 'Lead'],
	Recommended: ['Direkomendasikan', 'Recommended'],
	Watchlist: ['Daftar Pantau', 'Watchlist'],
	'Expiring Soon': ['Segera Kedaluwarsa', 'Expiring Soon'],
	'Needs Evidence': ['Butuh Bukti', 'Needs Evidence'],
	'Needs HS Review': ['Perlu Tinjauan HS', 'Needs HS Review'],
	Enriched: ['Diperkaya', 'Enriched'],
	Missing: ['Hilang', 'Missing'],
	Revoked: ['Dicabut', 'Revoked'],
	Quoted: ['Ditawarkan', 'Quoted'],
	'Needs Research': ['Perlu Riset', 'Needs Research'],
	Internal: ['Internal', 'Internal'],
	Bug: ['Bug', 'Bug'],
	Question: ['Pertanyaan', 'Question'],
	// Prioritas & severity
	Low: ['Rendah', 'Low'],
	Medium: ['Sedang', 'Medium'],
	High: ['Tinggi', 'High'],
	Critical: ['Kritis', 'Critical'],
	Urgent: ['Mendesak', 'Urgent'],
	Major: ['Mayor', 'Major'],
	Minor: ['Minor', 'Minor'],
	Info: ['Info', 'Info'],
	Warning: ['Peringatan', 'Warning'],
	Error: ['Galat', 'Error'],
	// Peran tim
	Admin: ['Admin', 'Admin'],
	Operations: ['Operasional', 'Operations'],
	Compliance: ['Kepatuhan', 'Compliance'],
	Finance: ['Keuangan', 'Finance'],
	Sales: ['Penjualan', 'Sales'],
	Exporter: ['Eksportir', 'Exporter'],
	Buyer: ['Pembeli', 'Buyer'],
	Forwarder: ['Forwarder', 'Forwarder'],
	CustomsBroker: ['Bea Cukai', 'Customs Broker'],
	KepalaDesa: ['Kepala Desa', 'Village Head']
};

/** Terjemahkan label domain; nilai tak dikenal dikembalikan apa adanya. */
export function label(value: string | null | undefined): string {
	if (!value) return '—';
	const entry = LABELS[value];
	return entry ? t(entry[0]) : value;
}
