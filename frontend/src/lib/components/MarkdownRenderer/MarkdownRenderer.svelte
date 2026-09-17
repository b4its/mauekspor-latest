<script lang="ts">
	import { marked } from 'marked';

	let { text = '' }: { text?: string } = $props();

	let html = $state('');

	$effect(() => {
		if (text) {
			marked.setOptions({ breaks: true, gfm: true });
			html = marked.parse(text, { async: false }) as string;
		}
	});
</script>

{#if html}
	<div class="md-render text-sm leading-relaxed">
		{@html html}
	</div>
{/if}

<style>
	.md-render :global(p) { margin-bottom: 0.5rem; }
	.md-render :global(ul) { margin-bottom: 0.5rem; list-style: disc; padding-left: 1.25rem; }
	.md-render :global(ol) { margin-bottom: 0.5rem; list-style: decimal; padding-left: 1.25rem; }
	.md-render :global(li > p) { margin-bottom: 0; }
	.md-render :global(code) { border-radius: 0.25rem; background: hsl(var(--muted)); padding: 0.125rem 0.375rem; font-family: monospace; font-size: 0.75rem; }
	.md-render :global(pre) { margin-bottom: 0.75rem; overflow-x: auto; border-radius: 0.5rem; background: hsl(var(--muted)); padding: 0.75rem; }
	.md-render :global(pre code) { background: transparent; padding: 0; }
	.md-render :global(h1) { margin-bottom: 0.5rem; font-size: 1.125rem; font-weight: 700; }
	.md-render :global(h2) { margin-bottom: 0.5rem; font-size: 1rem; font-weight: 700; }
	.md-render :global(h3) { margin-bottom: 0.25rem; font-size: 0.875rem; font-weight: 700; }
	.md-render :global(hr) { margin: 0.75rem 0; }
	.md-render :global(blockquote) { margin-bottom: 0.5rem; border-left: 2px solid hsl(var(--primary) / 0.3); padding-left: 0.75rem; color: hsl(var(--muted-foreground)); }
	.md-render :global(a) { color: hsl(var(--primary)); text-decoration: underline; }
	.md-render :global(a:hover) { text-decoration: none; }
	.md-render :global(table) { margin-bottom: 0.75rem; width: 100%; border-collapse: collapse; }
	.md-render :global(th) { border: 1px solid hsl(var(--border)); background: hsl(var(--muted) / 0.5); padding: 0.25rem 0.5rem; text-align: left; font-size: 0.75rem; }
	.md-render :global(td) { border: 1px solid hsl(var(--border)); padding: 0.25rem 0.5rem; font-size: 0.75rem; }
</style>