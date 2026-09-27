<script lang="ts">
	import { cn, type WithElementRef } from "$lib/utils.js";
	import type { HTMLAttributes } from "svelte/elements";
	import type { Snippet } from "svelte";

	/**
	 * Judul kartu. Secara default `<div>` (agar tidak mengganggu hierarki heading
	 * yang dikelola AppShell), tetapi dapat dijadikan heading semantik dengan
	 * `as="h1" | "h2" | "h3" | "h4"` — dipakai halaman publik yang tidak memakai
	 * AppShell dan butuh heading level satu.
	 */
	let {
		ref = $bindable(null),
		class: className,
		as = "div",
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> & {
		as?: "div" | "h1" | "h2" | "h3" | "h4";
		children?: Snippet;
	} = $props();

	const classes = $derived(
		cn("text-base leading-snug font-medium group-data-[size=sm]/card:text-sm", className)
	);
</script>

<svelte:element
	this={as}
	bind:this={ref}
	data-slot="card-title"
	class={classes}
	{...restProps}
>
	{@render children?.()}
</svelte:element>
