<template>
  <div class="header">
    <div class="title-area">
      <slot name="prefix" />
      <div>
        <h2>{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
      </div>
    </div>
    <slot />
  </div>
</template>
<script setup>
defineProps({ title: String, description: String })
</script>
<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; gap: 16px; }
.title-area { display: flex; align-items: center; gap: 12px; min-width: 0; }
h2 { margin: 0; }
p { margin: 6px 0 0; color: #6b7d71; }
</style>
