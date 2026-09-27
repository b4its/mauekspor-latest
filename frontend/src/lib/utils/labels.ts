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
