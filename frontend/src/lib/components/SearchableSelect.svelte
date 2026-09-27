<script lang="ts">
	import { onMount } from 'svelte';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { t } from '$lib/i18n.svelte';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import SearchIcon from '@lucide/svelte/icons/search';
	import XIcon from '@lucide/svelte/icons/x';
	import CheckIcon from '@lucide/svelte/icons/check';

	type Option = {
		value: string;
		label: string;
		sub?: string;
	};

	let {
		options = $bindable([] as Option[]),
		value = $bindable(''),
		placeholder = t('Pilih...'),
		disabled = false,
		searchable = true,
		groupKey = 'value',
		class: className = '',
		id = undefined,
		labelledby = undefined,
		label = undefined
	}: {
		options?: Option[];
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		searchable?: boolean;
		groupKey?: string;
		class?: string;
		/** id elemen agar bisa dipasangkan dengan <Label for>. */
		id?: string;
		/** id elemen label (aria-labelledby) bila label berada di luar. */
		labelledby?: string;
		/** Label aksesibel langsung (dipakai bila tidak ada elemen label). */
		label?: string;
	} = $props();

	let open = $state(false);
	let query = $state('');
	let expandedGroup = $state<string | null>(null);
	let el = $state<HTMLDivElement | null>(null);
	let activeIndex = $state(-1);

	let filtered = $derived(
		query.trim()
			? options.filter((o) => o.label.toLowerCase().includes(query.toLowerCase()))
			: options
	);

	// Grouping duplikat berdasarkan label
	let grouped = $derived.by(() => {
		const map = new Map<string, Option[]>();
		for (const o of filtered) {
			if (!map.has(o.label)) map.set(o.label, []);
			map.get(o.label)!.push(o);
		}
		return [...map.entries()].map(([label, items]) => ({ label, items }));
	});

	// Daftar opsi terlihat (digabung dari semua grup) untuk navigasi keyboard.
	let flatVisible = $derived(grouped.flatMap((g) => g.items));

	let selected = $derived(options.find((o) => o.value === value) ?? null);

	const uid = $props.id();
	const triggerId = $derived(id ?? `searchable-select-${uid}`);
	const listboxId = $derived(`${triggerId}-listbox`);

	function toggle() {
		if (!disabled) {
			open = !open;
			query = '';
			expandedGroup = null;
			activeIndex = open ? 0 : -1;
		}
	}

	function pick(val: string) {
		value = val;
		open = false;
		query = '';
		expandedGroup = null;
		activeIndex = -1;
	}

	function toggleGroup(label: string) {
		expandedGroup = expandedGroup === label ? null : label;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (disabled) return;
		const items = flatVisible;
		if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
			event.preventDefault();
			if (!open) {
				toggle();
				return;
			}
			const delta = event.key === 'ArrowDown' ? 1 : -1;
			const next = activeIndex + delta;
			activeIndex = next < 0 ? items.length - 1 : next >= items.length ? 0 : next;
		} else if (event.key === 'Enter') {
			if (open && items[activeIndex]) {
				event.preventDefault();
				pick(items[activeIndex].value);
			} else if (!open) {
				event.preventDefault();
				toggle();
			}
		} else if (event.key === 'Escape') {
			if (open) {
				event.preventDefault();
				open = false;
				query = '';
			}
		} else if (event.key === 'Home' && open) {
			event.preventDefault();
			activeIndex = 0;
		} else if (event.key === 'End' && open) {
			event.preventDefault();
			activeIndex = items.length - 1;
		}
	}

	onMount(() => {
		function handleClick(e: MouseEvent) {
			if (el && !el.contains(e.target as Node)) {
				open = false;
				query = '';
				expandedGroup = null;
			}
		}
		document.addEventListener('click', handleClick);
		return () => document.removeEventListener('click', handleClick);
	});
</script>

<div bind:this={el} class={`relative ${className}`}>
	<!-- Trigger -->
	<button
		type="button"
		id={triggerId}
		disabled={disabled}
		onclick={toggle}
		onkeydown={handleKeydown}
		role="combobox"
		aria-haspopup="listbox"
		aria-expanded={open}
		aria-controls={listboxId}
		aria-labelledby={labelledby}
		aria-label={!labelledby ? (label ?? undefined) : undefined}
		class="flex w-full items-center justify-between gap-2 rounded-md border border-border bg-background px-3 py-2 text-left text-sm shadow-sm transition-colors hover:bg-accent/40 disabled:cursor-not-allowed disabled:opacity-60"
	>
		<span class="truncate font-medium {selected ? '' : 'text-muted-foreground'}">
			{selected?.label ?? placeholder}
		</span>
		<ChevronDownIcon class="size-4 shrink-0 text-muted-foreground transition-transform {open ? 'rotate-180' : ''}" />
	</button>

	<!-- Dropdown -->
	{#if open}
		<div id={listboxId} role="listbox" class="absolute inset-x-0 top-full z-50 mt-1.5 overflow-hidden rounded-lg border border-border bg-background shadow-xl">
			<!-- Search -->
			{#if searchable}
				<div class="flex items-center gap-2 border-b bg-muted/30 px-3 py-2">
					<SearchIcon class="size-4 shrink-0 text-muted-foreground" />
					<input
						type="text"
						placeholder={t('Cari...')}
						aria-label={t('Cari opsi')}
						bind:value={query}
						class="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
					/>
					{#if query}
						<button type="button" onclick={() => (query = '')} class="text-muted-foreground hover:text-foreground" aria-label={t('Bersihkan pencarian')}>
							<XIcon class="size-3.5" />
						</button>
					{/if}
				</div>
			{/if}

			<!-- Options -->
			<div class="max-h-64 overflow-y-auto p-1">
				{#if grouped.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">{t('Tidak ada hasil.')}</p>
				{:else}
					{#each grouped as group}
						{#if group.items.length === 1}
							<button
								type="button"
								role="option"
								aria-selected={group.items[0].value === value}
								onclick={() => pick(group.items[0].value)}
								class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent {group.items[0].value === value ? 'bg-accent font-semibold' : ''}"
							>
								<span class="flex min-w-0 items-center gap-2">
									<span class="truncate">{group.items[0].label}</span>
									{#if group.items[0].sub}
										<span class="shrink-0 text-xs text-muted-foreground">{group.items[0].sub}</span>
									{/if}
								</span>
								{#if group.items[0].value === value}
									<CheckIcon class="size-4 shrink-0 text-primary" />
								{/if}
							</button>
						{:else}
							<div class="rounded-md">
								<button
									type="button"
									onclick={() => toggleGroup(group.label)}
									class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent"
								>
									<span class="flex min-w-0 items-center gap-2">
										<span class="truncate">{group.label}</span>
										<Badge variant="outline" class="shrink-0">{group.items.length}</Badge>
									</span>
									<ChevronRightIcon class="size-4 shrink-0 text-muted-foreground transition-transform {expandedGroup === group.label ? 'rotate-90' : ''}" />
								</button>
								{#if expandedGroup === group.label}
									<div class="ml-3 border-l border-border pl-2">
										{#each group.items as item}
											<button
												type="button"
												role="option"
												aria-selected={item.value === value}
												onclick={() => pick(item.value)}
												class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-1.5 text-left text-sm transition-colors hover:bg-accent {item.value === value ? 'bg-accent font-semibold' : ''}"
											>
												<span class="flex min-w-0 items-center gap-2">
													<span class="truncate">{item.label}</span>
													{#if item.sub}
														<span class="shrink-0 text-xs text-muted-foreground">{item.sub}</span>
													{/if}
												</span>
												{#if item.value === value}
													<CheckIcon class="size-4 shrink-0 text-primary" />
												{/if}
											</button>
										{/each}
									</div>
								{/if}
							</div>
						{/if}
					{/each}
				{/if}
			</div>
		</div>
	{/if}
</div>