export type CountryListItem = {
	country_code: string;
	country_name: string;
	region: string;
	has_details?: boolean;
	risk_level?: string;
	customs_system?: string;
	regulationsCount?: number;
};

export type CountryStats = {
	total: number;
	detailed: number;
	highRisk: number;
};

export function filterCountries(
	items: CountryListItem[],
	opts: { search?: string; region?: string; onlyDetailed?: boolean }
): CountryListItem[] {
	const search = (opts.search ?? '').trim().toLowerCase();
	const region = opts.region ?? '';
	return items.filter((c) => {
		if (search && !(c.country_name + ' ' + c.country_code).toLowerCase().includes(search)) return false;
		if (region && c.region !== region) return false;
		if (opts.onlyDetailed && !c.has_details) return false;
		return true;
	});
}

export function computeCountryStats(items: CountryListItem[]): CountryStats {
	return {
		total: items.length,
		detailed: items.filter((c) => c.has_details).length,
		highRisk: items.filter((c) => c.risk_level === 'High' || c.risk_level === 'Elevated').length,
	};
}
