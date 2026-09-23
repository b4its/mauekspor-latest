import { apiFetch } from '$lib/api/client';

export type Country = {
	country_code: string;
	country_name: string;
	region: string;
	regulationsCount?: number;
	regulations?: CountryRegulation[];
	regulations_by_category?: Record<string, CountryRegulation[]>;
};

export type CountryRegulation = {
	country_code?: string;
	rule_category: string;
	forbidden_keywords?: string;
	required_specs?: string;
	description_rule?: string;
};

export function listCountries() {
	return apiFetch<Country[]>('/countries/');
}

export function getCountry(code: string) {
	return apiFetch<Country>(`/countries/${code}/`);
}
