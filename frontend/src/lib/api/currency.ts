import { apiFetch } from '$lib/api/client';

export type CurrencyInfo = {
	code: string;
	name: string;
	symbol: string;
};

export type CurrencySettings = {
	baseCurrency: string;
	displayCurrency: string;
	exchangeRate: number;
	exchangeSource: string;
	available: CurrencyInfo[];
};

export function getCurrencyInfo() {
	return apiFetch<CurrencySettings>('/settings/currencies/');
}

export function setDisplayCurrency(currency: string) {
	return apiFetch<{
		baseCurrency: string;
		displayCurrency: string;
		exchangeRate: number;
		exchangeSource: string;
	}>('/settings/display-currency/', {
		method: 'POST',
		body: JSON.stringify({ currency }),
	});
}
