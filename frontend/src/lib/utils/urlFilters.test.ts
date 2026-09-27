import { beforeEach, describe, expect, it, vi } from 'vitest';

const gotoMock = vi.fn();
vi.mock('$app/navigation', () => ({ goto: (...args: unknown[]) => gotoMock(...args) }));

import { readParam, syncFiltersToUrl } from './urlFilters';

function url(path: string) {
	return new URL(`http://localhost:5188${path}`);
}

describe('urlFilters', () => {
	beforeEach(() => gotoMock.mockClear());

	it('menulis nilai non-default ke query string', () => {
		syncFiltersToUrl(url('/products'), { query: 'kopi', status: 'Ready' }, { query: '', status: '' });
		expect(gotoMock).toHaveBeenCalledTimes(1);
		const target = gotoMock.mock.calls[0][0] as string;
		expect(target).toContain('query=kopi');
		expect(target).toContain('status=Ready');
	});

	it('menghapus parameter yang kembali ke nilai default', () => {
		syncFiltersToUrl(url('/products?query=kopi&status=Ready'), { query: '', status: '' }, { query: '', status: '' });
		const target = gotoMock.mock.calls[0][0] as string;
		expect(target).toBe('/products');
	});

	it('mempertahankan parameter lain yang tidak dikelola', () => {
		syncFiltersToUrl(url('/products?from=villages'), { query: 'kopi' }, { query: '' }, ['query']);
		const target = gotoMock.mock.calls[0][0] as string;
		expect(target).toContain('from=villages');
		expect(target).toContain('query=kopi');
	});

	it('tidak memicu navigasi bila URL tidak berubah', () => {
		syncFiltersToUrl(url('/products?query=kopi'), { query: 'kopi' }, { query: '' });
		expect(gotoMock).not.toHaveBeenCalled();
	});

	it('memakai replaceState + noScroll agar tidak mengganggu scroll/focus', () => {
		syncFiltersToUrl(url('/products'), { query: 'x' }, { query: '' });
		const opts = gotoMock.mock.calls[0][1] as Record<string, unknown>;
		expect(opts.replaceState).toBe(true);
		expect(opts.noScroll).toBe(true);
	});

	it('readParam mengembalikan fallback saat parameter tidak ada', () => {
		expect(readParam(url('/products'), 'query', 'default')).toBe('default');
		expect(readParam(url('/products?query=kopi'), 'query', 'default')).toBe('kopi');
	});
});
