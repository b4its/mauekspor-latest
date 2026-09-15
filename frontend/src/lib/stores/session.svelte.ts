import { apiFetch } from '$lib/api/client';
import { getSession, logout as logoutApi } from '$lib/api/auth';
import type { SessionUser, LoginPayload, RegisterPayload, UserRole } from '$lib/api/auth';

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

let user = $state<SessionUser | null>(null);
let status = $state<AuthStatus>('loading');

export function getUser() {
	return user;
}

export function getStatus() {
	return status;
}

export function isAuthenticated() {
	return status === 'authenticated';
}

function hydrateSession(u: {
	id?: string;
	fullName?: string;
	name?: string;
	email?: string;
	role?: string;
	organization?: string;
} | null): SessionUser | null {
	if (!u?.id) return null;
	return {
		id: u.id,
		name: u.fullName || u.name || u.email || 'User',
		email: u.email ?? '',
		role: (u.role ?? 'Exporter') as UserRole,
		organization: u.organization ?? ''
	};
}

export async function fetchSession(): Promise<boolean> {
	try {
		const res = await getSession();
		user = hydrateSession(res.data);
		status = user ? 'authenticated' : 'unauthenticated';
		return !!user;
	} catch {
		user = null;
		status = 'unauthenticated';
		return false;
	}
}

export async function login(payload: LoginPayload): Promise<void> {
	await apiFetch<SessionUser>('/auth/login/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
	await fetchSession();
}

export async function register(payload: RegisterPayload): Promise<void> {
	await apiFetch<SessionUser>('/auth/register/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
	await fetchSession();
}

export async function logout(): Promise<void> {
	try {
		await logoutApi();
	} finally {
		user = null;
		status = 'unauthenticated';
	}
}