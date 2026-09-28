export type ApiResult<T> = {
	data: T;
	meta?: Record<string, unknown>;
};

export type ApiErrorBody = {
	message: string;
	errors?: Record<string, string[]>;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

/** URL absolut ke endpoint CSV export backend (mis. '/products/export.csv'). */
export function csvExportUrl(path: string): string {
	return `${API_BASE_URL}${path}`;
}

export type ExportScope = {
	/** Kata kunci pencarian aktif. */
	search?: string;
	/** Filter status aktif ('' = semua). */
	status?: string;
	/** Daftar id terpilih; bila ada, mengalahkan filter lain. */
	ids?: string[];
};

/**
 * Bangun path export ber-scope (FR-EXP-2): sertakan `search`/`status`/`ids`
 * agar berkas yang diunduh mencerminkan tampilan yang sedang ditinjau.
 */
export function exportPath(path: string, scope: ExportScope = {}): string {
	const qs = new URLSearchParams();
	if (scope.ids && scope.ids.length) qs.set('ids', scope.ids.join(','));
	if (scope.search) qs.set('search', scope.search);
	if (scope.status) qs.set('status', scope.status);
	const query = qs.toString();
	return query ? `${path}?${query}` : path;
}

/**
 * Unduh file dari endpoint backend yang butuh autentikasi (export CSV/XLSX,
 * PDF, dsb). Berbeda dengan `<a href>`, helper ini mengirim header
 * `Authorization: Bearer` dari token sesi sehingga unduhan tidak 401.
 *
 * Token disimpan di sessionStorage, jadi tidak ikut pada navigasi tautan biasa;
 * karena itu unduhan harus lewat fetch + blob.
 */
export type DownloadOptions = {
	/** Metode HTTP (default GET). POST dipakai endpoint yang butuh body. */
	method?: 'GET' | 'POST';
	/** Body JSON untuk metode POST. */
	body?: unknown;
};

export async function downloadFile(
	path: string,
	filename: string,
	options: DownloadOptions = {}
): Promise<void> {
	const { method = 'GET', body } = options;
	const headers: Record<string, string> = {};
	// Prefer token dari store (sudah dimuat dari sessionStorage), fallback ke
	// sessionStorage langsung bila store belum diinisialisasi (mis. SSR guard).
	const token =
		_accessToken ??
		(typeof sessionStorage !== 'undefined' ? sessionStorage.getItem('mauekspor_access_token') : null);
	if (token) headers['Authorization'] = `Bearer ${token}`;
	if (body !== undefined) headers['Content-Type'] = 'application/json';

	const response = await fetch(`${API_BASE_URL}${path}`, {
		method,
		credentials: 'include',
		headers,
		body: body === undefined ? undefined : JSON.stringify(body)
	});
	if (!response.ok) {
		// Coba baca pesan error JSON agar pengguna tahu alasan kegagalan.
		let errBody: ApiErrorBody | null = null;
		try {
			if (response.headers.get('content-type')?.includes('application/json')) {
				errBody = (await response.json()) as ApiErrorBody;
			}
		} catch {
			/* abaikan body tak terbaca */
		}
		throw new ApiError(response.status, errBody);
	}
	const blob = await response.blob();
	const url = URL.createObjectURL(blob);
	try {
		const link = document.createElement('a');
		link.href = url;
		link.download = filename;
		document.body.appendChild(link);
		link.click();
		link.remove();
	} finally {
		// Bebaskan object URL setelah klik diproses.
		setTimeout(() => URL.revokeObjectURL(url), 1000);
	}
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
			// Refresh gagal → bersihkan token dan sinyalkan session expired
			clearTokens();
			try {
				window.dispatchEvent(new CustomEvent('mauekspor-session-expired'));
			} catch { /* SSR / non-browser */ }
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
