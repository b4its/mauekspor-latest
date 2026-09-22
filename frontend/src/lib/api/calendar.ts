import { apiFetch } from '$lib/api/client';
import type { CalendarEvent } from '$lib/data/trade';

export function listCalendarEvents() {
	return apiFetch<CalendarEvent[]>('/calendar/');
}

export function createCalendarEvent(payload: Pick<CalendarEvent, 'title' | 'date' | 'type' | 'projectId'>) {
	return apiFetch<CalendarEvent>('/calendar/', { method: 'POST', body: JSON.stringify(payload) });
}

export function markCalendarEventDone(id: string) {
	return apiFetch<CalendarEvent>(`/calendar/${id}/done/`, { method: 'POST' });
}

export function updateCalendarEvent(id: string, payload: Partial<CalendarEvent>) {
	return apiFetch<CalendarEvent>(`/calendar/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function deleteCalendarEvent(id: string) {
	return apiFetch<{ status: string; id: string }>(`/calendar/${id}/`, { method: 'DELETE' });
}
