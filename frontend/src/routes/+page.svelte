<script lang="ts">
	import { onMount } from 'svelte';
	let message = 'Loading...';

	onMount(async () => {
		try {
			const res = await fetch('/api/hello');
			const data = await res.json();
			message = data.message;
		} catch (err) {
			message = `Error: ${err.message}`;
		}
	});
</script>

<main class="p-8 text-center">
	<h1 class="text-2xl font-bold mb-4">DuckLearn Test</h1>
	<p class="text-lg text-green-600">{message}</p>
</main>