import { describe, expect, it } from 'vitest';
import { filterCountries, computeCountryStats, type CountryListItem } from './countries';

const items: CountryListItem[] = [
	{ country_code: 'ID', country_name: 'Indonesia', region: 'Asia', has_details: true, risk_level: 'Moderate' },
	{ country_code: 'JP', country_name: 'Japan', region: 'Asia', has_details: true, risk_level: 'Moderate' },
	{ country_code: 'US', country_name: 'United States', region: 'Americas', has_details: true, risk_level: 'Elevated' },
	{ country_code: 'RU', country_name: 'Russia', region: 'Europe', has_details: false, risk_level: 'High' },
	{ country_code: 'ZZ', country_name: 'Unknownia', region: 'Oceania', has_details: false },
];

describe('filterCountries', () => {
	it('tanpa filter mengembalikan semua', () => {
		expect(filterCountries(items, {})).toHaveLength(items.length);
	});

	it('mencari nama atau kode ISO (case-insensitive)', () => {
		expect(filterCountries(items, { search: 'indo' }).map((c) => c.country_code)).toEqual(['ID']);
		expect(filterCountries(items, { search: 'unit' }).map((c) => c.country_code)).toEqual(['US']);
		expect(filterCountries(items, { search: 'JP' }).map((c) => c.country_code)).toEqual(['JP']);
	});

	it('memfilter berdasarkan region', () => {
		expect(filterCountries(items, { region: 'Asia' })).toHaveLength(2);
		expect(filterCountries(items, { region: 'Europe' }).map((c) => c.country_code)).toEqual(['RU']);
		expect(filterCountries(items, { region: 'Tidak-Ada' })).toHaveLength(0);
	});

	it('hanya negara dengan detail', () => {
		expect(filterCountries(items, { onlyDetailed: true })).toHaveLength(3);
	});

	it('gabungan search + region + onlyDetailed', () => {
		expect(filterCountries(items, { region: 'Asia', onlyDetailed: true })).toHaveLength(2);
		expect(filterCountries(items, { region: 'Europe', onlyDetailed: true })).toHaveLength(0);
	});

	it('mengabaikan whitespace pada pencarian', () => {
		expect(filterCountries(items, { search: ' indo ' })).toHaveLength(1);
	});
});

describe('computeCountryStats', () => {
	it('menghitung total, detailed, dan high risk', () => {
		expect(computeCountryStats(items)).toEqual({ total: 5, detailed: 3, highRisk: 2 });
	});

	it('daftar kosong -> semua nol', () => {
		expect(computeCountryStats([])).toEqual({ total: 0, detailed: 0, highRisk: 0 });
	});
});
