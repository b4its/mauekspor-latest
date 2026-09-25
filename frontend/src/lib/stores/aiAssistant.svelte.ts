import { page } from '$app/state';

// ─── AI Assistant Global State (Svelte 5 Runes) ─────────────────────────────
let isOpen = $state(false);
let pendingPrompt = $state<string | null>(null);

export function isAiAssistantOpen() {
	return isOpen;
}

export function openAiAssistant(prompt?: string) {
	isOpen = true;
	if (prompt) {
		pendingPrompt = prompt;
	}
}

export function closeAiAssistant() {
	isOpen = false;
}

export function toggleAiAssistant() {
	isOpen = !isOpen;
}

export function consumePendingPrompt(): string | null {
	const prompt = pendingPrompt;
	pendingPrompt = null;
	return prompt;
}

export type PagePromptContext = {
	title: string;
	prompts: string[];
};

export function getPromptsForPath(pathname: string): PagePromptContext {
	if (pathname.startsWith('/products')) {
		return {
			title: 'Katalog Produk & HS Code',
			prompts: [
				'Analisis potensi ekspor katalog produk saya',
				'Bagaimana klasifikasi HS code yang tepat untuk produk UMKM?',
				'Buatkan deskripsi produk B2B berbahasa Inggris profesional'
			]
		};
	}
	if (pathname.startsWith('/compliance')) {
		return {
			title: 'Kepatuhan & Regulasi Ekspor',
			prompts: [
				'Apa syarat kepatuhan ekspor makanan ke Jepang?',
				'Jelaskan kewajiban EUDR untuk komoditas ke Uni Eropa',
				'Apa dokumen wajib karantina tumbuhan/hewan (Phytosanitary)?'
			]
		};
	}
	if (pathname.startsWith('/export-analysis')) {
		return {
			title: 'Analisis Kesiapan Ekspor',
			prompts: [
				'Jelaskan skor kesiapan ekspor produk saya',
				'Negara tujuan mana yang paling potensial untuk produk saya?',
				'Bagaimana cara meningkatkan grade kepatuhan dari C ke A?'
			]
		};
	}
	if (pathname.startsWith('/trade-projects')) {
		return {
			title: 'Proyek Dagang Ekspor',
			prompts: [
				'Ringkas status dan risiko proyek dagang aktif saya',
				'Langkah apa yang perlu segera diselesaikan pada proyek berjalan?',
				'Bagaimana negosiasi term pembayaran LC (Letter of Credit)?'
			]
		};
	}
	if (pathname.startsWith('/costing')) {
		return {
			title: 'Kalkulasi Biaya & Harga',
			prompts: [
				'Bagaimana cara hitung harga FOB dari HPP dan margin keuntungan?',
				'Apa perbedaan mendasar Incoterms EXW, FOB, dan CIF?',
				'Berapa batas aman fluktuasi kurs valuta asing dalam kontrak?'
			]
		};
	}
	if (pathname.startsWith('/markets') || pathname.startsWith('/countries')) {
		return {
			title: 'Pasar & Regulasi Negara',
			prompts: [
				'Negara tujuan dengan pertumbuhan impor tertinggi untuk Indonesia',
				'Bagaimana memanfaatkan tarif preferensial perjanjian dagang (FTA/EPA)?',
				'Apa tren permintaan produk halal di kawasan Timur Tengah?'
			]
		};
	}
	if (pathname.startsWith('/forwarders') || pathname.startsWith('/shipments')) {
		return {
			title: 'Logistik & Forwarder',
			prompts: [
				'Bagaimana memilih forwarder terbaik untuk muatan LCL vs FCL?',
				'Dokumen apa yang dibutuhkan untuk pengurusan Bill of Lading (B/L)?',
				'Tips mengantisipasi demurrage dan detention di pelabuhan tujuan'
			]
		};
	}
	if (pathname.startsWith('/buyers') || pathname.startsWith('/buyer-requests')) {
		return {
			title: 'Jaringan Pembeli & Inquiry',
			prompts: [
				'Bagaimana cara memverifikasi kredibilitas calon buyer internasional?',
				'Cara menyusun penawaran resmi (Quotation) yang menarik buyer',
				'Strategi follow-up buyer setelah pengiriman sampel produk'
			]
		};
	}

	return {
		title: 'Workspace MauEkspor',
		prompts: [
			'Apa langkah awal memulai ekspor bagi produk saya?',
			'Cek kesiapan regulasi dan dokumen produk unggulan saya',
			'Ringkas performa dan proyek dagang yang sedang berjalan'
		]
	};
}
