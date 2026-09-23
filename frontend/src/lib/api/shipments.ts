import { apiFetch } from '$lib/api/client';
import type { Shipment } from '$lib/data/trade';

export type ShipmentExceptionPayload = {
	shipmentId: string;
	note: string;
	owner: string;
};

export function listShipments() {
	return apiFetch<Shipment[]>('/shipments/');
}

export function getShipment(id: string) {
	return apiFetch<Shipment>(`/shipments/${id}/`);
}

export function updateShipmentMilestone(id: string, milestone: string) {
	return apiFetch<Shipment>(`/shipments/${id}/milestones/`, {
		method: 'POST',
		body: JSON.stringify({ milestone })
	});
}

export function resolveShipmentException(payload: ShipmentExceptionPayload) {
	return apiFetch<Shipment>(`/shipments/${payload.shipmentId}/exceptions/resolve/`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}
