import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/i18n.svelte', () => ({ t: (key: string) => key }));

import { createConfirmController } from './confirm.svelte';

describe('createConfirmController', () => {
	it('ask() membuka dialog dengan nilai yang diminta', () => {
		const confirm = createConfirmController();
		expect(confirm.open).toBe(false);

		const action = vi.fn();
		confirm.ask({
			title: 'Hapus produk',
			description: 'Produk akan dihapus permanen.',
			detail: 'Kopi Gayo',
			action
		});

		expect(confirm.open).toBe(true);
		expect(confirm.title).toBe('Hapus produk');
		expect(confirm.description).toBe('Produk akan dihapus permanen.');
		expect(confirm.detail).toBe('Kopi Gayo');
		// label default diambil dari kamus t('Hapus')
		expect(confirm.label).toBe('Hapus');
	});

	it('run() menjalankan action dan menutup dialog', async () => {
		const confirm = createConfirmController();
		const action = vi.fn().mockResolvedValue(undefined);
		confirm.ask({ title: 'T', description: 'D', action });

		await confirm.run();

		expect(action).toHaveBeenCalledTimes(1);
		expect(confirm.open).toBe(false);
		expect(confirm.loading).toBe(false);
	});

	it('run() tetap menutup loading ketika action gagal', async () => {
		const confirm = createConfirmController();
		const action = vi.fn().mockRejectedValue(new Error('boom'));
		confirm.ask({ title: 'T', description: 'D', action });

		await expect(confirm.run()).rejects.toThrow('boom');
		expect(confirm.loading).toBe(false);
	});

	it('label kustom dipakai bila diberikan', () => {
		const confirm = createConfirmController();
		confirm.ask({ title: 'T', description: 'D', label: 'Jalankan', action: () => {} });
		expect(confirm.label).toBe('Jalankan');
	});

	it('open dapat diubah langsung untuk menutup dialog', () => {
		const confirm = createConfirmController();
		confirm.ask({ title: 'T', description: 'D', action: () => {} });
		confirm.open = false;
		expect(confirm.open).toBe(false);
	});
});
