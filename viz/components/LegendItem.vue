<template>
  <div class="flex items-center gap-2">
    <slot name="icon"></slot>
    <span class="whitespace-nowrap">
      <span class="font-medium">{{ label }}:</span>
      <span class="text-gray-600 ml-1">{{ description }}</span>
    </span>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  description: String
})
</script> 