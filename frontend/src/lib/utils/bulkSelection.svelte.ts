/**
 * State pemilihan baris (bulk) yang bisa dipakai ulang.
 *
 * Sebelumnya pola `Set<string>` + `toggleAll` disalin manual di halaman produk.
 * Helper ini memusatkannya agar setiap halaman list bisa menawarkan aksi massal
 * (hapus terpilih, dsb.) dengan perilaku yang konsisten: pilih satu, pilih
 * semua yang tampak, dan hitung jumlah terpilih.
 *
 * Dipakai dari komponen Svelte:
 *   const bulk = createBulkSelection();
 *   bulk.toggle(id) / bulk.toggleAll(ids) / bulk.clear() / bulk.has(id)
 */
export function createBulkSelection() {
	let selected = $state<Set<string>>(new Set());

	function toggle(id: string) {
		const next = new Set(selected);
		if (next.has(id)) next.delete(id);
		else next.add(id);
		selected = next;
	}

	/** Pilih/batalkan semua id yang diberikan (biasanya item yang sedang tampak). */
	function toggleAll(ids: string[]) {
		const allSelected = ids.length > 0 && ids.every((id) => selected.has(id));
		const next = new Set(selected);
		for (const id of ids) {
			if (allSelected) next.delete(id);
			else next.add(id);
		}
		selected = next;
	}

	function clear() {
		selected = new Set();
	}

	/** Buang id yang tidak lagi ada (mis. setelah reload daftar). */
	function keepOnly(ids: string[]) {
		const valid = new Set(ids);
		const next = new Set([...selected].filter((id) => valid.has(id)));
		selected = next;
	}

	return {
		get selected() {
			return selected;
		},
		get count() {
			return selected.size;
		},
		get ids() {
			return [...selected];
		},
		has: (id: string) => selected.has(id),
		toggle,
		toggleAll,
		clear,
		keepOnly,
		/** Semua id yang diberikan sudah terpilih? */
		allOf: (ids: string[]) => ids.length > 0 && ids.every((id) => selected.has(id))
	};
}
