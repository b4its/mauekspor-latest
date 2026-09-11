import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchSession, login, logout, getUser, getStatus, isAuthenticated } from './session.svelte';

function jsonResponse(status: number, data: unknown) {
	return {
		ok: status >= 200 && status < 300,
		status,
		headers: { get: (name: string) => (name.toLowerCase() === 'content-type' ? 'application/json' : null) },
		json: async () => data
	} as unknown as Response;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

async function resetUnauthenticated() {
	vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
	await fetchSession();
	vi.unstubAllGlobals();
}

beforeEach(async () => {
	await resetUnauthenticated();
});

describe('session store', () => {
	it('status awal unauthenticated setelah reset', () => {
		expect(getStatus()).toBe('unauthenticated');
		expect(getUser()).toBeNull();
		expect(isAuthenticated()).toBe(false);
	});

	it('fetchSession sukses -> authenticated dengan user ter-hydrate', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue(
				jsonResponse(200, { data: { id: 'U-1', fullName: 'Rizal Fahmi', email: 'rizal@example.com', role: 'UMKM', organization: 'PT Kopi' } })
			)
		);
		const ok = await fetchSession();
		expect(ok).toBe(true);
		expect(getStatus()).toBe('authenticated');
		expect(isAuthenticated()).toBe(true);
		expect(getUser()?.name).toBe('Rizal Fahmi');
		expect(getUser()?.role).toBe('UMKM');
	});

	it('fetchSession fallback name ke email saat fullName/name kosong', async () => {
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(200, { data: { id: 'U-2', email: 'a@b.c' } })));
		await fetchSession();
		expect(getUser()?.name).toBe('a@b.c');
	});

	it('fetchSession gagal -> unauthenticated, user null', async () => {
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(401, { message: 'Unauthorized' })));
		const ok = await fetchSession();
		expect(ok).toBe(false);
		expect(getStatus()).toBe('unauthenticated');
		expect(getUser()).toBeNull();
	});

	it('login memanggil /auth/login/ lalu fetchSession', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValueOnce(jsonResponse(200, { data: { id: 'U-1' } })) // login
			.mockResolvedValueOnce(
				jsonResponse(200, { data: { id: 'U-1', fullName: 'MauEkspor Admin', email: 'admin@example.com', role: 'Admin' } })
			); // me
		vi.stubGlobal('fetch', fetchMock);

		await login({ email: 'admin@example.com', password: 'password123' });
		expect(fetchMock).toHaveBeenCalledTimes(2);
		expect(String(fetchMock.mock.calls[0][0])).toContain('/auth/login/');
		expect(String(fetchMock.mock.calls[1][0])).toContain('/auth/me/');
		expect(getStatus()).toBe('authenticated');
	});

	it('logout selalu mengosongkan sesi meskipun API gagal', async () => {
		// set authenticated dulu
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(200, { data: { id: 'U-1', fullName: 'X' } })));
		await fetchSession();
		expect(getStatus()).toBe('authenticated');

		// logout dengan API error (state tetap dibersihkan via finally)
		vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
		await logout().catch(() => {});
		expect(getStatus()).toBe('unauthenticated');
		expect(getUser()).toBeNull();
	});
});
