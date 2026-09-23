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
