/**
 * Pagination helper: ambil subset array untuk halaman tertentu.
 * Gunakan bersama komponen Pagination.svelte.
 *
 * Contoh di +page.svelte:
 *   let page = $state(1);
 *   let pageSize = $state(20);
 *   let filtered = $derived.by(() => { ... filter items ... });
 *   let paged = $derived(paginate(filtered, page, pageSize));
 *   let totalPages = $derived(calcTotalPages(filtered.length, pageSize));
 */
export function paginate<T>(items: T[], page: number, pageSize: number): T[] {
	const start = (page - 1) * pageSize;
	return items.slice(start, start + pageSize);
}

export function calcTotalPages(totalItems: number, pageSize: number): number {
	return Math.max(1, Math.ceil(totalItems / pageSize));
}

export function resetPageOnSearch(page: { value: number }, currentFilter: string, previousFilter: { value: string }) {
	if (currentFilter !== previousFilter.value) {
		page.value = 1;
		previousFilter.value = currentFilter;
	}
}