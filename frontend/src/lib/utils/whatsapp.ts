/**
 * Utilitas WhatsApp (diadaptasi dari `lib/utils/whatsapp.ts` ExportReadyAI-fe).
 * Membuka chat WhatsApp (wa.me) dengan pesan template.
 */

import { t } from '$lib/i18n.svelte';

const DEFAULT_TEMPLATES: { label: string; text: string }[] = [
	{
		label: 'Perkenalan',
		text: 'Halo {name}, saya dari {company}. Kami tertarik untuk berdiskusi peluang kerja sama.'
	},
	{
		label: 'Minta penawaran',
		text: 'Halo {name}, bisakah kami mendapatkan penawaran terbaru untuk {company}?'
	},
	{
		label: 'Tindak lanjut pengiriman',
		text: 'Halo {name}, kami ingin menindaklanjuti status pengiriman untuk {company}.'
	},
	{
		label: 'Dokumen',
		text: 'Halo {name}, dokumen untuk {company} sudah kami siapkan. Mohon dicek.'
	},
	{
		label: 'Jadwal meeting',
		text: 'Halo {name}, apakah Anda tersedia untuk meeting singkat minggu ini terkait {company}?'
	},
	{
		label: 'Umpan balik',
		text: 'Halo {name}, mohon masukan untuk kerja sama {company} sejauh ini.'
	}
];

export function openWhatsApp(phone: string, message: string): void {
	let digits = phone.replace(/[^0-9]/g, '');
	if (!digits) return;
	// Konversi prefix 0 (lokal Indonesia) ke 62 (kode negara)
	if (digits.startsWith('0')) {
		digits = '62' + digits.slice(1);
	}
	const encoded = encodeURIComponent(message);
	const url = `https://wa.me/${digits}?text=${encoded}`;
	window.open(url, '_blank', 'noopener,noreferrer');
}

export function getWhatsAppTemplates() {
	return DEFAULT_TEMPLATES.map((template) => ({
		label: t(template.label),
		text: t(template.text)
	}));
}
