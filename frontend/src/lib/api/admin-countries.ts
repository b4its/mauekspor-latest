import { apiFetch } from '$lib/api/client';

export type AdminCountry = {
	id: string;
	country_code: string;
	country_name: string;
	region: string;
	regulationsCount?: number;
	_has_profile?: boolean;
	_is_template?: boolean;
};

export type AdminRegulation = {
	id: string;
	country_code: string;
	rule_category: string;
	forbidden_keywords: string;
	required_specs: string;
	description_rule: string;
};

export type RegulationPayload = {
	rule_category: string;
	forbidden_keywords: string;
	required_specs: string;
	description_rule: string;
};

export function listAdminCountries() {
	return apiFetch<AdminCountry[]>('/countries/');
}

export function createAdminCountry(payload: { country_code: string; country_name: string; region?: string }) {
	return apiFetch<AdminCountry>('/admin/countries/', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateAdminCountry(countryCode: string, payload: { country_name: string; region?: string }) {
	return apiFetch<AdminCountry>(`/admin/countries/${countryCode}/`, { method: 'PUT', body: JSON.stringify(payload) });
}

export function deleteAdminCountry(countryCode: string) {
	return apiFetch<{ status: string }>(`/admin/countries/${countryCode}/delete/`, { method: 'DELETE' });
}

export function listAdminRegulations(countryCode: string, ruleCategory = '') {
	return apiFetch<AdminRegulation[]>(
		`/admin/countries/${countryCode}/regulations/${ruleCategory ? `?rule_category=${encodeURIComponent(ruleCategory)}` : ''}`
	);
}

export function createAdminRegulation(countryCode: string, payload: RegulationPayload) {
	return apiFetch<AdminRegulation>(`/admin/countries/${countryCode}/regulations/create/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function updateAdminRegulation(regulationId: string, payload: RegulationPayload) {
	return apiFetch<AdminRegulation>(`/admin/regulations/${regulationId}/`, {
		method: 'PUT',
		body: JSON.stringify(payload)
	});
}

export function deleteAdminRegulation(regulationId: string) {
	return apiFetch<{ status: string }>(`/admin/regulations/${regulationId}/delete/`, { method: 'DELETE' });
}

export function importAdminRegulations(file: File) {
	const form = new FormData();
	form.append('file', file);
	return apiFetch<{ imported: number }>('/admin/regulations/import/', { method: 'POST', body: form });
}
