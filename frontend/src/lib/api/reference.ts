import { apiFetch } from '$lib/api/client';

export type ReferenceTimelineItem = { date: string; event: string; scope: string };

export type ReferenceHs2028 = {
	effective: string;
	edition: number;
	review_cycle: string;
	amendment_sets: number;
	headings_total: number;
	subheadings_total: number;
	headings_new: number;
	headings_deleted: number;
	subheadings_new: number;
	subheadings_deleted: number;
	highlights: string;
	preparation: string;
	sources?: { name: string; url: string }[];
};

export type ReferenceFta = { name: string; status: string; note: string };

export type ReferenceBundle = {
	snapshotDate: string;
	guide: string;
	disclaimer: string;
	timeline: ReferenceTimelineItem[];
	hs2028: ReferenceHs2028;
	hsStructureNote: string;
	indonesiaFtas: ReferenceFta[];
	customsSystems: Record<
		string,
		{ label: string; nomenclature: string; tariffs: string; note: string }
	>;
	// ── Data lengkap dari panduan (full guide) ──
	institutions?: { abbr: string; name: string; function: string; url: string }[];
	wtoPrinciples?: { name: string; detail: string }[];
	incoterms?: { code: string; name: string; risk: string; mode: string }[];
	incotermsNotes?: string[];
	hsDigitLengths?: { name: string; system: string; digits: number }[];
	hs2022?: { sections: number; chapters: number; reserved_chapter: number; headings: number; subheadings: number };
	kumhs?: { rule: string; detail: string }[];
	classificationTips?: string[];
	indonesia?: {
		legalBasis: { regulation: string; material: string }[];
		btki: { effective: string; basis: string; lines: number; lines_previous: number; access: string };
		importDereg2025: string[];
		exportDereg2026: string[];
		licenses: { document: string; note: string }[];
		systems: { name: string; detail: string }[];
		importLevies: { levy: string; rate: string }[];
		importExample: Record<string, number | string>;
		parcelRules: string[];
		dhe: Record<string, string>;
		hilirisasi: string[];
		coo: { portal: string; forms: string[]; euGsp: string };
	};
	unitedStates?: {
		timeline: { date: string; event: string }[];
		section301ForcedLabor: {
			effective: string;
			standard_10pct: string[];
			standard_12_5pct: string[];
			mfn_capped: Record<string, string[]>;
			exemptions: string[];
			trq_textile: string[];
			ftz: string;
		};
		section232: { product: string; tariff: string }[];
		china: string[];
		importCompliance: string[];
	};
	europeanUnion?: {
		cbam: Record<string, string | string[]>;
		eudr: Record<string, string | string[]>;
		customsReform: string[];
		tariff: string[];
	};
	otherCountries?: { name: string; authority: string; note: string }[];
	globalFtas?: { name: string; note: string }[];
	rulesOfOrigin?: { rule: string; detail: string }[];
	standardDocuments?: { document: string; function: string }[];
	paymentMethods?: string;
	exportControls?: { scope: string; detail: string }[];
	officialPortals?: { country: string; portals: string[] }[];
	globalPortals?: { need: string; portal: string }[];
	complianceChecklist?: { section: string; items: string[] }[];
	primarySources?: string[];
};

/** Referensi riset faktual terkurasi (timeline, HS 2028, FTA, sistem kepabeanan). */
export function getReference() {
	return apiFetch<ReferenceBundle>('/reference/');
}
