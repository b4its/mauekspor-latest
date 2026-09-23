import { apiFetch } from '$lib/api/client';
import type { ExportAnalysis } from '$lib/data/trade';

export type CreateExportAnalysisPayload = {
	productId: string;
	destination: string;
};

export type ComparePayload = {
	product_id: string;
	country_codes: string[];
};

export type CompareResult = {
	analysisId: string;
	country: string;
	score: number;
	grade: string;
	critical_issues: number;
	recommendation: string;
};

export type RegulationSection = {
	key: string;
	title: string;
	title_en?: string;
	body: string;
};

export type RegulationRecommendations = {
	analysisId?: string;
	language?: string;
	sections: RegulationSection[];
	country?: Record<string, unknown>;
	fromCache?: boolean;
};

export type Country = {
	country_code: string;
	country_name: string;
	region: string;
	regulationsCount?: number;
	regulations?: CountryRegulation[];
	regulations_by_category?: Record<string, CountryRegulation[]>;
};

export type CountryRegulation = {
	country_code?: string;
	rule_category: string;
	forbidden_keywords?: string;
	required_specs?: string;
	description_rule?: string;
};

export function listExportAnalyses() {
	return apiFetch<ExportAnalysis[]>('/export-analysis/');
}

export function getExportAnalysis(id: string) {
	return apiFetch<ExportAnalysis>(`/export-analysis/${id}/`);
}

export function createExportAnalysis(payload: CreateExportAnalysisPayload) {
	return apiFetch<ExportAnalysis>('/export-analysis/', { method: 'POST', body: JSON.stringify(payload) });
}

export function deleteExportAnalysis(id: string) {
	return apiFetch<{ status: string }>(`/export-analysis/${id}/`, { method: 'DELETE' });
}

export function reanalyzeExportAnalysis(id: string) {
	return apiFetch<ExportAnalysis>(`/export-analysis/${id}/reanalyze/`, { method: 'POST' });
}

export function compareExportAnalyses(payload: ComparePayload) {
	return apiFetch<{ product: { id: string; name: string }; results: CompareResult[] }>('/export-analysis/compare/', {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export function runRegulationCheck(id: string) {
	return apiFetch<ExportAnalysis>(`/export-analysis/${id}/regulation-recommendations/`, { method: 'POST' });
}

export function getRegulationRecommendations(id: string, language = 'id') {
	return apiFetch<RegulationRecommendations>(`/export-analysis/${id}/regulation-recommendations/?language=${language}`);
}

export function analysisPdfUrl(id: string) {
	const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
	return `${base}/export-analysis/${id}/pdf/`;
}

// ---------- Countries ----------
export function listCountries() {
	return apiFetch<Country[]>('/countries/');
}

export function getCountry(code: string) {
	return apiFetch<Country>(`/countries/${code}/`);
}
