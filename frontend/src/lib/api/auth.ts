import { apiFetch } from '$lib/api/client';

export type UserRole = 'Admin' | 'Exporter' | 'Buyer' | 'Forwarder' | 'CustomsBroker' | 'Finance';

export type SessionUser = {
	id: string;
	name: string;
	email: string;
	role: UserRole;
	organization: string;
};

export type LoginPayload = {
	email: string;
	password: string;
};

export type RegisterPayload = LoginPayload & {
	name: string;
	role: UserRole;
	organization: string;
};

export function login(payload: LoginPayload) {
	return apiFetch<SessionUser>('/auth/login/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function register(payload: RegisterPayload) {
	return apiFetch<SessionUser>('/auth/register/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function getSession() {
	return apiFetch<SessionUser>('/auth/me/');
}

export function logout() {
	return apiFetch('/auth/logout/', { method: 'POST' });
}
