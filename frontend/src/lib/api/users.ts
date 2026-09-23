import { apiFetch } from '$lib/api/client';
import type { UserAccount } from '$lib/data/trade';

export function listUsers() { return apiFetch<UserAccount[]>('/users/'); }
export function getUser(id: string) { return apiFetch<UserAccount>(`/users/${id}/`); }
