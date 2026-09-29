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
};

/** Referensi riset faktual terkurasi (timeline, HS 2028, FTA, sistem kepabeanan). */
export function getReference() {
	return apiFetch<ReferenceBundle>('/reference/');
}
