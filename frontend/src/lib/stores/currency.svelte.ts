import { writable } from 'svelte/store';
import { getDisplayCurrency, setDisplayCurrency } from '$lib/utils/format';

// ─── Currency store ──────────────────────────────────────────────────────────
// Reactive store untuk display currency. Default IDR.
// Dipakai di settings page dan AppShell untuk currency selector.

function createCurrencyStore() {
	const { subscribe, set } = writable(getDisplayCurrency());

	return {
		subscribe,
		set(code: string) {
			setDisplayCurrency(code);
			set(code);
		},
	};
}

export const displayCurrency = createCurrencyStore();
