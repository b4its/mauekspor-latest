export type ApiResult<T> = {
	data: T;
	meta?: Record<string, unknown>;
};

export type ApiErrorBody = {
	message: string;
	errors?: Record<string, string[]>;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

/** URL absolut ke endpoint CSV export backend (mis. '/products/export.csv'). */
export function csvExportUrl(path: string): string {
	return `${API_BASE_URL}${path}`;
}

export class ApiError extends Error {
	status: number;
	body: ApiErrorBody | null;

	constructor(status: number, body: ApiErrorBody | null) {
		super(body?.message ?? `Request failed with status ${status}`);
		this.name = 'ApiError';
		this.status = status;
		this.body = body;
	}
}

// ── Token management ──────────────────────────────────────────────
let _accessToken: string | null = null;
let _refreshToken: string | null = null;

// Coba pulihkan token dari sessionStorage (bertahan saat page reload)
try {
	const saved = sessionStorage.getItem('mauekspor_access_token');
	if (saved) _accessToken = saved;
	const savedRefresh = sessionStorage.getItem('mauekspor_refresh_token');
	if (savedRefresh) _refreshToken = savedRefresh;
} catch { /* sessionStorage mungkin tidak tersedia */ }

/** Simpan access token setelah login/register untuk dikirim sebagai Bearer header. */
export function setAccessToken(token: string | null) {
	_accessToken = token;
	try {
		if (token) {
			sessionStorage.setItem('mauekspor_access_token', token);
		} else {
			sessionStorage.removeItem('mauekspor_access_token');
		}
	} catch { /* ignore */ }
}

/** Ambil access token yang tersimpan. */
export function getAccessToken(): string | null {
	return _accessToken;
}

/** Simpan refresh token untuk digunakan saat token refresh. */
export function setRefreshToken(token: string | null) {
	_refreshToken = token;
	try {
		if (token) {
			sessionStorage.setItem('mauekspor_refresh_token', token);
		} else {
			sessionStorage.removeItem('mauekspor_refresh_token');
		}
	} catch { /* ignore */ }
}

/** Bersihkan semua token (saat logout). */
export function clearTokens() {
	setAccessToken(null);
	setRefreshToken(null);
}

// ── Token refresh ─────────────────────────────────────────────────
let refreshing: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
	if (refreshing) return refreshing;
	const headers: Record<string, string> = {};
	// Kirim refresh_token via header jika tersedia
	if (_refreshToken) {
		headers['X-Refresh-Token'] = _refreshToken;
	} else if (_accessToken) {
		// Fallback: kirim access_token via Authorization
		headers['Authorization'] = `Bearer ${_accessToken}`;
	}
	refreshing = fetch(`${API_BASE_URL}/auth/refresh/`, {
		method: 'POST',
		credentials: 'include',
		headers
	}).then(async (res) => {
		if (res.ok) {
			try {
				const body = await res.json();
				if (body?.meta?.access_token) {
					setAccessToken(body.meta.access_token as string);
				}
				if (body?.meta?.refresh_token) {
					setRefreshToken(body.meta.refresh_token as string);
				}
			} catch { /* ignore */ }
		} else {
			// Refresh gagal → bersihkan token
			clearTokens();
		}
		return res.ok;
	});
	refreshing.finally(() => (refreshing = null));
	return refreshing;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}, _retried = false): Promise<ApiResult<T>> {
	const isFormData = init.body instanceof FormData;

	// Build headers: tambahkan Authorization Bearer jika token tersedia
	const headers: Record<string, string> = {
		Accept: 'application/json',
		...(isFormData ? {} : { 'Content-Type': 'application/json' }),
		...(init.headers as Record<string, string> | undefined)
	};
	if (_accessToken && !headers['Authorization']) {
		headers['Authorization'] = `Bearer ${_accessToken}`;
	}

	const response = await fetch(`${API_BASE_URL}${path}`, {
		...init,
		credentials: 'include',
		headers
	});

	if (response.status === 401 && !_retried && !path.startsWith('/auth/')) {
		const ok = await attemptRefresh();
		if (ok) return apiFetch<T>(path, init, true);
	}

	const body = response.headers.get('content-type')?.includes('application/json')
		? await response.json()
		: null;

	if (!response.ok) {
		throw new ApiError(response.status, body as ApiErrorBody | null);
	}

	return body as ApiResult<T>;
}
