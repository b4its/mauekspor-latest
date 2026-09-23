import { apiFetch } from '$lib/api/client';
import type { UserAccount } from '$lib/data/trade';

export type ListUsersParams = {
	search?: string;
	role?: string;
	limit?: number;
	offset?: number;
};

export function listUsers(params: ListUsersParams = {}) {
	const q = new URLSearchParams();
	if (params.search) q.set('search', params.search);
	if (params.role) q.set('role', params.role);
	if (params.limit) q.set('limit', String(params.limit));
	if (params.offset) q.set('offset', String(params.offset));
	const qs = q.toString();
	const path = '/users/' + (qs ? '?' + qs : '');
	return apiFetch<UserAccount[]>(path);
}
export function getUser(id: string) { return apiFetch<UserAccount>(`/users/${id}/`); }
export function deleteUser(id: string) { return apiFetch<{ status: string; id: string }>(`/users/${id}/`, { method: 'DELETE' }); }
