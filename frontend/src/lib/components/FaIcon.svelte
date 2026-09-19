<script lang="ts">
	/**
	 * FaIcon — wrapper tipis untuk Font Awesome icons.
	 *
	 * Penggunaan:
	 *   <FaIcon icon="fa-solid fa-seedling" />
	 *   <FaIcon icon="fa-solid fa-rocket" class="text-2xl text-blue-400" />
	 *
	 * Prop:
	 *   icon  — kelas FA lengkap, mis. "fa-solid fa-rocket"
	 *   class — kelas Tailwind tambahan (ukuran, warna, dll.)
	 */
	let { icon, class: className = '' }: { icon: string; class?: string } = $props();
</script>

<i class="{icon} {className}" aria-hidden="true"></i>
