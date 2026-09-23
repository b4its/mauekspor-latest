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

let refreshing: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
	if (refreshing) return refreshing;
	refreshing = fetch(`${API_BASE_URL}/auth/refresh/`, {
		method: 'POST',
		credentials: 'include',
		headers: { 'X-Refresh-Token': '' }
	}).then(async (res) => res.ok);
	refreshing.finally(() => (refreshing = null));
	return refreshing;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}, _retried = false): Promise<ApiResult<T>> {
	const isFormData = init.body instanceof FormData;
	const response = await fetch(`${API_BASE_URL}${path}`, {
		...init,
		credentials: 'include',
		headers: {
			Accept: 'application/json',
			...(isFormData ? {} : { 'Content-Type': 'application/json' }),
			...init.headers
		}
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
