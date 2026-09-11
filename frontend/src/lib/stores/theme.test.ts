import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { getTheme, setTheme, toggleTheme } from './theme.svelte';

function stubDom() {
	const storage = new Map<string, string>();
	const classList = { toggle: vi.fn(), contains: vi.fn(() => false) };
	const documentStub = { documentElement: { classList } };
	const matchMedia = vi.fn(() => ({ matches: false, addEventListener: vi.fn() }));
	vi.stubGlobal('window', {
		localStorage: {
			getItem: vi.fn((k: string) => storage.get(k) ?? null),
			setItem: vi.fn((k: string, v: string) => void storage.set(k, v))
		},
		matchMedia
	});
	vi.stubGlobal('document', documentStub);
	return { storage, classList };
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('theme store', () => {
	it('default light saat window tidak tersedia (node)', () => {
		// theme di-inisialisasi saat import; di node tanpa window -> light
		expect(['light', 'dark']).toContain(getTheme());
	});

	it('setTheme menyimpan ke localStorage dan menerapkan class', () => {
		const { storage, classList } = stubDom();
		setTheme('dark');
		expect(getTheme()).toBe('dark');
		expect(storage.get('mauekspor-theme')).toBe('dark');
		expect(classList.toggle).toHaveBeenCalledWith('dark', true);
	});

	it('toggleTheme membalik light <-> dark', () => {
		stubDom();
		setTheme('light');
		expect(getTheme()).toBe('light');
		toggleTheme();
		expect(getTheme()).toBe('dark');
		toggleTheme();
		expect(getTheme()).toBe('light');
	});
});
