<template>
  <template v-for="(part, index) in parts" :key="index">
    <mark v-if="part.matched">{{ part.text }}</mark><template v-else>{{ part.text }}</template>
  </template>
</template>
<script setup>
import { computed } from 'vue'
import { highlightParts } from '../utils/highlight'
const props = defineProps({ text: String, keyword: String })
const parts = computed(() => highlightParts(props.text, props.keyword))
</script>
<style scoped>
mark { background: rgba(201,169,110,.3); color: #e8cf9f; padding: 0 2px; }
</style>
