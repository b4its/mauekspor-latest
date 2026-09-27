import { t } from '$lib/i18n.svelte';

/**
 * Helper konfirmasi aksi destruktif.
 *
 * Sebelumnya `askConfirm` + `runConfirmed` + 7 variabel `$state`-nya disalin
 * verbatim ke 47 berkas rute. Modul ini menjadi satu sumber, dipakai bersama
 * komponen <ConfirmDialog>.
 *
 * Pemakaian:
 * ```svelte
 * const confirm = createConfirmController();
 * // tombol: onclick={() => confirm.ask({ title: t('Hapus x'), description: t('...'), action: () => doDelete() })}
 * // render: <ConfirmDialog bind:open={confirm.open} title={confirm.title} ... onconfirm={confirm.run} />
 * ```
 */
export type ConfirmRequest = {
	title: string;
	description: string;
	detail?: string;
	label?: string;
	action: () => void | Promise<void>;
};

export function createConfirmController() {
	let open = $state(false);
	let title = $state('');
	let description = $state('');
	let detail = $state('');
	let label = $state('');
	let action = $state<() => void | Promise<void>>(() => {});
	let loading = $state(false);

	function ask(request: ConfirmRequest) {
		title = request.title;
		description = request.description;
		detail = request.detail ?? '';
		label = request.label ?? t('Hapus');
		action = request.action;
		open = true;
	}

	async function run() {
		loading = true;
		try {
			await action();
			open = false;
		} finally {
			loading = false;
		}
	}

	return {
		get open() {
			return open;
		},
		set open(value: boolean) {
			open = value;
		},
		get title() {
			return title;
		},
		get description() {
			return description;
		},
		get detail() {
			return detail;
		},
		get label() {
			return label;
		},
		get loading() {
			return loading;
		},
		ask,
		run
	};
}
