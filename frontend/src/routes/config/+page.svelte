<script lang="ts">
	import { onMount } from 'svelte';

	let config: Record<string, any> | null = null;
	let error: string | null = null;

	onMount(async () => {
		try {
			const res = await fetch('/api/config');
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			config = await res.json();
		} catch (err) {
			error = err.message;
		}
	});
</script>

<main class="p-8 max-w-2xl mx-auto">
	<h1 class="text-2xl font-bold mb-6 text-center">DuckDB Configuration</h1>

	{#if error}
		<p class="text-red-600 text-center">❌ {error}</p>
	{:else if !config}
		<p class="text-gray-500 text-center">Loading...</p>
	{:else}
		<div class="bg-white shadow-md rounded-2xl p-6 space-y-3">
			{#each Object.entries(config) as [key, value]}
				<div class="flex justify-between border-b border-gray-100 pb-2">
					<span class="font-medium capitalize text-gray-700">{key.replaceAll('_', ' ')}</span>
					<span class="text-gray-900">
						{#if value === null}
							<em class="text-gray-400">null</em>
						{:else if typeof value === 'boolean'}
							{value ? '✅ True' : '❌ False'}
						{:else}
							{value}
						{/if}
					</span>
				</div>
			{/each}
		</div>
	{/if}
</main>

<style>
	main {
		font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
	}
</style>