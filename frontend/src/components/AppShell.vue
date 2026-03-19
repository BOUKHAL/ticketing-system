<template>
  <div class="page-wrap">
    <div class="topbar">
      <div>
        <h1 class="page-title">{{ title }}</h1>
        <div v-if="subtitle" class="page-subtitle">{{ subtitle }}</div>
      </div>

      <div class="toolbar-actions">
        <slot name="actions" />
      </div>
    </div>

    <slot />
  </div>
</template>

<script>
export default {
  props: {
    title: String,
    subtitle: String,
  },
}
</script>