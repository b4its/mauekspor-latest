import { apiFetch } from '$lib/api/client';
import type { TeamMember } from '$lib/data/trade';

export function listTeamMembers() {
	return apiFetch<TeamMember[]>('/team/');
}

export function inviteTeamMember(email: string, role: TeamMember['role']) {
	return apiFetch<TeamMember>('/team/invite/', {
		method: 'POST',
		body: JSON.stringify({ email, role })
	});
}

export function updateTeamMemberRole(id: string, role: TeamMember['role']) {
	return apiFetch<TeamMember>(`/team/${id}/role/`, {
		method: 'POST',
		body: JSON.stringify({ role })
	});
}

export function updateTeamMember(id: string, payload: Partial<Pick<TeamMember, 'name' | 'email' | 'role' | 'status'>>) {
	return apiFetch<TeamMember>(`/team/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function removeTeamMember(id: string) {
	return apiFetch<{ status: string; id: string }>(`/team/${id}/`, { method: 'DELETE' });
}
