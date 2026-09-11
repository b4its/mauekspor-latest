import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiFetch, ApiError, csvExportUrl } from './client';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: {
			get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null)
		},
		json: async () => data
	} as unknown as Response;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('csvExportUrl', () => {
	it('menggabungkan base URL dengan path', () => {
		expect(csvExportUrl('/products/export.csv')).toMatch(/\/api\/v1\/products\/export\.csv$/);
	});
});

describe('ApiError', () => {
	it('menyimpan status dan body', () => {
		const err = new ApiError(404, { message: 'Product not found' });
		expect(err).toBeInstanceOf(Error);
		expect(err.name).toBe('ApiError');
		expect(err.status).toBe(404);
		expect(err.message).toBe('Product not found');
		expect(err.body?.message).toBe('Product not found');
	});

	it('fallback pesan default jika body null', () => {
		const err = new ApiError(500, null);
		expect(err.message).toBe('Request failed with status 500');
	});
});

describe('apiFetch', () => {
	it('mengembalikan data saat sukses', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { data: { id: 'P-1' } }));
		vi.stubGlobal('fetch', fetchMock);

		const result = await apiFetch<{ id: string }>('/products/');
		expect(result.data).toEqual({ id: 'P-1' });
		expect(fetchMock).toHaveBeenCalledTimes(1);
		// credentials include + Content-Type json
		const init = fetchMock.mock.calls[0][1];
		expect(init.credentials).toBe('include');
		expect(init.headers['Content-Type']).toBe('application/json');
	});

	it('melempar ApiError saat response error', async () => {
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(404, { message: 'Product not found' })));

		await expect(apiFetch('/products/')).rejects.toMatchObject({
			name: 'ApiError',
			status: 404,
			message: 'Product not found'
		});
	});

	it('melempar ApiError dengan status saat body bukan json', async () => {
		const res = {
			ok: false,
			status: 500,
			headers: { get: () => null },
			json: async () => {
				throw new Error('no json');
			}
		} as unknown as Response;
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(res));

		await expect(apiFetch('/products/')).rejects.toMatchObject({ status: 500 });
	});

	it('retry sekali setelah refresh berhasil saat 401', async () => {
		const fetchMock = vi
			.fn()
			// panggilan 1: 401 -> trigger refresh
			.mockResolvedValueOnce(jsonResponse(401, { message: 'Unauthorized' }))
			// panggilan 2: refresh endpoint -> ok
			.mockResolvedValueOnce(jsonResponse(200, { ok: true }))
			// panggilan 3: retry original -> sukses
			.mockResolvedValueOnce(jsonResponse(200, { data: { id: 'P-2' } }));
		vi.stubGlobal('fetch', fetchMock);

		const result = await apiFetch<{ id: string }>('/products/');
		expect(result.data).toEqual({ id: 'P-2' });
		expect(fetchMock).toHaveBeenCalledTimes(3);
		// panggilan kedua harus ke /auth/refresh/
		expect(String(fetchMock.mock.calls[1][0])).toContain('/auth/refresh/');
	});

	it('tidak mencoba refresh untuk endpoint auth', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(401, { message: 'Unauthorized' }));
		vi.stubGlobal('fetch', fetchMock);

		await expect(apiFetch('/auth/me/')).rejects.toMatchObject({ status: 401 });
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});
});
