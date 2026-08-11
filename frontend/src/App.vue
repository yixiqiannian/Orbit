<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans, 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif);
  background-color: var(--color-background, #f8fafc);
  color: var(--color-foreground, #1e3a8a);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code,
pre,
kbd {
  font-family: var(--font-code, 'Fira Code', Consolas, Menlo, monospace);
}
</style>
