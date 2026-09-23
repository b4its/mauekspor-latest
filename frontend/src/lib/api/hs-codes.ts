import { apiFetch } from '$lib/api/client';

export type HSCode = {
	hs_code: string;
	description: string;
	section?: string;
	parent?: string;
	level?: number;
	section_name?: string;
	children?: HSCode[];
};

export function listHsCodes(search = '', limit = 50) {
	return apiFetch<HSCode[]>(`/hs-codes/?search=${encodeURIComponent(search)}&limit=${limit}`);
}

export function autocompleteHsCodes(q: string, limit = 10) {
	return apiFetch<HSCode[]>(`/hs-codes/autocomplete/?q=${encodeURIComponent(q)}&limit=${limit}`);
}

export function getHsCode(hsCode: string) {
	return apiFetch<HSCode>(`/hs-codes/${hsCode}/`);
}
