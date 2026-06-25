<template>
  <div class="header">
    <div>
      <h2>{{ title }}</h2>
      <p v-if="description">{{ description }}</p>
    </div>
    <slot />
  </div>
</template>
<script setup>
defineProps({ title: String, description: String })
</script>
<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
h2 { margin: 0; }
p { margin: 6px 0 0; color: #6b7d71; }
</style>
